import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-early-mae-decision-value');
const PRE = 10000;
const DEV = 6000;
const PATH_HORIZON = 10;
const FIXED_BANDS = [0.25, 0.5, 0.75, 1.0];

const CTX = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 960, endMinutes: 1320 },
  ],
  avoidWindows: [],
};

const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { const v = [...a].filter(finite).sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };
const pct = (n, d) => d ? n / d : null;

function profitFactor(rs) {
  const wins = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? wins / losses : null;
}

function spearman(xs, ys) {
  const pairs = [];
  for (let i = 0; i < xs.length; i++) if (finite(xs[i]) && finite(ys[i])) pairs.push([xs[i], ys[i]]);
  if (pairs.length < 3) return null;
  const rank = arr => {
    const indexed = arr.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
    const ranks = new Array(arr.length);
    let i = 0;
    while (i < indexed.length) {
      let j = i;
      while (j + 1 < indexed.length && indexed[j + 1].v === indexed[i].v) j++;
      const r = (i + j) / 2 + 1;
      for (let k = i; k <= j; k++) ranks[indexed[k].i] = r;
      i = j + 1;
    }
    return ranks;
  };
  const rx = rank(pairs.map(p => p[0]));
  const ry = rank(pairs.map(p => p[1]));
  const mx = mean(rx), my = mean(ry);
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < rx.length; i++) {
    const a = rx[i] - mx, b = ry[i] - my;
    num += a * b; dx += a * a; dy += b * b;
  }
  const denom = Math.sqrt(dx * dy);
  return denom > 0 ? num / denom : null;
}

