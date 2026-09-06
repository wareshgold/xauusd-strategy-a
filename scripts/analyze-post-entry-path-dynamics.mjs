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
const OUT = resolve(ROOT, 'data/reports/strategy-a-post-entry-path-dynamics');
const PRE = 10000;
const DEV = 6000;
const PATH_HORIZON = 20;

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

function pf(rs) {
  const wins = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? wins / losses : null;
}

function sessionLabel(ts) {
  const d = new Date(ts);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  if (m >= 420 && m < 960) return 'LONDON';
  return 'OTHER';
}

// Spearman with tie handling
function spearman(xs, ys) {
  const pairs = [];
  for (let i = 0; i < xs.length; i++) {
    if (finite(xs[i]) && finite(ys[i])) pairs.push([xs[i], ys[i]]);
  }
  if (pairs.length < 3) return null;
  const n = pairs.length;
  function rank(arr) {
    const indexed = arr.map((v, i) => ({ v, i }));
    indexed.sort((a, b) => a.v - b.v);
    const ranks = new Array(n);
    let i = 0;
    while (i < n) {
      let j = i;
      while (j < n - 1 && indexed[j + 1].v === indexed[j].v) j++;
      const avgRank = (i + j) / 2 + 1;
      for (let k = i; k <= j; k++) ranks[indexed[k].i] = avgRank;
      i = j + 1;
    }
    return ranks;
  }
  const rx = rank(pairs.map(p => p[0]));
  const ry = rank(pairs.map(p => p[1]));
  const mx = mean(rx), my = mean(ry);
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const a = rx[i] - mx, b = ry[i] - my;
    num += a * b;
    dx += a * a;
    dy += b * b;
  }
  const denom = Math.sqrt(dx * dy);
  return denom > 0 ? num / denom : null;
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
    return {
      entryIndex: index,
      direction: tr.direction,
      entry: tr.entryPrice,
      stopLoss: inv.invalidationLevel,
      tp1: pr.tp1,
      risk,
      entryTime: tr.timestamp,
    };
  }
  return null;
}

