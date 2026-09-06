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
const V3 = resolve(ROOT, 'data/reports/strategy-a-ny-sell-correction-path-geometry-v3/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-trigger-process-features');
const DEV = 6000;
const PRE = 10000;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
const utcMinutes = (ts) => { const d = new Date(ts); return d.getUTCHours() * 60 + d.getUTCMinutes(); };
const isNySell = (ts) => { const m = utcMinutes(ts); return m >= 960 && m < 1320; };

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

// ── Trigger process features ───────────────────────────────────────────────

function computeTriggerProcessFeatures(visible, correction, trigger, spike) {
  const triggerDelay = trigger.index - correction.correctionExtremeIndex;
  const intermediateCount = triggerDelay - 1;

  // Intermediate candles: strictly between correction extreme and trigger candle
  const intermediate = [];
  for (let i = correction.correctionExtremeIndex + 1; i < trigger.index; i++) {
    intermediate.push(visible[i]);
  }
  if (intermediate.length !== intermediateCount) {
    throw new Error(`Intermediate candle count mismatch: expected ${intermediateCount}, got ${intermediate.length}`);
  }

  const triggerLevel = correction.extremePrice;
  const correctionSize = correction.extremePrice - spike.endPrice;

  // Feature 2: triggerPathRetraceDepth
  // For SELL: max adverse excursion = max intermediate high - triggerLevel, normalized by correctionSize
  let triggerPathRetraceDepth = 0;
  if (intermediateCount > 0) {
    const maxHigh = Math.max(...intermediate.map((c) => c.high));
    const adverseExcursion = Math.max(0, maxHigh - triggerLevel);
    triggerPathRetraceDepth = correctionSize > 0 ? adverseExcursion / correctionSize : 0;
  }

  // Feature 3: triggerPathFailedReclaims
  // For SELL: count of intermediate candles where low < triggerLevel AND close >= triggerLevel
  let triggerPathFailedReclaims = 0;
  if (intermediateCount > 0) {
    const failedCount = intermediate.filter((c) => c.low < triggerLevel && c.close >= triggerLevel).length;
    triggerPathFailedReclaims = failedCount / intermediateCount;
  }

  return {
    triggerDelay,
    intermediateCount,
    triggerPathRetraceDepth,
    triggerPathFailedReclaims,
  };
}

// ── Statistical helpers ────────────────────────────────────────────────────

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => { const pos = (a.length - 1) * f; const lo = Math.floor(pos); const hi = Math.ceil(pos); return p(a[lo] + (a[hi] - a[lo]) * (pos - lo)); };
  return { n: a.length, p25: q(.25), median: q(.5), p75: q(.75), min: p(a[0]), max: p(a.at(-1)) };
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

function featureSummary(rows, feature) {
  const normal = rows.filter((x) => x.classification === 'NORMAL_WIN');
  const loss = rows.filter((x) => x.classification === 'LOSS');
  const noExceptional = rows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN');
  const normalVals = normal.map((x) => Number(x[feature])).filter(Number.isFinite);
  const lossVals = loss.map((x) => Number(x[feature])).filter(Number.isFinite);
  const normalMedian = median(normalVals);
  const lossMedian = median(lossVals);
  const delta = Number.isFinite(normalMedian) && Number.isFinite(lossMedian) ? normalMedian - lossMedian : null;
  return {
    normalN: normalVals.length,
    lossN: lossVals.length,
    normalMedian: p(normalMedian),
    lossMedian: p(lossMedian),
    delta: p(delta),
    spearmanAll: spearman(rows, feature),
    spearmanNoExceptional: spearman(noExceptional, feature),
    allMedian: p(median(rows.map((x) => Number(x[feature])).filter(Number.isFinite))),
    noExceptionalMedian: p(median(noExceptional.map((x) => Number(x[feature])).filter(Number.isFinite))),
  };
}

function temporalWindows(rows) {
  const result = [];
  for (const split of ['DEV', 'VAL']) {
    const scoped = rows.filter((x) => x.split === split).sort((a, b) => new Date(a.time) - new Date(b.time));
    const mid = Math.ceil(scoped.length / 2);
    for (const [i, w] of [scoped.slice(0, mid), scoped.slice(mid)].entries()) {
      result.push({
        id: `${split}_H${i + 1}`,
        split,
        n: w.length,
        start: w[0]?.time ?? null,
        end: w.at(-1)?.time ?? null,
        outcome: outcomeStats(w),
        nonExceptionalOutcome: outcomeStats(w.filter((x) => x.classification !== 'EXCEPTIONAL_WIN')),
        features: Object.fromEntries(FEATURES.map((f) => [f, featureSummary(w, f)])),
      });
    }
  }
  return result;
}

