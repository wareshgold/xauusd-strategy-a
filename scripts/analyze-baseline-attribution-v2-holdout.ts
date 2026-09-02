import { readFile } from 'node:fs/promises';
import { runStrategyABacktest } from '../src/backtest/StrategyAAdapter.js';
import type { HistoricalDataset } from '../src/backtest/HistoricalCandle.js';
import { decide } from './run-baseline-backtest.js';
import type { Candle } from '../src/domain/market/Candle.js';
import type { BacktestTrade } from '../src/backtest/BacktestTypes.js';

const HOLDOUT_CANDLES = Number(process.env.FRESH_HOLDOUT_CANDLES ?? '5000');
const TIMEFRAMES = ['1min', '5min'] as const;

type Trade = BacktestTrade & {
  readonly session?: string;
  readonly qualityScore?: number;
  readonly structureScore?: number;
  readonly overlapScore?: number;
  readonly emaAligned?: boolean;
  readonly nearRoundLevel?: boolean;
  readonly rewardRisk?: number;
};

type Excursion = {
  readonly maeR: number;
  readonly mfeR: number;
  readonly maeBars: number;
  readonly mfeBars: number;
  readonly mfeBeforeMae: boolean;
  readonly maeBeforeMfe: boolean;
  readonly barsToExit: number;
  readonly mfeBeforeExitR: number;
};

function excursion(candles: readonly Candle[], trade: Trade): Excursion {
  const risk = Math.abs(trade.entry - trade.stopLoss);
  if (risk <= 0) throw new Error(`Invalid trade risk at entryIndex=${trade.entryIndex}`);
  let mae = 0;
  let mfe = 0;
  let maeBars = 0;
  let mfeBars = 0;
  let mfeBeforeMae = false;
  let maeBeforeMfe = false;
  let firstMaeBar = Number.POSITIVE_INFINITY;
  let firstMfeBar = Number.POSITIVE_INFINITY;
  let barsToExit = 0;
  let mfeBeforeExitR = 0;

  for (let i = trade.entryIndex + 1; i < candles.length; i += 1) {
    const c = candles[i]!;
    const favorable = trade.direction === 'BUY' ? c.high - trade.entry : trade.entry - c.low;
    const adverse = trade.direction === 'BUY' ? trade.entry - c.low : c.high - trade.entry;
    const mfeR = favorable / risk;
    const maeR = adverse / risk;
    if (mfeR > mfe) { mfe = mfeR; mfeBars = i - trade.entryIndex; }
    if (maeR > mae) { mae = maeR; maeBars = i - trade.entryIndex; }
    if (maeR >= 1 && firstMaeBar === Number.POSITIVE_INFINITY) firstMaeBar = i - trade.entryIndex;
    if (mfeR > 0 && firstMfeBar === Number.POSITIVE_INFINITY) firstMfeBar = i - trade.entryIndex;

    const sl = trade.direction === 'BUY' ? c.low <= trade.stopLoss : c.high >= trade.stopLoss;
    const tp2 = trade.tp2 == null ? false : trade.direction === 'BUY' ? c.high >= trade.tp2 : c.low <= trade.tp2;
    const tp1 = trade.direction === 'BUY' ? c.high >= trade.tp1 : c.low <= trade.tp1;
    if (sl || tp2 || tp1) {
      barsToExit = i - trade.entryIndex;
      mfeBeforeExitR = mfe;
      break;
    }
  }
  if (firstMfeBar < firstMaeBar) mfeBeforeMae = true;
  if (firstMaeBar < firstMfeBar) maeBeforeMfe = true;
  return { maeR: mae, mfeR: mfe, maeBars, mfeBars, mfeBeforeMae, maeBeforeMfe, barsToExit, mfeBeforeExitR };
}

function mean(values: readonly number[]): number | null {
  return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
}

function quantile(values: readonly number[], q: number): number | null {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  if (lo === hi) return sorted[lo]!;
  return sorted[lo]! + (sorted[hi]! - sorted[lo]!) * (pos - lo);
}