function computePath(candles, c) {
  const maxBar = Math.min(c.entryIndex + PATH_HORIZON, candles.length - 1);
  const features = {
    t1Mae: null,
    t3Mae: null,
    t5Mae: null,
    t10Mae: null,
    mae20: 0,
    mfe20: 0,
    barsToMAE: null,
    barsToMFE: null,
    maeBeforeMfe: null,
    firstEvent: null,
    sameBarSL: false,
    barsToOutcome: null,
    pathLength: 0,
  };

  // Same-bar SL check on bar entryIndex+1
  const t1 = candles[c.entryIndex + 1];
  if (!t1) return null;
  features.sameBarSL = c.direction === 'BUY' ? t1.low <= c.stopLoss : t1.high >= c.stopLoss;

  let maeBar = null;
  let mfeBar = null;
  let maeTime = null;
  let mfeTime = null;

  for (let j = c.entryIndex + 1; j <= maxBar; j++) {
    const x = candles[j];
    const barNum = j - c.entryIndex;
    const adv = (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk;
    const fav = (c.direction === 'BUY' ? x.high - c.entry : c.entry - x.low) / c.risk;
    const advR = Math.max(0, adv);
    const favR = Math.max(0, fav);

    // Early-path MAE at fixed horizons (actionable)
    if (barNum === 1) features.t1Mae = advR;
    if (barNum <= 3 && (features.t3Mae === null || advR > features.t3Mae)) features.t3Mae = advR;
    if (barNum <= 5 && (features.t5Mae === null || advR > features.t5Mae)) features.t5Mae = advR;
    if (barNum <= 10 && (features.t10Mae === null || advR > features.t10Mae)) features.t10Mae = advR;

    // Full-path MAE/MFE (retrospective)
    if (advR > features.mae20) {
      features.mae20 = advR;
      maeBar = barNum;
    }
    if (favR > features.mfe20) {
      features.mfe20 = favR;
      mfeBar = barNum;
    }

    features.pathLength = barNum;
  }

  features.barsToMAE = maeBar;
  features.barsToMFE = mfeBar;

  // Sequence
  if (maeBar !== null && mfeBar !== null) {
    if (maeBar === mfeBar) {
      features.firstEvent = 'SAME_BAR';
      features.maeBeforeMfe = null;
    } else if (maeBar < mfeBar) {
      features.firstEvent = 'MAE';
      features.maeBeforeMfe = true;
    } else {
      features.firstEvent = 'MFE';
      features.maeBeforeMfe = false;
    }
  } else if (maeBar === null && mfeBar === null) {
    features.firstEvent = 'NONE';
    features.maeBeforeMfe = null;
  } else if (maeBar === null) {
    features.firstEvent = 'MFE_ONLY';
    features.maeBeforeMfe = false;
  } else {
    features.firstEvent = 'MAE_ONLY';
    features.maeBeforeMfe = true;
  }

  return features;
}

function overallStats(rows) {
  const rs = rows.map(r => r.rMultiple).filter(finite);
  const wins = rs.filter(x => x > 0);
  const losses = rs.filter(x => x < 0);
  return {
    n: rows.length,
    avgR: mean(rs),
    medianR: median(rs),
    WR: pct(wins.length, rs.length),
    PF: pf(rs),
    totalR: rs.reduce((a, b) => a + b, 0),
    exceptional: rows.filter(r => r.rMultiple >= 5).length,
  };
}

function featureDiag(rows, feat) {
  const win = rows.filter(r => r.rMultiple > 0 && r.rMultiple < 5).map(r => r[feat]);
  const loss = rows.filter(r => r.rMultiple < 0).map(r => r[feat]);
  const allR = rows.map(r => r.rMultiple);
  const allF = rows.map(r => r[feat]);
  const noExRows = rows.filter(r => r.rMultiple < 5);
  const noExR = noExRows.map(r => r.rMultiple);
  const noExF = noExRows.map(r => r[feat]);
  return {
    n: rows.length,
    medianWin: median(win),
    medianLoss: median(loss),
    delta: (median(win) ?? 0) - (median(loss) ?? 0),
    spearmanAll: spearman(allF, allR),
    spearmanNoEx: spearman(noExF, noExR),
  };
}

function featureDiagSplit(rows, feat) {
  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV);
  return {
    overall: featureDiag(rows, feat),
    dev: featureDiag(dev, feat),
    val: featureDiag(val, feat),
  };
}

function sameBarSLStats(rows) {
  const sl = rows.filter(r => r.sameBarSL);
  const noSl = rows.filter(r => !r.sameBarSL);
  return {
    sameBarSL: overallStats(sl),
    postEntry: overallStats(noSl),
  };
}

