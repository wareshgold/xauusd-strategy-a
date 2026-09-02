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
import type { HistoricalDataset } from '../src/backtest/HistoricalCandle.js';

const ROOT = resolve(process.cwd());
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
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

function bump(map, key) { map[key] = (map[key] ?? 0) + 1; }
function median(values) {
  if (!values.length) return null;
  const a = [...values].sort((x, y) => x - y);
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

async function run(timeframe) {
  const dataset = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
  const candles = dataset.candles;
  const stages = Object.fromEntries(['visible','breakout','followThrough','spike','correction','trigger','projection','invalidation','context','quality','riskReward','accepted'].map(k => [k, 0]));
  const rejection = {};
  const accepted = [];
  const triggerCandidates = [];
  const firstCorrectionCandidates = [];
  const spikePaths = [];

  for (let index = 0; index < candles.length; index++) {
    const visible = candles.slice(0, index + 1);
    if (visible.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) continue;
    bump(stages, 'visible');

    const breakouts = detectBreakout(visible, BREAKOUT_LOOKBACK);
    if (!breakouts.length) { bump(rejection, 'no_breakout'); continue; }
    bump(stages, 'breakout');

    const followThrough = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
    if (!followThrough.length) { bump(rejection, 'no_follow_through'); continue; }
    bump(stages, 'followThrough');

    const spikes = detectSpikeCandidates(visible, breakouts, followThrough, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
    const eligibleSpikes = spikes.candidates.filter(s => s.endIndex < index);
    if (!eligibleSpikes.length) { bump(rejection, 'no_eligible_spike'); continue; }
    bump(stages, 'spike');
    spikePaths.push(...eligibleSpikes.map(s => ({ index, spikeStartIndex:s.startIndex, spikeEndIndex:s.endIndex, direction:s.direction, size:s.size, structureScore:s.structureScore, overlapScore:s.overlapScore })));

    let sawCorrection = false;
    let sawTrigger = false;
    let sawProjection = false;
    let sawInvalidation = false;
    let sawContext = false;
    let sawQuality = false;
    let sawRR = false;

    for (const spike of eligibleSpikes) {
      const correction = detectFirstCorrection(visible, spike);
      if (!correction || correction.correctionExtremeIndex >= index) continue;
      sawCorrection = true;
      firstCorrectionCandidates.push({ index, spikeEndIndex:spike.endIndex, correctionStartIndex:correction.correctionStartIndex, correctionExtremeIndex:correction.correctionExtremeIndex, direction:correction.direction, depth:Math.abs(correction.extremePrice - spike.startPrice) / Math.max(Math.abs(spike.endPrice - spike.startPrice), 1e-9) });

      const trigger = detectEntryTrigger(visible, correction);
      if (!trigger || trigger.index !== index) continue;
      sawTrigger = true;
      triggerCandidates.push({ index, timestamp:trigger.timestamp, direction:trigger.direction, entryPrice:trigger.entryPrice, triggerLevel:trigger.triggerLevel, delay:index - correction.correctionExtremeIndex });

      const projection = projectLeg2(visible, correction);
      if (!projection) continue;
      sawProjection = true;
      const invalidation = getInvalidationRule(correction);
      sawInvalidation = true;
      const emaContext = buildEMAContext(visible.map(c => c.close), CONTEXT);
      if (!emaContext) continue;
      const location = buildLocationContext(trigger.entryPrice, CONTEXT);
      const session = buildSessionContext(trigger.timestamp, CONTEXT);
      sawContext = true;
      const quality = scoreSetup(spike, { ema:emaContext, location, session });
      if (!quality.tradeAllowed) continue;
      sawQuality = true;
      const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
      const reward = Math.abs(projection.tp1 - trigger.entryPrice);
      const targetIsDirectional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
      if (risk <= 0 || reward <= 0 || !targetIsDirectional) continue;
      sawRR = true;
      accepted.push({ index, timestamp:trigger.timestamp, direction:trigger.direction, entry:trigger.entryPrice, stopLoss:invalidation.invalidationLevel, tp1:projection.tp1, risk, reward, rr:reward/risk, session:session.session, qualityGrade:quality.grade, qualityScore:quality.score, structureScore:spike.structureScore, overlapScore:spike.overlapScore, spikeStartIndex:spike.startIndex, spikeEndIndex:spike.endIndex, correctionExtremeIndex:correction.correctionExtremeIndex, triggerDelay:index-correction.correctionExtremeIndex, correctionDepth:Math.abs(correction.extremePrice-spike.startPrice)/Math.max(Math.abs(spike.endPrice-spike.startPrice),1e-9) });
    }
    if (sawCorrection) bump(stages, 'correction'); else bump(rejection, 'no_eligible_correction');
    if (sawTrigger) bump(stages, 'trigger'); else bump(rejection, 'no_trigger_at_current_index');
    if (sawProjection) bump(stages, 'projection'); else if (sawTrigger) bump(rejection, 'no_projection');
    if (sawInvalidation) bump(stages, 'invalidation');
    if (sawContext) bump(stages, 'context');
    if (sawQuality) bump(stages, 'quality'); else if (sawContext) bump(rejection, 'quality_rejected');
    if (sawRR) bump(stages, 'riskReward'); else if (sawQuality) bump(rejection, 'invalid_risk_reward');
    if (sawRR) bump(stages, 'accepted');
  }

  const report = {
    strategy:'Strategy A', mode:'DIRECT_BASELINE_PATH_FORENSICS', timeframe, candles:candles.length,
    methodology:'Research-only replay of the same baseline decision path, evaluated candle-by-candle with no future candles. No production thresholds or rules changed.',
    parameters:{BREAKOUT_LOOKBACK,FT_MAX_BARS,SPIKE_MAX_CANDLES,SPIKE_MIN_DIRECTIONAL_FRACTION,SPIKE_MAX_OVERLAP_FRACTION,emaPeriod:CONTEXT.emaPeriod,roundStep:CONTEXT.roundStep,roundDistance:CONTEXT.roundDistance},
    stages, rejectionReasons:rejection,
    counts:{triggerCandidates:triggerCandidates.length,accepted:accepted.length,spikePaths:spikePaths.length,correctionCandidates:firstCorrectionCandidates.length},
    triggerStats:{medianDelay:median(triggerCandidates.map(x=>x.delay)), delays:triggerCandidates.map(x=>x.delay)},
    acceptedStats:{medianRR:median(accepted.map(x=>x.rr)),medianDelay:median(accepted.map(x=>x.triggerDelay)),medianCorrectionDepth:median(accepted.map(x=>x.correctionDepth))},
    accepted,
  };
  await mkdir(OUTPUT,{recursive:true});
  const out=resolve(OUTPUT,`${timeframe}.json`);
  await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: visible=${stages.visible} breakout=${stages.breakout} FT=${stages.followThrough} spike=${stages.spike} correction=${stages.correction} trigger=${stages.trigger} projection=${stages.projection} quality=${stages.quality} RR=${stages.riskReward} accepted=${stages.accepted}`);
  console.log(`  triggerCandidates=${triggerCandidates.length} medianDelay=${report.triggerStats.medianDelay ?? 'n/a'} acceptedMedianRR=${report.acceptedStats.medianRR ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
