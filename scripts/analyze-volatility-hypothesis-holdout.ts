import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
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
import type { BacktestTrade } from '../src/backtest/BacktestTypes.js';
import type { HistoricalDataset } from '../src/backtest/HistoricalCandle.js';

const ROOT = resolve(process.cwd());
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-volatility-hypothesis-holdout');
const HOLDOUT_CANDLES = Number(process.env.FRESH_HOLDOUT_CANDLES ?? '5000');
const FROZEN_RANGE_TO_ATR = 1.25;
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

if (!Number.isInteger(HOLDOUT_CANDLES) || HOLDOUT_CANDLES < 1) {
  throw new Error('FRESH_HOLDOUT_CANDLES must be a positive integer');
}

const decide: StrategyADecision = (event) => {
  const candles = event.visibleCandles;
  if (candles.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];
  const breakouts = detectBreakout(candles, BREAKOUT_LOOKBACK);
  const followThrough = detectFollowThrough(candles, breakouts, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(candles, breakouts, followThrough, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
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
    const targetIsDirectional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
    if (risk <= 0 || reward <= 0 || !targetIsDirectional) continue;
    candidates.push({
      entryIndex: trigger.index, entryTime: trigger.timestamp, direction: trigger.direction,
      entry: trigger.entryPrice, stopLoss: invalidation.invalidationLevel, tp1: projection.tp1,
      session: session.session, qualityGrade: quality.grade, qualityScore: quality.score,
      structureScore: spike.structureScore, overlapScore: spike.overlapScore,
      hasPGAPEvidence: spike.hasPGAPEvidence, nearRoundLevel: location.nearRoundLevel, emaAligned: emaContext.aligned,
    });
  }
  return candidates.slice(0, 1);
};

async function loadDataset(timeframe: '1min' | '5min'): Promise<HistoricalDataset> {
  return JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')) as HistoricalDataset;
}

function atr14(candles: HistoricalDataset['candles'], entryIndex: number): number | null {
  if (entryIndex < 14) return null;
  let sum = 0;
  for (let i = entryIndex - 13; i <= entryIndex; i += 1) {
    const candle = candles[i];
    const prevClose = candles[i - 1]?.close;
    if (!candle || prevClose == null) return null;
    sum += Math.max(candle.high - candle.low, Math.abs(candle.high - prevClose), Math.abs(candle.low - prevClose));
  }
  const value = sum / 14;
  return Number.isFinite(value) && value > 0 ? value : null;
}

function rangeToAtr(candles: HistoricalDataset['candles'], entryIndex: number): number | null {
  const candle = candles[entryIndex];
  if (!candle) return null;
  const atr = atr14(candles, entryIndex);
  if (atr == null) return null;
  return (candle.high - candle.low) / atr;
}

function maxDrawdown(values: number[]): number {
  let equity = 0;
  let peak = 0;
  let maxDD = 0;
  for (const value of values) {
    equity += value;
    peak = Math.max(peak, equity);
    maxDD = Math.max(maxDD, peak - equity);
  }
  return maxDD;
}

function metrics(trades: readonly BacktestTrade[]) {
  const resolved = trades.filter((trade) => trade.rMultiple != null);
  const wins = resolved.filter((trade) => (trade.rMultiple ?? 0) > 0).length;
  const losses = resolved.filter((trade) => (trade.rMultiple ?? 0) < 0).length;
  const rs = resolved.map((trade) => trade.rMultiple as number);
  const grossProfit = rs.filter((r) => r > 0).reduce((a, b) => a + b, 0);
  const grossLoss = Math.abs(rs.filter((r) => r < 0).reduce((a, b) => a + b, 0));
  let consecutiveLosses = 0;
  let currentLosses = 0;
  for (const r of rs) {
    if (r < 0) { currentLosses += 1; consecutiveLosses = Math.max(consecutiveLosses, currentLosses); }
    else currentLosses = 0;
  }
  const totalR = rs.reduce((a, b) => a + b, 0);
  return {
    trades: resolved.length,
    wins,
    losses,
    winRate: resolved.length ? wins / resolved.length : 0,
    averageR: resolved.length ? totalR / resolved.length : 0,
    totalR,
    profitFactor: grossLoss > 0 ? grossProfit / grossLoss : null,
    maxDrawdownR: maxDrawdown(rs),
    consecutiveLosses,
  };
}

async function run(timeframe: '1min' | '5min'): Promise<void> {
  const dataset = await loadDataset(timeframe);
  if (dataset.candles.length < HOLDOUT_CANDLES * 3) {
    throw new Error(`${timeframe}: need at least ${HOLDOUT_CANDLES * 3} candles, found ${dataset.candles.length}`);
  }
  const splitIndex = dataset.candles.length - HOLDOUT_CANDLES;
  const runResult = runStrategyABacktest(dataset.candles, decide).result;
  const holdoutTrades = runResult.trades.filter((trade) => trade.entryIndex >= splitIndex && trade.rMultiple != null);
  const baseline = metrics(holdoutTrades);
  const filteredTrades = holdoutTrades.filter((trade) => {
    const ratio = rangeToAtr(dataset.candles, trade.entryIndex);
    return ratio != null && ratio >= FROZEN_RANGE_TO_ATR;
  });
  const filtered = metrics(filteredTrades);
  const gate = filtered.trades >= 15 && filtered.profitFactor != null && filtered.profitFactor >= 1 && filtered.averageR > 0;
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'FRESH_UNTOUCHED_HOLDOUT',
    timeframe,
    symbol: dataset.symbol,
    source: dataset.source,
    candles: dataset.candles.length,
    holdoutCandles: HOLDOUT_CANDLES,
    splitIndex,
    holdoutFrom: dataset.candles[splitIndex]?.timestamp ?? null,
    holdoutTo: dataset.candles.at(-1)?.timestamp ?? null,
    hypothesis: 'If entry candle range / ATR14 >= 1.25, Strategy A expectancy will be better than baseline.',
    frozenBeforeHoldout: true,
    thresholdSearchPerformed: false,
    filter: { feature: 'entryCandleRangeToATR14', operator: '>=', threshold: FROZEN_RANGE_TO_ATR },
    parameters: { breakoutLookback: BREAKOUT_LOOKBACK, followThroughMaxBars: FT_MAX_BARS, spikeMaxCandles: SPIKE_MAX_CANDLES, spikeMinDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, spikeMaxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION, emaPeriod: CONTEXT.emaPeriod, roundStep: CONTEXT.roundStep, roundDistance: CONTEXT.roundDistance },
    baselineHoldout: baseline,
    filteredHoldout: filtered,
    descriptiveGate: { minTrades: 15, profitFactorAtLeast: 1, averageRPositive: true, passed: gate },
    verdict: gate ? 'SURVIVES_DESCRIPTIVE_GATE_REQUIRES_REVIEW' : 'FAILS_DESCRIPTIVE_GATE',
    trades: filteredTrades.map((trade) => ({ ...trade, entryRangeToAtr14: rangeToAtr(dataset.candles, trade.entryIndex) })),
  };
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await mkdir(OUTPUT, { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: holdout=${baseline.trades} filtered=${filtered.trades} baselineAvgR=${baseline.averageR.toFixed(4)} filteredAvgR=${filtered.averageR.toFixed(4)} baselinePF=${baseline.profitFactor?.toFixed(4) ?? 'n/a'} filteredPF=${filtered.profitFactor?.toFixed(4) ?? 'n/a'} gate=${gate}`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
