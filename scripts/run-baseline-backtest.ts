import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext, type ContextConfig } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';
import { runStrategyABacktest, type StrategyADecision } from '../src/backtest/StrategyAAdapter.js';
import type { BacktestCandidate } from '../src/backtest/BacktestEngine.js';
import type { HistoricalDataset } from '../src/backtest/HistoricalCandle.js';

const ROOT = resolve(process.cwd());
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');

// Baseline parameters are intentionally explicit and NOT optimized.
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

function decide: StrategyADecision = (event) => {
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
    const context = { ema: emaContext, location, session };
    const quality = scoreSetup(spike, context);
    if (!quality.tradeAllowed) continue;

    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    if (risk <= 0) continue;
    const tp1 = projection.tp1;
    const reward = Math.abs(tp1 - trigger.entryPrice);
    if (reward <= 0) continue;

    candidates.push({
      entryIndex: trigger.index,
      entryTime: trigger.timestamp,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: invalidation.invalidationLevel,
      tp1,
    });
  }

  // A replay timestamp represents one decision point. Keep the first valid setup
  // at that timestamp so one candle cannot create duplicate positions.
  return candidates.slice(0, 1);
};

async function loadDataset(timeframe: '1min' | '5min'): Promise<HistoricalDataset> {
  const path = resolve(ROOT, `data/historical/xauusd-${timeframe}.json`);
  const raw = await readFile(path, 'utf8');
  return JSON.parse(raw) as HistoricalDataset;
}

async function run(timeframe: '1min' | '5min'): Promise<void> {
  const dataset = await loadDataset(timeframe);
  const run = runStrategyABacktest(dataset.candles, decide);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'BASELINE',
    timeframe,
    symbol: dataset.symbol,
    source: dataset.source,
    candles: dataset.candles.length,
    from: dataset.candles[0]?.timestamp ?? null,
    to: dataset.candles.at(-1)?.timestamp ?? null,
    parameters: {
      breakoutLookback: BREAKOUT_LOOKBACK,
      followThroughMaxBars: FT_MAX_BARS,
      spikeMaxCandles: SPIKE_MAX_CANDLES,
      spikeMinDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
      spikeMaxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
      emaPeriod: CONTEXT.emaPeriod,
      roundStep: CONTEXT.roundStep,
      roundDistance: CONTEXT.roundDistance,
    },
    metrics: run.result.metrics,
    trades: run.result.trades,
  };
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: candles=${dataset.candles.length} trades=${run.result.metrics.trades} winRate=${(run.result.metrics.winRate * 100).toFixed(2)}% avgR=${run.result.metrics.averageR.toFixed(4)} PF=${run.result.metrics.profitFactor?.toFixed(4) ?? 'n/a'} maxDD=${run.result.metrics.maxDrawdownR.toFixed(4)}R`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
