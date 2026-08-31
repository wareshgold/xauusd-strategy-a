import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-structural-compliance');
const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 7 * 60, endMinutes: 16 * 60 },
    { name: 'NEW_YORK', startMinutes: 13 * 60, endMinutes: 22 * 60 },
  ],
  avoidWindows: [],
};

async function loadModules() {
  const base = (name) => pathToFileURL(resolve(ROOT, 'src/domain', name)).href;
  return {
    detectBreakout: (await import(base('market/BreakoutDetector.ts'))).detectBreakout,
    detectFollowThrough: (await import(base('market/FollowThroughDetector.ts'))).detectFollowThrough,
    detectSpikeCandidates: (await import(base('strategy-a/SpikeDetector.ts'))).detectSpikeCandidates,
    detectFirstCorrection: (await import(base('strategy-a/CorrectionDetector.ts'))).detectFirstCorrection,
    detectEntryTrigger: (await import(base('strategy-a/EntryTrigger.ts'))).detectEntryTrigger,
    projectLeg2: (await import(base('strategy-a/LegProjection.ts'))).projectLeg2,
    collectPGAPObservations: (await import(base('strategy-a/PGAPResearch.ts'))).collectPGAPObservations,
    getInvalidationRule: (await import(base('strategy-a/Invalidation.ts'))).getInvalidationRule,
    buildEMAContext: (await import(base('strategy-a/Context.ts'))).buildEMAContext,
    buildLocationContext: (await import(base('strategy-a/Context.ts'))).buildLocationContext,
    buildSessionContext: (await import(base('strategy-a/Context.ts'))).buildSessionContext,
    scoreSetup: (await import(base('strategy-a/QualityScore.ts'))).scoreSetup,
  };
}

async function loadDataset(timeframe) {
  const path = resolve(ROOT, `data/historical/xauusd-${timeframe}.json`);
  return JSON.parse(await readFile(path, 'utf8'));
}

function emptyCounts() {
  return {
    replayEvents: 0,
    spikeFound: 0,
    correctionFound: 0,
    triggerFound: 0,
    projectionFound: 0,
    qualityAllowed: 0,
    baselineEntries: 0,
    pgapObservations: 0,
    pgapCandidates: 0,
    pgapValidated: 0,
    leg2ProjectionAvailable: 0,
    leg2CompletedAtEntry: 0,
    postEntryLeg2Observable: 0,
    postEntryLeg2RatioMedian: null,
    postEntryLeg2RatioP50: null,
    postEntryLeg2RatioP90: null,
    postEntryLeg2RatioMax: null,
  };
}

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const index = (sorted.length - 1) * p;
  const lo = Math.floor(index);
  const hi = Math.ceil(index);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo);
}

function ratioForEntry(candles, entryIndex, direction, leg1Size) {
  if (!(leg1Size > 0) || entryIndex >= candles.length - 1) return null;
  let favorable = 0;
  for (let i = entryIndex + 1; i < candles.length; i += 1) {
    const c = candles[i];
    const move = direction === 'BUY' ? c.high - candles[entryIndex].close : candles[entryIndex].close - c.low;
    favorable = Math.max(favorable, move);
    if (direction === 'BUY' && c.low <= candles[entryIndex].close - leg1Size) break;
    if (direction === 'SELL' && c.high >= candles[entryIndex].close + leg1Size) break;
  }
  return favorable / leg1Size;
}