async function run() {
  const raw = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE) throw new Error(`Expected >= ${PRE} candles, found ${candles.length}`);

  const base = JSON.parse(await readFile(resolve(BASE, '5min.json'), 'utf8'));
  const trades = (base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)));

  const canonicalMap = new Map(trades.map(t => [
    `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`,
    t,
  ]));

  const rows = [];
  let replayOK = 0, replayFail = 0, noPath = 0;
  for (let i = 0; i < PRE; i++) {
    const c = candidate(candles, i);
    if (!c) continue;
    const key = `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
    const t = canonicalMap.get(key);
    if (!t) { replayFail++; continue; }
    replayOK++;
    const p = computePath(candles, c);
    if (!p) { noPath++; continue; }
    rows.push({
      entryIndex: c.entryIndex,
      entryTime: c.entryTime,
      direction: c.direction,
      session: sessionLabel(c.entryTime),
      rMultiple: Number(t.rMultiple),
      result: t.result ?? null,
      ...p,
    });
  }

  // Integrity gate
  // The baseline has 210 pre-holdout resolved trades total.
  // Of those, only DELAY1 trades (entryIndex - correctionExtremeIndex === 1) are reconstructable.
  // Existing delay1 analyzers confirm 144 for 5min.
  const baselinePreHoldout = trades.filter(t => Number(t.entryIndex) < PRE).length;
  const devRows = rows.filter(r => r.entryIndex < DEV);
  const valRows = rows.filter(r => r.entryIndex >= DEV);
  const sellNY = rows.filter(r => r.direction === 'SELL' && r.session === 'NEW_YORK');
  const sellLON = rows.filter(r => r.direction === 'SELL' && r.session === 'LONDON');
  const buyNY = rows.filter(r => r.direction === 'BUY' && r.session === 'NEW_YORK');
  const buyLON = rows.filter(r => r.direction === 'BUY' && r.session === 'LONDON');

  const earlyFeats = ['t1Mae', 't3Mae', 't5Mae', 't10Mae'];
  const retroFeats = ['mae20', 'mfe20', 'barsToMAE', 'barsToMFE'];

  const report = {
    strategy: 'Strategy A',
    mode: 'POST_ENTRY_PATH_DYNAMICS',
    timeframe: '5min',
    scope: {
      preHoldoutCandles: PRE,
      devCandles: DEV,
      valCandles: PRE - DEV,
      pathHorizon: PATH_HORIZON,
      freshHoldoutExcluded: true,
      delayExactly: 1,
    },
    methodology: {
      purpose: 'Descriptive analysis of post-entry path dynamics. Primary: early-path MAE at fixed horizons (t1/t3/t5/t10). Secondary (retrospective): MAE20/MFE20, timing, sequence.',
      earlyPathFeatures: 'MAE at fixed bar horizons. Available after each horizon closes. Potential live exit signals.',
      retrospectiveFeatures: 'Full 20-bar MAE/MFE, barsToMAE/MFE, sequence. Only known after trade resolves. Descriptive only.',
      sameBarSLSeparation: 'Trades where SL is hit on bar 1 are separated from post-entry path analysis.',
      noThresholdOptimization: true,
      noExitRuleCreation: true,
      diagnosticOnly: true,
      productionUntouched: true,
      freshHoldoutExcluded: true,
    },
    integrity: {
      baselineResolvedPreHoldout: baselinePreHoldout,
      delay1Reconstructed: replayOK,
      nonDelay1Baseline: baselinePreHoldout - replayOK,
      unmatchedCandidates: replayFail,
      noPath: noPath,
      totalRows: rows.length,
      devN: devRows.length,
      valN: valRows.length,
      replayConsistent: replayOK === 144,
      note: 'DELAY1 trades only. Of 210 pre-holdout resolved, 144 are DELAY1 (confirmed by existing analyzers). Unmatched candidates are extra reconstructions not in baseline.',
    },
    outcome: {
      all: overallStats(rows),
      dev: overallStats(devRows),
      val: overallStats(valRows),
    },
    cells: {
      sellNY: overallStats(sellNY),
      sellLONDON: overallStats(sellLON),
      buyNY: overallStats(buyNY),
      buyLONDON: overallStats(buyLON),
    },
    sameBarSL: sameBarSLStats(rows),
    earlyPath: {},
    retrospective: {},
    classifications: {},
  };

  // Early-path diagnostics
  for (const f of earlyFeats) {
    report.earlyPath[f] = featureDiagSplit(rows, f);
  }

  // Retrospective diagnostics
  for (const f of retroFeats) {
    report.retrospective[f] = featureDiagSplit(rows, f);
  }

  // Sequence distribution
  const seqAll = {};
  for (const r of rows) { seqAll[r.firstEvent] = (seqAll[r.firstEvent] || 0) + 1; }
  const seqDev = {};
  for (const r of devRows) { seqDev[r.firstEvent] = (seqDev[r.firstEvent] || 0) + 1; }
  const seqVal = {};
  for (const r of valRows) { seqVal[r.firstEvent] = (seqVal[r.firstEvent] || 0) + 1; }
  report.sequence = { all: seqAll, dev: seqDev, val: seqVal };

  // maeBeforeMfe distribution
  const mbfAll = rows.filter(r => r.maeBeforeMfe !== null);
  report.maeBeforeMfe = {
    all: { yes: mbfAll.filter(r => r.maeBeforeMfe).length, no: mbfAll.filter(r => !r.maeBeforeMfe).length, total: mbfAll.length },
  };

  // Classification
  for (const f of earlyFeats) {
    const d = report.earlyPath[f];
    const devSp = d.dev.spearmanNoEx;
    const valSp = d.val.spearmanNoEx;
    const devN = d.dev.n ?? 0;
    const valN = d.val.n ?? 0;
    if (devN < 10 || valN < 10) {
      report.classifications[f] = 'INSUFFICIENT_SAMPLE';
    } else if (devSp === null || valSp === null) {
      report.classifications[f] = 'INSUFFICIENT_SAMPLE';
    } else if ((devSp > 0) === (valSp > 0) && Math.abs(devSp) > 0.05 && Math.abs(valSp) > 0.05) {
      report.classifications[f] = 'STABLE_POST_ENTRY_ASSOCIATION';
    } else if ((devSp > 0) === (valSp > 0)) {
      report.classifications[f] = 'WEAK_POST_ENTRY_ASSOCIATION';
    } else {
      report.classifications[f] = 'UNSTABLE_DEV_VAL';
    }
  }

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(report, null, 2));

  // Compact stdout
  console.log(`POST_ENTRY_PATH_DYNAMICS N=${rows.length} DEV=${devRows.length} VAL=${valRows.length} FRESH=LOCKED`);
  console.log(`INTEGRITY delay1=${replayOK}/144 unmatched=${replayFail} noPath=${noPath} consistent=${report.integrity.replayConsistent}`);
  console.log(`CELLS sellNY=${sellNY.length} sellLON=${sellLON.length} buyNY=${buyNY.length} buyLON=${buyLON.length}`);
  console.log(`ALL avgR=${fmt(report.outcome.all.avgR)} PF=${fmt(report.outcome.all.PF)} WR=${fmtPct(report.outcome.all.WR)} ex=${report.outcome.all.exceptional}`);
  console.log(`DEV avgR=${fmt(report.outcome.dev.avgR)} PF=${fmt(report.outcome.dev.PF)} WR=${fmtPct(report.outcome.dev.WR)}`);
  console.log(`VAL avgR=${fmt(report.outcome.val.avgR)} PF=${fmt(report.outcome.val.PF)} WR=${fmtPct(report.outcome.val.WR)}`);
  console.log(`SAME_BAR_SL n=${report.sameBarSL.sameBarSL.n} avgR=${fmt(report.sameBarSL.sameBarSL.avgR)} | POST_ENTRY n=${report.sameBarSL.postEntry.n} avgR=${fmt(report.sameBarSL.postEntry.avgR)}`);
  console.log(`SEQUENCE all=${JSON.stringify(report.sequence.all)} dev=${JSON.stringify(report.sequence.dev)} val=${JSON.stringify(report.sequence.val)}`);
  console.log('');
  console.log('=== EARLY PATH (ACTIONABLE) ===');
  for (const f of earlyFeats) {
    const d = report.earlyPath[f];
    const c = report.classifications[f];
    console.log(`${f}: devSp=${fmt(d.dev.spearmanNoEx)} valSp=${fmt(d.val.spearmanNoEx)} devN=${d.dev.n ?? 0} valN=${d.val.n ?? 0} | ${c}`);
  }
  console.log('');
  console.log('=== RETROSPECTIVE (DESCRIPTIVE ONLY) ===');
  for (const f of retroFeats) {
    const d = report.retrospective[f];
    console.log(`${f}: allSp=${fmt(d.overall.spearmanAll)} noExSp=${fmt(d.overall.spearmanNoEx)} devSp=${fmt(d.dev.spearmanNoEx)} valSp=${fmt(d.val.spearmanNoEx)}`);
  }
  console.log('');
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
}

function fmt(v) { return finite(v) ? v.toFixed(4) : 'NA'; }
function fmtPct(v) { return finite(v) ? (v * 100).toFixed(1) + '%' : 'NA'; }

await run();
