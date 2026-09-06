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
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-early-mae-recovery-transition');
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [3, 5, 10];
const PATH_END = 20;
const STATES = ['<0.25R', '0.25-0.50R', '0.50-0.75R', '0.75-1.00R', '>=1.00R'];

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
const pct = (n, d) => d ? n / d : null;

function profitFactor(rs) {
  const wins = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? wins / losses : null;
}

function stats(rows) {
  const rs = rows.map(r => r.rMultiple).filter(finite);
  const wins = rs.filter(x => x > 0);
  return {
    n: rs.length,
    avgR: mean(rs),
    PF: profitFactor(rs),
    WR: pct(wins.length, rs.length),
    totalR: rs.reduce((a, b) => a + b, 0),
    exceptional: rs.filter(x => x >= 5).length,
  };
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

function pathAt(candles, c, startOffset, endOffset) {
  const start = c.entryIndex + startOffset;
  const end = Math.min(c.entryIndex + endOffset, candles.length - 1);
  if (start > end) return null;
  let mae = 0;
  let mfe = 0;
  for (let j = start; j <= end; j++) {
    const x = candles[j];
    const adverse = (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk;
    const favorable = (c.direction === 'BUY' ? x.high - c.entry : c.entry - x.low) / c.risk;
    if (finite(adverse)) mae = Math.max(mae, Math.max(0, adverse));
    if (finite(favorable)) mfe = Math.max(mfe, Math.max(0, favorable));
  }
  return { mae, mfe, pathLength: end - start + 1, complete: end >= c.entryIndex + endOffset };
}

function maeState(mae) {
  if (!finite(mae)) return null;
  if (mae < 0.25) return '<0.25R';
  if (mae < 0.5) return '0.25-0.50R';
  if (mae < 0.75) return '0.50-0.75R';
  if (mae < 1.0) return '0.75-1.00R';
  return '>=1.00R';
}

async function load() {
  const raw = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE) throw new Error(`5min: expected at least ${PRE} candles, found ${candles.length}`);

  const baseline = JSON.parse(await readFile(resolve(BASE, '5min.json'), 'utf8')).trades ?? [];
  const usableBaseline = baseline.filter(t => t.result !== 'AMBIGUOUS' && finite(Number(t.rMultiple)) && Number(t.entryIndex) < PRE);
  const keyCounts = new Map();
  for (const t of usableBaseline) keyCounts.set(key(t), (keyCounts.get(key(t)) ?? 0) + 1);
  const duplicateKeys = [...keyCounts.entries()].filter(([, n]) => n > 1).map(([k, n]) => ({ key: k, count: n }));
  if (duplicateKeys.length) throw new Error(`Baseline canonical-key duplicates: ${duplicateKeys.length}`);
  const byKey = new Map(usableBaseline.map(t => [key(t), t]));

  const rows = [];
  let candidates = 0;
  let matched = 0;
  for (let i = 0; i < PRE; i++) {
    const c = candidate(candles, i);
    if (!c) continue;
    candidates++;
    const t = byKey.get(key(c));
    if (!t) continue;
    matched++;
    const p1 = pathAt(candles, c, 1, 1);
    const p3 = pathAt(candles, c, 1, 3);
    const p5 = pathAt(candles, c, 1, 5);
    const p10 = pathAt(candles, c, 1, 10);
    const later3 = pathAt(candles, c, 4, PATH_END);
    const later5 = pathAt(candles, c, 6, PATH_END);
    const later10 = pathAt(candles, c, 11, PATH_END);
    if (!p1 || !p3 || !p5 || !p10 || !later3 || !later5 || !later10) continue;
    if (!p10.complete || !later3.complete || !later5.complete || !later10.complete) continue;
    rows.push({
      entryIndex: Number(t.entryIndex),
      direction: t.direction,
      entryTime: t.entryTime ?? t.timestamp,
      entry: Number(t.entry),
      stopLoss: Number(t.stopLoss),
      tp1: Number(t.tp1),
      rMultiple: Number(t.rMultiple),
      sameBarSL: c.direction === 'BUY' ? candles[i + 1].low <= c.stopLoss : candles[i + 1].high >= c.stopLoss,
      t3Mae: p3.mae,
      t5Mae: p5.mae,
      t10Mae: p10.mae,
      t3LaterMfe: later3.mfe,
      t5LaterMfe: later5.mfe,
      t10LaterMfe: later10.mfe,
    });
  }

  return { candles, rows, candidates, matched, baselinePre: usableBaseline.length, duplicateKeys };
}

function transition(rows, fromH, toH) {
  const result = {};
  for (const from of STATES) {
    const fromRows = rows.filter(r => maeState(r[`t${fromH}Mae`]) === from);
    const counts = Object.fromEntries(STATES.map(s => [s, 0]));
    for (const r of fromRows) counts[maeState(r[`t${toH}Mae`])]++;
    result[from] = {
      n: fromRows.length,
      to: Object.fromEntries(STATES.map(s => [s, pct(counts[s], fromRows.length)])),
    };
  }
  return result;
}

function stateTable(rows, h) {
  return Object.fromEntries(STATES.map(s => {
    const subset = rows.filter(r => maeState(r[`t${h}Mae`]) === s);
    const o = stats(subset);
    const laterMfe = subset.map(r => r[`t${h}LaterMfe`]).filter(finite);
    const mfe1 = laterMfe.filter(x => x >= 1).length;
    const mfe2 = laterMfe.filter(x => x >= 2).length;
    return [s, {
      n: subset.length,
      outcome: o,
      laterPathMfe: {
        ge1R: pct(mfe1, laterMfe.length),
        ge2R: pct(mfe2, laterMfe.length),
        n: laterMfe.length,
      },
    }];
  }));
}

function adverseRecovery(rows, h) {
  const subset = rows.filter(r => r[`t${h}Mae`] >= 1);
  const later = subset.map(r => r[`t${h}LaterMfe`]).filter(finite);
  return {
    n: subset.length,
    laterMfeGE1R: later.filter(x => x >= 1).length,
    laterMfeGE2R: later.filter(x => x >= 2).length,
    laterMfeGE1RPct: pct(later.filter(x => x >= 1).length, later.length),
    laterMfeGE2RPct: pct(later.filter(x => x >= 2).length, later.length),
  };
}

async function run() {
  const loaded = await load();
  const rows = loaded.rows;
  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const post = rows.filter(r => !r.sameBarSL);
  const postDev = post.filter(r => r.entryIndex < DEV);
  const postVal = post.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);

  if (rows.length !== 144 || dev.length !== 91 || val.length !== 53) {
    throw new Error(`Integrity gate failed: rows=${rows.length} dev=${dev.length} val=${val.length}`);
  }

  const makeHorizon = h => ({
    all: stateTable(rows, h),
    dev: stateTable(dev, h),
    val: stateTable(val, h),
    postEntry: stateTable(post, h),
    postEntryDev: stateTable(postDev, h),
    postEntryVal: stateTable(postVal, h),
    transitionsToLater: Object.fromEntries(HORIZONS.filter(x => x > h).map(toH => [`T${toH}`, {
      all: transition(rows, h, toH),
      dev: transition(dev, h, toH),
      val: transition(val, h, toH),
    }])),
    adverseGE1RRecovery: {
      all: adverseRecovery(rows, h),
      dev: adverseRecovery(dev, h),
      val: adverseRecovery(val, h),
      postEntry: adverseRecovery(post, h),
      postEntryDev: adverseRecovery(postDev, h),
      postEntryVal: adverseRecovery(postVal, h),
    },
  });

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_MAE_RECOVERY_TRANSITION',
    timeframe: '5min',
    scope: {
      preHoldoutCandles: PRE,
      devCutoff: DEV,
      freshHoldoutAccessed: false,
      freshHoldoutLocked: true,
      horizons: HORIZONS,
      laterRecoveryEnd: PATH_END,
      fixedStates: STATES,
    },
    integrity: {
      baselinePre: loaded.baselinePre,
      candidates: loaded.candidates,
      matched: loaded.matched,
      rows: rows.length,
      devN: dev.length,
      valN: val.length,
      duplicateKeys: loaded.duplicateKeys.length,
      path10Complete: rows.length,
      deterministic: true,
    },
    methodology: {
      purpose: 'Descriptive early-MAE recovery/failure state transition study.',
      outcome: 'Canonical baseline rMultiple; no outcome recomputation.',
      stateDefinition: 'Fixed existing MAE bands; no threshold selection.',
      earlyStateHorizon: 'MAE measured from entry+1 through T3/T5/T10.',
      laterRecoveryWindow: 'MFE measured strictly after the state horizon: T3 uses bars 4-20, T5 uses bars 6-20, T10 uses bars 11-20.',
      transitions: 'MAE state at an earlier fixed horizon mapped to MAE state at a later fixed horizon.',
      sameBarSLAnalysis: 'Reported separately because the first post-entry bar can contain ambiguous intrabar ordering under OHLC data.',
      devValReplication: 'All, DEV, VAL, and post-entry populations reported separately; no new segmentation.',
      noThresholdOptimization: true,
      noExitRuleCreation: true,
      noBrokerExecutionModel: true,
      diagnosticOnly: true,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    baseline: {
      all: stats(rows),
      dev: stats(dev),
      val: stats(val),
      sameBarSL: stats(rows.filter(r => r.sameBarSL)),
      postEntry: stats(post),
      postEntryDev: stats(postDev),
      postEntryVal: stats(postVal),
    },
    horizons: Object.fromEntries(HORIZONS.map(h => [`T${h}`, makeHorizon(h)])),
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(report, null, 2));

  console.log(`PHASE_10C_EARLY_MAE_RECOVERY N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${loaded.baselinePre} candidates=${loaded.candidates} matched=${loaded.matched} duplicateKeys=${loaded.duplicateKeys.length} complete=${rows.length === 144}`);
  console.log(`BASELINE ALL avgR=${report.baseline.all.avgR.toFixed(4)} PF=${report.baseline.all.PF.toFixed(4)} WR=${(report.baseline.all.WR * 100).toFixed(2)}% | POST_ENTRY avgR=${report.baseline.postEntry.avgR.toFixed(4)} PF=${report.baseline.postEntry.PF.toFixed(4)} WR=${(report.baseline.postEntry.WR * 100).toFixed(2)}%`);

  for (const h of HORIZONS) {
    console.log(`\nT${h} STATE RECOVERY — LATER BARS ${h + 1}-20`);
    for (const s of STATES) {
      const x = report.horizons[`T${h}`].all[s];
      const o = x.outcome;
      const r = x.laterPathMfe;
      console.log(`${s} N=${o.n} WR=${o.WR == null ? 'NA' : (o.WR * 100).toFixed(2) + '%'} avgR=${o.avgR == null ? 'NA' : o.avgR.toFixed(4)} PF=${o.PF == null ? 'NA' : o.PF.toFixed(4)} | LATER_MFE>=1R=${r.ge1R == null ? 'NA' : (r.ge1R * 100).toFixed(2) + '%'} >=2R=${r.ge2R == null ? 'NA' : (r.ge2R * 100).toFixed(2) + '%'}`);
    }
  }

  console.log('\n=== ADVERSE >=1R RECOVERY — STRICTLY LATER PATH ===');
  for (const h of HORIZONS) {
    const a = report.horizons[`T${h}`].adverseGE1RRecovery;
    console.log(`T${h}: ALL N=${a.all.n} -> >=1R ${a.all.laterMfeGE1RPct == null ? 'NA' : (a.all.laterMfeGE1RPct * 100).toFixed(2) + '%'} | >=2R ${a.all.laterMfeGE2RPct == null ? 'NA' : (a.all.laterMfeGE2RPct * 100).toFixed(2) + '%'} | DEV >=1R ${a.dev.laterMfeGE1RPct == null ? 'NA' : (a.dev.laterMfeGE1RPct * 100).toFixed(2) + '%'} | VAL >=1R ${a.val.laterMfeGE1RPct == null ? 'NA' : (a.val.laterMfeGE1RPct * 100).toFixed(2) + '%'}`);
  }

  console.log('\nSTATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

await run();