function groupSummary(trades: readonly Trade[], excursions: readonly Excursion[]) {
  const rs = trades.map((t) => t.rMultiple).filter((v): v is number => v != null);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r <= 0);
  const grossWin = wins.reduce((a, b) => a + b, 0);
  const grossLoss = Math.abs(losses.reduce((a, b) => a + b, 0));
  return {
    n: trades.length,
    wins: wins.length,
    losses: losses.length,
    winRate: trades.length ? wins.length / trades.length : null,
    avgR: mean(rs),
    totalR: rs.reduce((a, b) => a + b, 0),
    profitFactor: grossLoss ? grossWin / grossLoss : null,
    maeR: { p50: quantile(excursions.map((x) => x.maeR), .5), p90: quantile(excursions.map((x) => x.maeR), .9) },
    mfeR: { p50: quantile(excursions.map((x) => x.mfeR), .5), p90: quantile(excursions.map((x) => x.mfeR), .9) },
    mfeBeforeMaeRate: excursions.length ? excursions.filter((x) => x.mfeBeforeMae).length / excursions.length : null,
    maeBeforeMfeRate: excursions.length ? excursions.filter((x) => x.maeBeforeMfe).length / excursions.length : null,
    medianBarsToExit: quantile(excursions.map((x) => x.barsToExit), .5),
    medianMfeBeforeExitR: quantile(excursions.map((x) => x.mfeBeforeExitR), .5),
  };
}

function summarizeSlice(trades: readonly Trade[], candles: readonly Candle[]) {
  return groupSummary(trades, trades.map((t) => excursion(candles, t)));
}

async function main() {
  for (const timeframe of TIMEFRAMES) {
    const path = `data/historical/xauusd-${timeframe}.json`;
    const dataset = JSON.parse(await readFile(path, 'utf8')) as HistoricalDataset;
    const candles = dataset.candles;
    if (candles.length < HOLDOUT_CANDLES * 3) throw new Error(`${timeframe}: dataset too small`);
    const splitIndex = candles.length - HOLDOUT_CANDLES;
    const result = runStrategyABacktest(candles, decide);
    const trades = result.result.trades.filter((t) => t.entryIndex >= splitIndex && t.rMultiple != null) as unknown as Trade[];
    const byDirection = Object.fromEntries(['BUY', 'SELL'].map((d) => [d, summarizeSlice(trades.filter((t) => t.direction === d), candles)]));
    const bySession = Object.fromEntries(['LONDON', 'NEW_YORK', 'OUTSIDE'].map((s) => [s, summarizeSlice(trades.filter((t) => (t.session ?? 'OUTSIDE') === s), candles)]));
    const byOutcome = {
      winners: summarizeSlice(trades.filter((t) => (t.rMultiple ?? -1) > 0), candles),
      losers: summarizeSlice(trades.filter((t) => (t.rMultiple ?? -1) <= 0), candles),
    };
    const byDirectionSession: Record<string, ReturnType<typeof summarizeSlice>> = {};
    for (const d of ['BUY', 'SELL']) for (const s of ['LONDON', 'NEW_YORK', 'OUTSIDE']) {
      const subset = trades.filter((t) => t.direction === d && (t.session ?? 'OUTSIDE') === s);
      byDirectionSession[`${d}_${s}`] = summarizeSlice(subset, candles);
    }
    const report = {
      strategy: 'Strategy A / SP2L', mode: 'BASELINE_ATTRIBUTION_V2_HOLDOUT',
      warning: 'Post-hoc diagnostic only. No production filter, threshold, entry rule, or exit rule is validated by this report.',
      timeframe, symbol: dataset.symbol, source: dataset.source, candles: candles.length,
      holdoutCandles: HOLDOUT_CANDLES, splitIndex,
      holdoutFrom: candles[splitIndex]?.timestamp ?? null, holdoutTo: candles[candles.length - 1]?.timestamp ?? null,
      baseline: summarizeSlice(trades, candles), byOutcome, byDirection, bySession, byDirectionSession,
      interpretationTargets: ['entry timing vs directional bias', 'adverse-first vs favorable-first path', 'realized excursion vs projected target geometry', 'session-direction interaction'],
    };
    const out = `data/reports/strategy-a-baseline-attribution-v2-holdout/${timeframe}.json`;
    const { mkdir, writeFile } = await import('node:fs/promises');
    await mkdir('data/reports/strategy-a-baseline-attribution-v2-holdout', { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2));
    console.log(`${timeframe}: holdout=${trades.length} avgR=${report.baseline.avgR?.toFixed(4)} PF=${report.baseline.profitFactor?.toFixed(4) ?? 'n/a'}`);
    console.log(`Report -> ${out}`);
  }
}

void main();