async function analyze(timeframe, modules) {
  const dataset = await loadDataset(timeframe);
  const candles = dataset.candles;
  const counts = emptyCounts();
  const ratios = [];
  const stageFailures = {};
  const entries = [];

  for (let eventIndex = 0; eventIndex < candles.length; eventIndex += 1) {
    if (eventIndex < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) continue;
    counts.replayEvents += 1;
    const visible = candles.slice(0, eventIndex + 1);
    const breakouts = modules.detectBreakout(visible, BREAKOUT_LOOKBACK);
    const followThrough = modules.detectFollowThrough(visible, breakouts, {
      maxBarsAfterBreakout: FT_MAX_BARS,
      requireCloseBeyondBrokenLevel: true,
    });
    const spikes = modules.detectSpikeCandidates(visible, breakouts, followThrough, {
      maxCandles: SPIKE_MAX_CANDLES,
      minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
      maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
    });

    for (const spike of spikes.candidates) {
      if (spike.endIndex >= eventIndex) continue;
      counts.spikeFound += 1;
      const correction = modules.detectFirstCorrection(visible, spike);
      if (!correction || correction.correctionExtremeIndex >= eventIndex) {
        stageFailures.correction_not_confirmed = (stageFailures.correction_not_confirmed ?? 0) + 1;
        continue;
      }
      counts.correctionFound += 1;
      const pgap = modules.collectPGAPObservations(visible, spike);
      counts.pgapObservations += pgap.length;
      counts.pgapCandidates += pgap.filter((x) => x.classification === 'CANDIDATE').length;

      const trigger = modules.detectEntryTrigger(visible, correction);
      if (!trigger || trigger.index !== eventIndex) continue;
      counts.triggerFound += 1;
      const projection = modules.projectLeg2(visible, correction);
      if (!projection) {
        stageFailures.leg1_projection_missing = (stageFailures.leg1_projection_missing ?? 0) + 1;
        continue;
      }
      counts.projectionFound += 1;
      const ema = modules.buildEMAContext(visible.map((c) => c.close), CONTEXT);
      if (!ema) continue;
      const location = modules.buildLocationContext(trigger.entryPrice, CONTEXT);
      const session = modules.buildSessionContext(trigger.timestamp, CONTEXT);
      const quality = modules.scoreSetup(spike, { ema, location, session });
      if (!quality.tradeAllowed) continue;
      counts.qualityAllowed += 1;
      const invalidation = modules.getInvalidationRule(correction);
      if (!invalidation) continue;
      const entry = {
        entryIndex: trigger.index,
        entryTime: trigger.timestamp,
        direction: trigger.direction,
        spike: { startIndex: spike.startIndex, endIndex: spike.endIndex },
        correction: { startIndex: correction.correctionStartIndex, extremeIndex: correction.correctionExtremeIndex },
        trigger: trigger.reason,
        pgapCandidates: pgap.filter((x) => x.classification === 'CANDIDATE').length,
        leg1Size: projection.leg1Size,
        projectionTP1: projection.tp1,
        twoLegValidation: 'NOT_APPLIED_AT_ENTRY',
      };
      entries.push(entry);
    }
  }

  const unique = new Map();
  for (const entry of entries) unique.set(`${entry.entryIndex}:${entry.direction}`, entry);
  const baselineEntries = [...unique.values()];
  counts.baselineEntries = baselineEntries.length;
  for (const entry of baselineEntries) {
    if (entry.pgapCandidates > 0) counts.pgapValidated += 0;
    const ratio = ratioForEntry(candles, entry.entryIndex, entry.direction, entry.leg1Size);
    if (ratio !== null && Number.isFinite(ratio)) {
      counts.postEntryLeg2Observable += 1;
      ratios.push(ratio);
    }
  }
  counts.leg2ProjectionAvailable = baselineEntries.length;
  counts.leg2CompletedAtEntry = 0;
  counts.postEntryLeg2RatioMedian = percentile(ratios, 0.5);
  counts.postEntryLeg2RatioP50 = percentile(ratios, 0.5);
  counts.postEntryLeg2RatioP90 = percentile(ratios, 0.9);
  counts.postEntryLeg2RatioMax = ratios.length ? Math.max(...ratios) : null;

  const report = {
    strategy: 'Strategy A / SP2L',
    timeframe,
    symbol: dataset.symbol,
    source: dataset.source,
    candles: candles.length,
    counts,
    compliance: {
      spike: counts.spikeFound > 0 ? 'EXERCISED' : 'NOT_EXERCISED',
      correction: counts.correctionFound > 0 ? 'EXERCISED' : 'NOT_EXERCISED',
      pGap: 'RESEARCH_ONLY_NOT_A_GATE',
      leg1: counts.projectionFound > 0 ? 'PROJECTED' : 'NOT_PROJECTED',
      leg2: 'NOT_VALIDATED_AT_ENTRY',
      trigger: counts.triggerFound > 0 ? 'EXERCISED' : 'NOT_EXERCISED',
      entry: counts.baselineEntries > 0 ? 'EXERCISED' : 'NOT_EXERCISED',
    },
    findings: [
      'The baseline creates an entry after correction-extreme reclaim, but does not require a validated P-GAP.',
      'PGAPResearch.ts only records imbalance observations and explicitly does not define a production P-GAP rule.',
      'LegProjection.ts computes a theoretical Leg-2 target from Leg-1 size; it does not validate that a second leg has completed before entry.',
      'The post-entry ratio is diagnostic only: favorable excursion divided by projected Leg-1 size. It must not be used as an entry filter without a separately validated Strategy A rule.',
    ],
    stageFailures,
    entries: baselineEntries,
  };
  await mkdir(REPORT_DIR, { recursive: true });
  const out = resolve(REPORT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: entries=${counts.baselineEntries} PGAPcand=${counts.pgapCandidates} leg2CompletedAtEntry=${counts.leg2CompletedAtEntry} postEntryRatioN=${ratios.length} ratioP50=${counts.postEntryLeg2RatioP50 ?? 'n/a'} ratioP90=${counts.postEntryLeg2RatioP90 ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

const modules = await loadModules();
await analyze('1min', modules);
await analyze('5min', modules);
