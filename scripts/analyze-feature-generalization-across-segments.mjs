import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

// ── Constants ──────────────────────────────────────────────────────────────
const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-feature-generalization-across-segments');
const DEV_CUTOFF = 6000;
const PRE_HOLDOUT = 10000;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
const utcMinutes = (ts) => { const d = new Date(ts); return d.getUTCHours() * 60 + d.getUTCMinutes(); };
const isNySell = (ts) => { const m = utcMinutes(ts); return m >= 960 && m < 1320; };
const isNyBuy = (ts) => { const m = utcMinutes(ts); return m >= 960 && m < 1320; };
const FEATURES = ['correctionBars', 'correctionToSpike', 'pathEfficiency', 'bodyParticipation', 'triggerReclaimToRange', 'triggerBodyToRange', 'triggerReclaimToCorrection'];
const CELLS = ['SELL+NEW_YORK', 'SELL+LONDON', 'BUY+NEW_YORK', 'BUY+LONDON'];

// ── Detector replay ────────────────────────────────────────────────────────
function replayAt(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !isNySell(trigger.timestamp)) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const followThrough = ft.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !followThrough) continue;
    return { visible, spike, breakout, followThrough, correction, trigger };
  }
  return null;
}

function replayAtAnyDirection(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const followThrough = ft.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !followThrough) continue;
    return { visible, spike, breakout, followThrough, correction, trigger };
  }
  return null;
}

// ── Feature computation (from V3 geometry) ─────────────────────────────────
function computeFeatures(visible, spike, correction, trigger) {
  const corr = visible.slice(correction.correctionStartIndex, correction.correctionExtremeIndex + 1);
  const spikeSize = Math.abs(spike.size);
  const correctionSize = Math.max(0, correction.extremePrice - spike.endPrice);
  const ranges = corr.map((c) => Math.max(0, c.high - c.low));
  const bodyMoves = corr.map((c) => Math.abs(c.close - c.open));
  const closeMoves = corr.slice(1).map((c, i) => Math.abs(c.close - corr[i].close));
  const netCloseMove = Math.abs(corr.at(-1).close - corr[0].close);
  const pathLength = closeMoves.reduce((s, v) => s + v, 0);
  const upperWicks = corr.map((c) => Math.max(0, c.high - Math.max(c.open, c.close)));
  const lowerWicks = corr.map((c) => Math.max(0, Math.min(c.open, c.close) - c.low));
  const reclaim = Math.max(0, correction.extremePrice - trigger.entryPrice);
  const correctionRange = Math.max(...corr.map((c) => c.high)) - Math.min(...corr.map((c) => c.low));
  const triggerCandle = visible[trigger.index];
  const triggerRange = triggerCandle.high - triggerCandle.low;
  const triggerBody = Math.abs(triggerCandle.close - triggerCandle.open);
  const totalRange = ranges.reduce((s, v) => s + v, 0);

  return {
    correctionBars: corr.length,
    correctionToSpike: spikeSize > 0 ? correctionSize / spikeSize : null,
    pathEfficiency: pathLength > 0 ? netCloseMove / pathLength : null,
    bodyParticipation: totalRange > 0 ? bodyMoves.reduce((s, v) => s + v, 0) / totalRange : null,
    triggerReclaimToRange: correctionRange > 0 ? reclaim / correctionRange : null,
    triggerBodyToRange: triggerRange > 0 ? triggerBody / triggerRange : null,
    triggerReclaimToCorrection: correctionSize > 0 ? reclaim / correctionSize : null,
  };
}

// ── Statistical helpers ────────────────────────────────────────────────────
function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => { const pos = (a.length - 1) * f; const lo = Math.floor(pos); const hi = Math.ceil(pos); return p(a[lo] + (a[hi] - a[lo]) * (pos - lo)); };
  return { n: a.length, p25: q(.25), median: q(.5), p75: q(.75), min: p(a[0]), max: p(a.at(-1)) };
}