// ── Features to analyze ────────────────────────────────────────────────────
const FEATURES = ['triggerDelay', 'triggerPathRetraceDepth', 'triggerPathFailedReclaims'];

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const v3 = JSON.parse(await readFile(V3, 'utf8'));

  // Build V3 case lookup by time for cross-referencing
  const v3ByTime = new Map((v3.cases ?? []).map((c) => [c.time, c]));

  const targets = (base.trades ?? [])
    .map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex < PRE && t.direction === 'SELL' && isNySell(t.entryTime) && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r));

  const rows = [];
  for (const t of targets) {
    const x = replayAt(candles, t.entryIndex);
    if (!x || x.trigger.timestamp !== t.entryTime) throw new Error(`Lineage mismatch at ${t.entryIndex}`);
    const { visible, spike, correction, trigger } = x;

    const tp = computeTriggerProcessFeatures(visible, correction, trigger, spike);

    // Merge V3 geometry features for cross-reference
    const v3case = v3ByTime.get(t.entryTime) ?? {};

    rows.push({
      split: t.entryIndex < DEV ? 'DEV' : 'VAL',
      time: t.entryTime,
      r: t.r,
      classification: t.r >= 5 ? 'EXCEPTIONAL_WIN' : t.r > 0 ? 'NORMAL_WIN' : 'LOSS',
      correctionExtremeIndex: correction.correctionExtremeIndex,
      triggerIndex: trigger.index,
      ...tp,
      // V3 geometry cross-reference features (already in discriminative pipeline)
      correctionBars: v3case.correctionBars ?? null,
      correctionToSpike: v3case.correctionToSpike ?? null,
      pathEfficiency: v3case.pathEfficiency ?? null,
      triggerReclaimToRange: v3case.triggerReclaimToRange ?? null,
      triggerBodyToRange: v3case.triggerBodyToRange ?? null,
      triggerCloseLocation: v3case.triggerCloseLocation ?? null,
      triggerReclaimToCorrection: v3case.triggerReclaimToCorrection ?? null,
    });
  }

  rows.sort((a, b) => new Date(a.time) - new Date(b.time));

  // Verify lineage: every V3 time must be present
  const rowTimes = new Set(rows.map((r) => r.time));
  for (const v3c of v3.cases ?? []) {
    if (!rowTimes.has(v3c.time)) throw new Error(`V3 case ${v3c.time} not found in replay results`);
  }

  const dev = rows.filter((x) => x.split === 'DEV');
  const val = rows.filter((x) => x.split === 'VAL');
  const noExceptional = rows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN');
  const pathNonzero = rows.filter((x) => x.intermediateCount > 0);

  // ── Build report ──────────────────────────────────────────────────────
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_TRIGGER_PROCESS_FEATURES',
    timeframe: '5m',
    scope: {
      source: 'canonical baseline trades + deterministic detector replay',
      n: rows.length,
      dev: dev.length,
      val: val.length,
      freshHoldoutExcluded: true,
      productionUntouched: true,
      pathFeatureNonzeroN: pathNonzero.length,
      pathFeatureTotalN: rows.length,
      pathFeatureLimitation: `${pathNonzero.length}/${rows.length} cases have intermediate candles (triggerDelay > 1). Path features are 0 for the remaining ${rows.length - pathNonzero.length} cases. Statistical claims about path features are descriptive only due to this severe sample limitation.`,
    },
    methodology: {
      purpose: 'Descriptive analysis of trigger-process features: timing, adverse excursion during the trigger path, and frequency of failed reclaim attempts.',
      features: FEATURES,
      featureDefinitions: {
        triggerDelay: 'trigger.index - correction.correctionExtremeIndex. Integer ≥ 1. Number of 5m candles between the correction extreme and the entry trigger.',
        triggerPathRetraceDepth: 'For SELL: max(0, max(intermediate.high) - triggerLevel) / correctionSize. Measures maximum adverse excursion during the intermediate path, normalized by correction magnitude. Returns 0 when triggerDelay = 1.',
        triggerPathFailedReclaims: 'For SELL: count(intermediate.candle where low < triggerLevel AND close >= triggerLevel) / intermediateCount. Measures frequency of intrabar level tests that failed to close beyond the trigger level. Returns 0 when triggerDelay = 1.',
      },
      triggerCandleExcluded: 'Neither path feature uses the trigger candle. Intermediate candles are indices (correctionExtremeIndex + 1) through (trigger.index - 1), strictly excluding the trigger candle.',
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      holdoutLocked: true,
      interpretation: 'All results are descriptive. No feature is promoted to a trading rule by this report.',
    },
    overall: {
      all: outcomeStats(rows),
      dev: outcomeStats(dev),
      val: outcomeStats(val),
      nonExceptional: outcomeStats(noExceptional),
      exceptionalCount: rows.length - noExceptional.length,
    },
    temporalWindows: temporalWindows(rows),
    features: Object.fromEntries(FEATURES.map((f) => [f, featureSummary(rows, f)])),
    featureOverlapNotes: {
      triggerDelay_note: 'Identical to entryDelayFromCorrection in expanded anatomy. NOT in the V3/discriminative/temporal-replication pipeline. First inclusion in the standardized outcome-association framework.',
      triggerPathRetraceDepth_note: 'Genuinely new. Distinct from triggerReclaimToRange (trigger candle reclaim vs intermediate path adverse excursion). Distinct from pathEfficiency (correction path vs trigger path).',
      triggerPathFailedReclaims_note: 'Genuinely new. No existing feature counts intrabar level tests. Distinct from triggerPathRetraceDepth (frequency vs magnitude).',
      triggerDelay_vs_correctionBars: 'triggerDelay measures the gap between correction and trigger. correctionBars measures the duration of the correction itself. Different segments of the trade lifecycle.',
      pathFeatures_sampleLimitation: `${pathNonzero.length}/${rows.length} cases have intermediate candles. Path feature Spearman correlations and temporal stability are computed on the full sample (24 zeros + ${pathNonzero.length} non-zeros) and should not be over-interpreted.`,
    },
    cases: rows.map((x) => ({
      split: x.split,
      time: x.time,
      r: x.r,
      classification: x.classification,
      correctionExtremeIndex: x.correctionExtremeIndex,
      triggerIndex: x.triggerIndex,
      triggerDelay: x.triggerDelay,
      intermediateCount: x.intermediateCount,
      triggerPathRetraceDepth: x.triggerPathRetraceDepth,
      triggerPathFailedReclaims: x.triggerPathFailedReclaims,
    })),
  };

  // ── Write report ──────────────────────────────────────────────────────
  await mkdir(OUT, { recursive: true });
  const outPath = resolve(OUT, '5m.json');
  await writeFile(outPath, JSON.stringify(report, null, 2));

  // ── Compact stdout ────────────────────────────────────────────────────
  console.log(`TRIGGER_PROCESS N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`PATH_FEATURE_NONZERO=${pathNonzero.length}/${rows.length}`);
  console.log(`ALL avgR=${report.overall.all.avgR} PF=${report.overall.all.PF} | NO_EXCEPTIONAL avgR=${report.overall.nonExceptional.avgR} PF=${report.overall.nonExceptional.PF} | EXCEPTIONAL=${report.overall.exceptionalCount}`);
  console.log(`DEV avgR=${report.overall.dev.avgR} PF=${report.overall.dev.PF} | VAL avgR=${report.overall.val.avgR} PF=${report.overall.val.PF}`);

  // Temporal windows
  for (const w of report.temporalWindows) {
    console.log(`${w.id}: N=${w.n} avgR=${w.outcome.avgR ?? '-'} PF=${w.outcome.PF ?? '-'} | noExAvgR=${w.nonExceptionalOutcome.avgR ?? '-'} noExPF=${w.nonExceptionalOutcome.PF ?? '-'}`);
  }

  // Feature diagnostics
  console.log('');
  console.log('FEATURE DIAGNOSTICS (NORMAL_WIN median - LOSS median):');
  for (const f of FEATURES) {
    const x = report.features[f];
    console.log(`  ${f}: delta=${x.delta ?? '-'} (${x.normalN}/${x.lossN}) spearmanAll=${x.spearmanAll ?? '-'} spearmanNoEx=${x.spearmanNoExceptional ?? '-'}`);
  }

  // Path feature limitation warning
  console.log('');
  console.log(`PATH_FEATURE_NONZERO=${pathNonzero.length}/${rows.length}`);
  console.log(`Path features are 0 for ${rows.length - pathNonzero.length}/${rows.length} cases (triggerDelay=1). Statistical claims about triggerPathRetraceDepth and triggerPathFailedReclaims are descriptive only.`);

  // Non-zero path feature cases
  if (pathNonzero.length > 0) {
    console.log('');
    console.log('NON-ZERO PATH FEATURE CASES:');
    for (const c of pathNonzero) {
      console.log(`  ${c.split} ${c.time} R=${p(c.r)} delay=${c.triggerDelay} retraceDepth=${p(c.triggerPathRetraceDepth)} failedReclaims=${p(c.triggerPathFailedReclaims)}`);
    }
  }

  // Redundancy notes
  console.log('');
  console.log('OVERLAP NOTES:');
  console.log('  triggerDelay = entryDelayFromCorrection (expanded anatomy). New to discriminative pipeline.');
  console.log('  triggerPathRetraceDepth: NEW. Distinct from triggerReclaimToRange (endpoint vs path).');
  console.log('  triggerPathFailedReclaims: NEW. Distinct from retraceDepth (frequency vs magnitude).');

  console.log('');
  console.log(`REPORT=${outPath}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

await main();