function key(t) {
  return `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
}

function candidate(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < 60) return null;
  const bo = detectBreakout(v, 5);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const cor = detectFirstCorrection(v, spike);
    if (!cor || cor.correctionExtremeIndex >= index || index - cor.correctionExtremeIndex !== 1) continue;
    const tr = detectEntryTrigger(v, cor);
    if (!tr || tr.index !== index) continue;
    const pr = projectLeg2(v, cor);
    if (!pr) continue;
    const inv = getInvalidationRule(cor);
    const ema = buildEMAContext(v.map(c => c.close), CTX);
    if (!ema) continue;
    const loc = buildLocationContext(tr.entryPrice, CTX);
    const ses = buildSessionContext(tr.timestamp, CTX);
    if (!scoreSetup(spike, { ema, location: loc, session: ses }).tradeAllowed) continue;
    const risk = Math.abs(tr.entryPrice - inv.invalidationLevel);
    if (!(risk > 0)) continue;
    if (!(tr.direction === 'BUY' ? pr.tp1 > tr.entryPrice : pr.tp1 < tr.entryPrice)) continue;
    return { entryIndex: index, direction: tr.direction, entry: tr.entryPrice, stopLoss: inv.invalidationLevel, tp1: pr.tp1, risk, entryTime: tr.timestamp };
  }
  return null;
}

function pathAt(candles, c, horizon) {
  const end = Math.min(c.entryIndex + horizon, candles.length - 1);
  if (c.entryIndex + 1 > end) return null;
  let mae = 0;
  for (let j = c.entryIndex + 1; j <= end; j++) {
    const x = candles[j];
    const adverse = (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk;
    mae = Math.max(mae, Math.max(0, adverse));
  }
  return { mae, pathLength: end - c.entryIndex, complete: end >= c.entryIndex + horizon };
}

function stats(rows) {
  const rs = rows.map(r => r.rMultiple).filter(finite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  return {
    n: rows.length,
    avgR: mean(rs),
    medianR: median(rs),
    WR: pct(wins.length, rs.length),
    PF: profitFactor(rs),
    totalR: rs.reduce((a, b) => a + b, 0),
    exceptional: rs.filter(x => x >= 5).length,
  };
}

function maeDiagnostics(rows, feat) {
  const valid = rows.filter(r => finite(r[feat]));
  const noEx = valid.filter(r => r.rMultiple < 5);
  return {
    n: valid.length,
    medianAll: median(valid.map(r => r[feat])),
    medianWin: median(valid.filter(r => r.rMultiple > 0 && r.rMultiple < 5).map(r => r[feat])),
    medianLoss: median(valid.filter(r => r.rMultiple < 0).map(r => r[feat])),
    spearmanAll: spearman(valid.map(r => r[feat]), valid.map(r => r.rMultiple)),
    spearmanNoEx: spearman(noEx.map(r => r[feat]), noEx.map(r => r.rMultiple)),
    positiveCount: valid.filter(r => r.rMultiple > 0).length,
    negativeCount: valid.filter(r => r.rMultiple < 0).length,
  };
}

function bandStats(rows, feature) {
  const ordered = [
    { label: '0-.25R', min: 0, max: 0.25 },
    { label: '.25-.50R', min: 0.25, max: 0.5 },
    { label: '.50-.75R', min: 0.5, max: 0.75 },
    { label: '.75-1.00R', min: 0.75, max: 1.0 },
    { label: '>1.00R', min: 1.0, max: Infinity },
  ];
  return ordered.map(b => {
    const subset = rows.filter(r => finite(r[feature]) && r[feature] >= b.min && r[feature] < b.max);
    const s = stats(subset);
    return { ...b, ...s, winners: subset.filter(r => r.rMultiple > 0).length, losers: subset.filter(r => r.rMultiple < 0).length };
  });
}

async function load() {
  const raw = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE) throw new Error(`5min: expected at least ${PRE} candles, found ${candles.length}`);
  const baseline = JSON.parse(await readFile(resolve(BASE, '5min.json'), 'utf8')).trades ?? [];
  const usable = baseline.filter(t => t.result !== 'AMBIGUOUS' && finite(Number(t.rMultiple)) && Number(t.entryIndex) < PRE);
  const keyCounts = new Map();
  for (const t of usable) keyCounts.set(key(t), (keyCounts.get(key(t)) ?? 0) + 1);
  const duplicateKeys = [...keyCounts.entries()].filter(([, n]) => n > 1).map(([k, n]) => ({ key: k, count: n }));
  if (duplicateKeys.length) throw new Error(`Baseline canonical-key duplicates: ${duplicateKeys.length}`);
  const byKey = new Map(usable.map(t => [key(t), t]));
  const rows = [];
  let candidates = 0, matched = 0;
  for (let i = 0; i < PRE; i++) {
    const c = candidate(candles, i);
    if (!c) continue;
    candidates++;
    const t = byKey.get(key(c));
    if (!t) continue;
    matched++;
    const p1 = pathAt(candles, c, 1);
    const p3 = pathAt(candles, c, 3);
    const p5 = pathAt(candles, c, 5);
    const p10 = pathAt(candles, c, 10);
    if (!p1 || !p3 || !p5 || !p10) continue;
    rows.push({
      entryIndex: Number(t.entryIndex),
      direction: t.direction,
      entryTime: t.entryTime ?? t.timestamp,
      rMultiple: Number(t.rMultiple),
      sameBarSL: c.direction === 'BUY' ? candles[i + 1].low <= c.stopLoss : candles[i + 1].high >= c.stopLoss,
      t1Mae: p1.mae,
      t3Mae: p3.mae,
      t5Mae: p5.mae,
      t10Mae: p10.mae,
      pathComplete10: p10.complete,
    });
  }
  const baselineDelay1 = usable.filter(t => Number(t.entryIndex) >= 0);
  const matchedKeys = new Set(rows.map(r => `${r.entryIndex}|${r.direction}`));
  return { candles, rows, candidates, matched, baselineDelay1: baselineDelay1.length, duplicateKeys };
}

function decisionMatrix(rows, feature) {
  const all = bandStats(rows, feature);
  const post = bandStats(rows.filter(r => !r.sameBarSL), feature);
  return { all, postEntryOnly: post };
}

function fmt(v) { return finite(v) ? v.toFixed(4) : 'NA'; }
function compact(s) { return `N=${s.n} avgR=${fmt(s.avgR)} PF=${fmt(s.PF)} WR=${fmt((s.WR ?? 0) * 100)}%`; }

async function run() {
  const loaded = await load();
  const rows = loaded.rows;
  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const post = rows.filter(r => !r.sameBarSL);
  const postDev = post.filter(r => r.entryIndex < DEV);
  const postVal = post.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_MAE_DECISION_VALUE',
    timeframe: '5min',
    scope: { preHoldoutCandles: PRE, devCutoff: DEV, freshHoldoutAccessed: false, freshHoldoutLocked: true },
    integrity: {
      baselineUsablePreHoldout: loaded.baselineDelay1,
      reconstructedCandidates: loaded.candidates,
      matchedCandidates: loaded.matched,
      rows: rows.length,
      devN: dev.length,
      valN: val.length,
      sameBarSL: rows.filter(r => r.sameBarSL).length,
      postEntryN: post.length,
      duplicateCanonicalKeys: loaded.duplicateKeys.length,
      allPath10Complete: rows.filter(r => r.pathComplete10).length,
      deterministicInputs: 'same canonical detector chain and baseline join key as Phase 10',
    },
    methodology: {
      populationA: 'All matched DELAY1 baseline trades',
      populationB: 'Only trades surviving the first post-entry bar without same-bar stop-loss hit',
      horizons: ['t1Mae', 't3Mae', 't5Mae', 't10Mae'],
      outcome: 'Canonical baseline rMultiple; no outcome recomputation',
      fixedBands: FIXED_BANDS,
      bandPurpose: 'Pre-existing descriptive MAE states only; no threshold selection or optimization',
      conditioningPurpose: 'Test whether MAE association survives removal of mechanical same-bar SL outcomes',
      noOptimization: true,
      noRuleCreation: true,
      diagnosticOnly: true,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    overall: {
      all: stats(rows),
      sameBarSL: stats(rows.filter(r => r.sameBarSL)),
      postEntry: stats(post),
      dev: stats(dev),
      val: stats(val),
      postEntryDev: stats(postDev),
      postEntryVal: stats(postVal),
    },
    earlyPath: {},
    decisionMatrix: {},
  };

  for (const feature of ['t1Mae', 't3Mae', 't5Mae', 't10Mae']) {
    report.earlyPath[feature] = {
      all: maeDiagnostics(rows, feature),
      dev: maeDiagnostics(dev, feature),
      val: maeDiagnostics(val, feature),
      postEntryOnly: maeDiagnostics(post, feature),
      postEntryDev: maeDiagnostics(postDev, feature),
      postEntryVal: maeDiagnostics(postVal, feature),
    };
    report.decisionMatrix[feature] = decisionMatrix(rows, feature);
  }

  console.log(`PHASE_10A_EARLY_MAE N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${loaded.baselineDelay1} candidates=${loaded.candidates} matched=${loaded.matched} duplicateKeys=${loaded.duplicateKeys.length} path10Complete=${rows.filter(r => r.pathComplete10).length}`);
  console.log(`POPULATION all=${rows.length} sameBarSL=${rows.filter(r => r.sameBarSL).length} postEntry=${post.length}`);
  console.log(`ALL ${compact(stats(rows))} | POST_ENTRY ${compact(stats(post))}`);
  console.log('=== EARLY MAE ASSOCIATION ===');
  for (const f of ['t1Mae', 't3Mae', 't5Mae', 't10Mae']) {
    const x = report.earlyPath[f];
    console.log(`${f}: ALL devSp=${fmt(x.dev.spearmanAll)} valSp=${fmt(x.val.spearmanAll)} | POST_ENTRY devSp=${fmt(x.postEntryDev.spearmanAll)} valSp=${fmt(x.postEntryVal.spearmanAll)}`);
  }
  console.log('=== FIXED DESCRIPTIVE BANDS; NO THRESHOLD SELECTION ===');
  for (const f of ['t1Mae', 't3Mae', 't5Mae', 't10Mae']) {
    console.log(`${f}: ALL ${JSON.stringify(report.decisionMatrix[f].all.map(x => ({ band: x.label, n: x.n, WR: x.WR, avgR: x.avgR, winners: x.winners, losers: x.losers })))}`);
    console.log(`${f}: POST_ENTRY ${JSON.stringify(report.decisionMatrix[f].postEntryOnly.map(x => ({ band: x.label, n: x.n, WR: x.WR, avgR: x.avgR, winners: x.winners, losers: x.losers })))}`);
  }
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(report, null, 2));
}

await run();