function median(xs) {
  const a = xs.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function pearson(xs, ys) {
  const pairs = xs.map((x, i) => [x, ys[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 3) return null;
  const xm = pairs.reduce((s, [x]) => s + x, 0) / pairs.length;
  const ym = pairs.reduce((s, [, y]) => s + y, 0) / pairs.length;
  let num = 0, dx = 0, dy = 0;
  for (const [x, y] of pairs) { num += (x - xm) * (y - ym); dx += (x - xm) ** 2; dy += (y - ym) ** 2; }
  return dx && dy ? p(num / Math.sqrt(dx * dy)) : null;
}

function rank(values) {
  const indexed = values.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const out = Array(values.length);
  let i = 0;
  while (i < indexed.length) {
    let j = i + 1;
    while (j < indexed.length && indexed[j].v === indexed[i].v) j++;
    const r = (i + j - 1) / 2 + 1;
    for (let k = i; k < j; k++) out[indexed[k].i] = r;
    i = j;
  }
  return out;
}

function spearman(rows, feature) {
  const pairs = rows.map((x) => [Number(x[feature]), Number(x.r)]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 3) return null;
  const rx = rank(pairs.map(([x]) => x));
  const ry = rank(pairs.map(([, y]) => y));
  return pearson(rx, ry);
}

function outcomeStats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0), losses = r.filter((x) => x < 0);
  const grossWin = wins.reduce((s, x) => s + x, 0);
  const grossLoss = -losses.reduce((s, x) => s + x, 0);
  return {
    n: r.length,
    WR: r.length ? p(wins.length / r.length) : null,
    avgR: r.length ? p(r.reduce((s, x) => s + x, 0) / r.length) : null,
    PF: grossLoss ? p(grossWin / grossLoss) : null,
    totalR: p(r.reduce((s, x) => s + x, 0)),
  };
}

function featureSummary(rows, feature) {
  if (rows.length < 3) return { insufficientData: true, n: rows.length };
  const normal = rows.filter((x) => x.classification === 'NORMAL_WIN');
  const loss = rows.filter((x) => x.classification === 'LOSS');
  const noEx = rows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN');
  const normalVals = normal.map((x) => Number(x[feature])).filter(Number.isFinite);
  const lossVals = loss.map((x) => Number(x[feature])).filter(Number.isFinite);
  const normalMedian = median(normalVals);
  const lossMedian = median(lossVals);
  const delta = Number.isFinite(normalMedian) && Number.isFinite(lossMedian) ? normalMedian - lossMedian : null;
  const allMedian = median(rows.map((x) => Number(x[feature])).filter(Number.isFinite));
  return {
    n: rows.length,
    allMedian: p(allMedian),
    normalN: normalVals.length,
    lossN: lossVals.length,
    normalMedian: p(normalMedian),
    lossMedian: p(lossMedian),
    delta: p(delta),
    spearmanAll: spearman(rows, feature),
    spearmanNoEx: spearman(noEx, feature),
    allFeatureMedian: p(median(rows.map((x) => Number(x[feature])).filter(Number.isFinite))),
    noExFeatureMedian: p(median(noEx.map((x) => Number(x[feature])).filter(Number.isFinite))),
  };
}

function temporalWindows(rows) {
  const result = [];
  for (const split of ['DEV', 'VAL']) {
    const scoped = rows.filter((x) => x.split === split).sort((a, b) => new Date(a.time) - new Date(b.time));
    const mid = Math.ceil(scoped.length / 2);
    for (const [i, w] of [scoped.slice(0, mid), scoped.slice(mid)].entries()) {
      if (w.length === 0) continue;
      result.push({
        id: `${split}_H${i + 1}`,
        n: w.length,
        outcome: outcomeStats(w),
        nonExOutcome: outcomeStats(w.filter((x) => x.classification !== 'EXCEPTIONAL_WIN')),
        features: Object.fromEntries(FEATURES.map((f) => [f, featureSummary(w, f)])),
      });
    }
  }
  return result;
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const targets = (base.trades ?? [])
    .map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result, session: t.session }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex >= 0 && t.entryIndex < PRE_HOLDOUT && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r));

  // ── Replay all pre-holdout trades ──────────────────────────────────────
  const rows = [];
  let replayFailures = 0;
  let replaySuccess = 0;

  for (const t of targets) {
    const x = replayAtAnyDirection(candles, t.entryIndex);
    if (!x || x.trigger.timestamp !== t.entryTime || x.trigger.direction !== t.direction) {
      replayFailures++;
      continue;
    }
    replaySuccess++;
    const { visible, spike, correction, trigger } = x;
    const features = computeFeatures(visible, spike, correction, trigger);
    const cell = `${t.direction}+${t.session}`;
    rows.push({
      split: t.entryIndex < DEV_CUTOFF ? 'DEV' : 'VAL',
      time: t.entryTime,
      r: t.r,
      classification: t.r >= 5 ? 'EXCEPTIONAL_WIN' : t.r > 0 ? 'NORMAL_WIN' : 'LOSS',
      direction: t.direction,
      session: t.session,
      cell,
      ...features,
    });
  }

  rows.sort((a, b) => new Date(a.time) - new Date(b.time));

  // ── Data integrity report ──────────────────────────────────────────────
  const dev = rows.filter((x) => x.split === 'DEV');
  const val = rows.filter((x) => x.split === 'VAL');
  const allPreHoldout = rows;
  const exceptional = rows.filter((x) => x.classification === 'EXCEPTIONAL_WIN');

  const cellCounts = {};
  for (const c of CELLS) {
    cellCounts[c] = { total: 0, DEV: 0, VAL: 0 };
  }
  for (const r of rows) {
    if (cellCounts[r.cell]) {
      cellCounts[r.cell].total++;
      cellCounts[r.cell][r.split]++;
    }
  }

  // Count null features per cell
  const nullFeatures = {};
  for (const c of CELLS) {
    nullFeatures[c] = {};
    for (const f of FEATURES) {
      nullFeatures[c][f] = rows.filter((r) => r.cell === c && r[f] === null).length;
    }
  }

  // ── Per-cell analysis ──────────────────────────────────────────────────
  const cellResults = {};
  for (const cellLabel of CELLS) {
    const cellRows = rows.filter((r) => r.cell === cellLabel);
    const cellDev = cellRows.filter((r) => r.split === 'DEV');
    const cellVal = cellRows.filter((r) => r.split === 'VAL');
    const cellNoEx = cellRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');

    if (cellRows.length < 5) {
      cellResults[cellLabel] = { insufficientData: true, n: cellRows.length, message: `N=${cellRows.length} is too small for meaningful analysis` };
      continue;
    }

    cellResults[cellLabel] = {
      overall: { all: outcomeStats(cellRows), dev: outcomeStats(cellDev), val: outcomeStats(cellVal), nonEx: outcomeStats(cellNoEx) },
      exceptionalCount: cellRows.filter((r) => r.classification === 'EXCEPTIONAL_WIN').length,
      features: Object.fromEntries(FEATURES.map((f) => [f, {
        all: featureSummary(cellRows, f),
        dev: featureSummary(cellDev, f),
        val: featureSummary(cellVal, f),
        noEx: featureSummary(cellNoEx, f),
      }])),
      temporalWindows: temporalWindows(cellRows),
    };
  }

  // ── Cross-cell feature comparison ──────────────────────────────────────
  const crossCellComparison = {};
  for (const f of FEATURES) {
    crossCellComparison[f] = {};
    for (const cellLabel of CELLS) {
      const cellRows = rows.filter((r) => r.cell === cellLabel);
      if (cellRows.length < 5) { crossCellComparison[f][cellLabel] = { insufficientData: true }; continue; }
      const devRows = cellRows.filter((r) => r.split === 'DEV');
      const valRows = cellRows.filter((r) => r.split === 'VAL');
      crossCellComparison[f][cellLabel] = {
        allSpearman: spearman(cellRows, f),
        devSpearman: devRows.length >= 3 ? spearman(devRows, f) : null,
        valSpearman: valRows.length >= 3 ? spearman(valRows, f) : null,
        noExSpearman: spearman(cellRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN'), f),
      };
    }
  }

  // ── Sign stability matrix ──────────────────────────────────────────────
  const signStability = {};
  for (const f of FEATURES) {
    signStability[f] = {};
    for (const cellLabel of CELLS) {
      const s = crossCellComparison[f][cellLabel];
      if (!s || s.insufficientData) { signStability[f][cellLabel] = 'INSUFFICIENT_DATA'; continue; }
      const signs = [s.allSpearman, s.devSpearman, s.valSpearman, s.noExSpearman].filter(Number.isFinite);
      if (signs.length === 0) { signStability[f][cellLabel] = 'NO_VALID_SPEARMAN'; continue; }
      const positive = signs.filter((x) => x > 0).length;
      const negative = signs.filter((x) => x < 0).length;
      if (positive === signs.length) signStability[f][cellLabel] = 'CONSISTENTLY_POSITIVE';
      else if (negative === signs.length) signStability[f][cellLabel] = 'CONSISTENTLY_NEGATIVE';
      else signStability[f][cellLabel] = 'MIXED';
    }
  }

  // ── Build report ───────────────────────────────────────────────────────
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_FEATURE_GENERALIZATION_ACROSS_SEGMENTS',
    timeframe: '5m',
    experimentType: 'GENERALIZATION_REPLICATION',
    scope: {
      source: 'canonical baseline trades + deterministic detector replay',
      totalResolvedBaseline: targets.length,
      replaySuccess,
      replayFailures,
      preHoldoutN: allPreHoldout.length,
      devN: dev.length,
      valN: val.length,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    dataIntegrity: {
      replayMatchRate: p(replaySuccess / targets.length),
      replayFailures,
      replayFailureNote: replayFailures > 0 ? `${replayFailures} trades could not be deterministically replayed. These trades either have no matching spike-correction-trigger chain or the baseline entry does not correspond to the first detected trigger.` : 'All baseline trades successfully replayed.',
      nullFeatureCounts: nullFeatures,
    },
    cellCounts,
    methodology: {
      purpose: 'Generalization / replication test of pre-entry geometry features across direction×session segments.',
      features: FEATURES,
      segments: CELLS,
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      holdoutLocked: true,
      interpretation: 'This experiment tests whether feature-outcome associations observed in NY SELL generalize to other segments. No feature threshold or trading rule is selected by this report.',
      exceptionalDefinition: 'r >= 5',
      temporalReplication: 'DEV_H1/DEV_H2/VAL_H1/VAL_H2 where sample size permits.',
      insufficientSamplePolicy: 'Cells with N < 5 are reported as insufficient data, not as zero or failure.',
    },
    overall: {
      all: outcomeStats(rows),
      dev: outcomeStats(dev),
      val: outcomeStats(val),
      nonEx: outcomeStats(rows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN')),
      exceptionalCount: exceptional.length,
    },
    cellResults,
    crossCellComparison,
    signStability,
    cases: rows.map((x) => ({
      split: x.split,
      time: x.time,
      r: x.r,
      classification: x.classification,
      direction: x.direction,
      session: x.session,
      cell: x.cell,
      ...Object.fromEntries(FEATURES.map((f) => [f, x[f]])),
    })),
  };

  // ── Write report ───────────────────────────────────────────────────────
  await mkdir(OUT, { recursive: true });
  const outPath = resolve(OUT, '5m.json');
  await writeFile(outPath, JSON.stringify(report, null, 2));

  // ── Compact stdout ─────────────────────────────────────────────────────
  console.log('FEATURE_GENERALIZATION N=' + allPreHoldout.length + ' DEV=' + dev.length + ' VAL=' + val.length + ' FRESH=LOCKED');
  console.log('REPLAY: success=' + replaySuccess + ' failures=' + replayFailures + ' rate=' + p(replaySuccess / targets.length));
  console.log('');
  console.log('CELL COUNTS:');
  for (const c of CELLS) {
    const cc = cellCounts[c];
    console.log('  ' + c + ': total=' + cc.total + ' DEV=' + cc.DEV + ' VAL=' + cc.VAL);
  }
  console.log('');

  // Per-cell outcomes
  console.log('CELL OUTCOMES:');
  for (const c of CELLS) {
    const cr = cellResults[c];
    if (!cr || cr.insufficientData) { console.log('  ' + c + ': INSUFFICIENT DATA (N=' + (cr?.n ?? 0) + ')'); continue; }
    const o = cr.overall;
    console.log('  ' + c + ': N=' + o.all.n + ' avgR=' + o.all.avgR + ' PF=' + o.all.PF + ' | DEV avgR=' + o.dev.avgR + ' | VAL avgR=' + o.val.avgR + ' | noEx avgR=' + o.nonEx.avgR + ' exceptional=' + cr.exceptionalCount);
  }
  console.log('');

  // Per-cell feature Spearman
  console.log('SPEARMAN(feature, rMultiple) — ALL / NO_EX:');
  for (const f of FEATURES) {
    const line = ['  ' + f + ':'];
    for (const c of CELLS) {
      const s = crossCellComparison[f][c];
      if (!s || s.insufficientData) { line.push(c + '=N/A'); continue; }
      line.push(c + '=' + (s.allSpearman ?? '-') + '/' + (s.noExSpearman ?? '-'));
    }
    console.log(line.join(' '));
  }
  console.log('');

  // Sign stability
  console.log('SIGN STABILITY (across allSpearman / devSpearman / valSpearman / noExSpearman):');
  for (const f of FEATURES) {
    const line = ['  ' + f + ':'];
    for (const c of CELLS) {
      line.push(c + '=' + signStability[f][c]);
    }
    console.log(line.join(' '));
  }
  console.log('');

  // Temporal windows summary (only for cells with data)
  console.log('TEMPORAL WINDOWS:');
  for (const c of CELLS) {
    const cr = cellResults[c];
    if (!cr || cr.insufficientData || !cr.temporalWindows?.length) continue;
    for (const tw of cr.temporalWindows) {
      console.log('  ' + c + ' ' + tw.id + ': N=' + tw.n + ' avgR=' + tw.outcome.avgR + ' PF=' + tw.outcome.PF + ' | noEx avgR=' + tw.nonExOutcome.avgR);
    }
  }
  console.log('');

  console.log('EXPERIMENT_TYPE=GENERALIZATION_REPLICATION');
  console.log('NO_FEATURE_THRESHOLD_SELECTED NO_RULE NO_FRESH');
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
  console.log('REPORT=' + outPath);
}

await main();
