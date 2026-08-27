import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.ts';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.ts';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.ts';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.ts';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.ts';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.ts';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.ts';
import { buildEMAContext, buildLocationContext, buildSessionContext, type ContextConfig } from '../src/domain/strategy-a/Context.ts';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.ts';
import { runStrategyABacktest, type StrategyADecision } from '../src/backtest/StrategyAAdapter.ts';
import type { BacktestCandidate } from '../src/backtest/BacktestEngine.ts';
import type { HistoricalDataset } from '../src/backtest/HistoricalCandle.ts';

const ROOT = resolve(process.cwd());
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');
const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT: ContextConfig = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 7 * 60, endMinutes: 16 * 60 },
    { name: 'NEW_YORK', startMinutes: 13 * 60, endMinutes: 22 * 60 },
  ],
  avoidWindows: [],
};

const decide: StrategyADecision = (event) => {
  const candles = event.visibleCandles;
  if (candles.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];

  const breakouts = detectBreakout(candles, BREAKOUT_LOOKBACK);
  const followThrough = detectFollowThrough(candles, breakouts, {
    maxBarsAfterBreakout: FT_MAX_BARS,
    requireCloseBeyondBrokenLevel: true,
  });
  const spikes = detectSpikeCandidates(candles, breakouts, followThrough, {
    maxCandles: SPIKE_MAX_CANDLES,
    minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
    maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
  });

  const candidates: BacktestCandidate[] = [];
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= event.index) continue;
    const correction = detectFirstCorrection(candles, spike);
    if (!correction || correction.correctionExtremeIndex >= event.index) continue;
    const trigger = detectEntryTrigger(candles, correction);
    if (!trigger || trigger.index !== event.index) continue;

    const projection = projectLeg2(candles, correction);
    if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const emaContext = buildEMAContext(candles.map((c) => c.close), CONTEXT);
    if (!emaContext) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema: emaContext, location, session });
    if (!quality.tradeAllowed) continue;

    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (risk <= 0 || reward <= 0) continue;

    candidates.push({
      entryIndex: trigger.index,
      entryTime: trigger.timestamp,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: invalidation.invalidationLevel,
      tp1: projection.tp1,
    });
  }

  return candidates.slice(0, 1);
};

async function loadDataset(timeframe: '1min' | '5min'): Promise<HistoricalDataset> {
  const path = resolve(ROOT, `data/historical/xauusd-${timeframe}.json`);
  return JSON.parse(await readFile(path, 'utf8')) as HistoricalDataset;
}

async function run(timeframe: '1min' | '5min'): Promise<void> {
  const dataset = await loadDataset(timeframe);
  const result = runStrategyABacktest(dataset.candles, decide).result;
  const report = {
    strategy: 'Strategy A / SP2L', mode: 'BASELINE', timeframe,
    symbol: dataset.symbol, source: dataset.source, candles: dataset.candles.length,
    from: dataset.candles[0]?.timestamp ?? null, to: dataset.candles.at(-1)?.timestamp ?? null,
    parameters: { breakoutLookback: BREAKOUT_LOOKBACK, followThroughMaxBars: FT_MAX_BARS, spikeMaxCandles: SPIKE_MAX_CANDLES, spikeMinDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, spikeMaxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION, emaPeriod: CONTEXT.emaPeriod, roundStep: CONTEXT.roundStep, roundDistance: CONTEXT.roundDistance },
    metrics: result.metrics, trades: result.trades,
  };
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await mkdir(OUTPUT, { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: candles=${dataset.candles.length} trades=${result.metrics.trades} winRate=${(result.metrics.winRate * 100).toFixed(2)}% avgR=${result.metrics.averageR.toFixed(4)} PF=${result.metrics.profitFactor?.toFixed(4) ?? 'n/a'} maxDD=${result.metrics.maxDrawdownR.toFixed(4)}R`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
