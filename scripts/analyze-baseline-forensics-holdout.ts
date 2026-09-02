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
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-baseline-forensics-holdout');
const HOLDOUT_CANDLES = Number(process.env.FRESH_HOLDOUT_CANDLES ?? '5000');
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

interface ForensicCandidate extends BacktestCandidate {
  readonly breakoutIndex: number;
  readonly spikeStartIndex: number;
  readonly spikeEndIndex: number;
  readonly followThroughIndex: number;
  readonly spikeSize: number;
  readonly rewardRisk: number;
}

const decide: StrategyADecision = (event) => {
  const candles = event.visibleCandles;
  if (candles.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];
  const breakouts = detectBreakout(candles, BREAKOUT_LOOKBACK);
  const followThrough = detectFollowThrough(candles, breakouts, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(candles, breakouts, followThrough, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
  const candidates: ForensicCandidate[] = [];
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
      entryIndex: trigger.index,
      entryTime: trigger.timestamp,
      direction: trigger.direction,
      entry: trigger.entryPrice,
      stopLoss: invalidation.invalidationLevel,
      tp1: projection.tp1,
      session: session.session,
      qualityGrade: quality.grade,
      qualityScore: quality.score,
      structureScore: spike.structureScore,
      overlapScore: spike.overlapScore,
      hasPGAPEvidence: spike.hasPGAPEvidence,
      nearRoundLevel: location.nearRoundLevel,
      emaAligned: emaContext.aligned,
      breakoutIndex: spike.breakoutIndex,
      spikeStartIndex: spike.startIndex,
      spikeEndIndex: spike.endIndex,
      followThroughIndex: spike.followThroughIndex,
      spikeSize: spike.size,
      rewardRisk: reward / risk,
    });
  }
  return candidates.slice(0, 1);
};

function metric(trades: readonly BacktestTrade[]) {
  const closed = trades.filter((t) => t.rMultiple !== null);
  const wins = closed.filter((t) => t.rMultiple! > 0);
  const losses = closed.filter((t) => t.rMultiple! < 0);
  const totalR = closed.reduce((s, t) => s + t.rMultiple!, 0);
  const grossWin = wins.reduce((s, t) => s + t.rMultiple!, 0);
  const grossLoss = Math.abs(losses.reduce((s, t) => s + t.rMultiple!, 0));
  return {
    n: closed.length,
    wins: wins.length,
    losses: losses.length,
    winRate: closed.length ? wins.length / closed.length : 0,
    avgR: closed.length ? totalR / closed.length : 0,
    totalR,
    profitFactor: grossLoss ? grossWin / grossLoss : null,
  };
}

function bucketNumber(value: number | undefined, edges: readonly number[]): string {
  if (value === undefined || !Number.isFinite(value)) return 'NA';
  for (let i = 0; i < edges.length; i += 1) if (value < edges[i]!) return `<${edges[i]}`;
  return `>=${edges.at(-1)}`;
}

function summarize<T>(items: readonly T[], key: (item: T) => string, tradeOf: (item: T) => BacktestTrade) {
  const groups = new Map<string, BacktestTrade[]>();
  for (const item of items) {
    const k = key(item);
    const arr = groups.get(k) ?? [];
    arr.push(tradeOf(item));
    groups.set(k, arr);
  }
  return Object.fromEntries([...groups.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([k, ts]) => [k, metric(ts)]));
}

function quantiles(values: readonly number[]) {
  const v = [...values].filter(Number.isFinite).sort((a, b) => a - b);
  if (!v.length) return null;
  const q = (p: number) => v[Math.min(v.length - 1, Math.floor((v.length - 1) * p))]!;
  return { p10: q(0.10), p25: q(0.25), p50: q(0.50), p75: q(0.75), p90: q(0.90) };
}

function minutesOfDay(timestamp: string): number {
  const d = new Date(timestamp);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

async function loadDataset(timeframe: '1min' | '5min'): Promise<HistoricalDataset> {
  return JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')) as HistoricalDataset;
}

async function run(timeframe: '1min' | '5min'): Promise<void> {
  const dataset = await loadDataset(timeframe);
  if (dataset.candles.length < HOLDOUT_CANDLES * 3) throw new Error(`${timeframe}: expected at least ${HOLDOUT_CANDLES * 3} candles, got ${dataset.candles.length}`);
  const splitIndex = dataset.candles.length - HOLDOUT_CANDLES;
  const result = runStrategyABacktest(dataset.candles, decide).result;
  const holdoutTrades = result.trades.filter((t) => t.entryIndex >= splitIndex && t.rMultiple !== null);
  const allCandidates = result.trades.filter((t) => t.entryIndex >= splitIndex) as Array<BacktestTrade & ForensicCandidate>;
  const candidates = allCandidates as readonly ForensicCandidate[];
  const wins = candidates.filter((t) => t.rMultiple! > 0);
  const losses = candidates.filter((t) => t.rMultiple! < 0);
  const byOutcome = (items: readonly ForensicCandidate[]) => ({
    n: items.length,
    avgR: metric(items.map((t) => t as BacktestTrade)).avgR,
    qualityScore: quantiles(items.map((t) => t.qualityScore ?? NaN)),
    structureScore: quantiles(items.map((t) => t.structureScore ?? NaN)),
    overlapScore: quantiles(items.map((t) => t.overlapScore ?? NaN)),
    rewardRisk: quantiles(items.map((t) => t.rewardRisk)),
    spikeSize: quantiles(items.map((t) => t.spikeSize)),
  });

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'BASELINE_FORENSICS_HOLDOUT',
    warning: 'Post-hoc descriptive analysis only. No production filter or threshold is validated by this report.',
    timeframe,
    symbol: dataset.symbol,
    source: dataset.source,
    candles: dataset.candles.length,
    holdoutCandles: HOLDOUT_CANDLES,
    splitIndex,
    holdoutFrom: dataset.candles[splitIndex]?.timestamp ?? null,
    holdoutTo: dataset.candles.at(-1)?.timestamp ?? null,
    baseline: metric(holdoutTrades),
    winners: byOutcome(wins),
    losers: byOutcome(losses),
    categorical: {
      direction: summarize(candidates, (t) => t.direction, (t) => t),
      session: summarize(candidates, (t) => t.session ?? 'NA', (t) => t),
      qualityGrade: summarize(candidates, (t) => t.qualityGrade ?? 'NA', (t) => t),
      emaAligned: summarize(candidates, (t) => String(t.emaAligned), (t) => t),
      nearRoundLevel: summarize(candidates, (t) => String(t.nearRoundLevel), (t) => t),
      hasPGAPEvidence: summarize(candidates, (t) => String(t.hasPGAPEvidence), (t) => t),
      qualityScore: summarize(candidates, (t) => bucketNumber(t.qualityScore, [6, 8, 10]), (t) => t),
      structureScore: summarize(candidates, (t) => bucketNumber(t.structureScore, [0.55, 0.70, 0.85]), (t) => t),
      overlapScore: summarize(candidates, (t) => bucketNumber(t.overlapScore, [0.60, 0.70, 0.85]), (t) => t),
      rewardRisk: summarize(candidates, (t) => bucketNumber(t.rewardRisk, [1, 1.5, 2, 3]), (t) => t),
      entryHourUTC: summarize(candidates, (t) => String(Math.floor(minutesOfDay(t.entryTime) / 60)).padStart(2, '0'), (t) => t),
    },
    tradeSamples: {
      worst: [...losses].sort((a, b) => (a.rMultiple! - b.rMultiple!)).slice(0, 10).map((t) => ({ entryIndex: t.entryIndex, entryTime: t.entryTime, direction: t.direction, session: t.session, rMultiple: t.rMultiple, qualityGrade: t.qualityGrade, qualityScore: t.qualityScore, structureScore: t.structureScore, overlapScore: t.overlapScore, emaAligned: t.emaAligned, nearRoundLevel: t.nearRoundLevel, rewardRisk: t.rewardRisk })),
      best: [...wins].sort((a, b) => (b.rMultiple! - a.rMultiple!)).slice(0, 10).map((t) => ({ entryIndex: t.entryIndex, entryTime: t.entryTime, direction: t.direction, session: t.session, rMultiple: t.rMultiple, qualityGrade: t.qualityGrade, qualityScore: t.qualityScore, structureScore: t.structureScore, overlapScore: t.overlapScore, emaAligned: t.emaAligned, nearRoundLevel: t.nearRoundLevel, rewardRisk: t.rewardRisk })),
    },
  };

  const out = resolve(OUTPUT, `${timeframe}.json`);
  await mkdir(OUTPUT, { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: holdout=${holdoutTrades.length} wins=${wins.length} losses=${losses.length} avgR=${report.baseline.avgR.toFixed(4)} PF=${report.baseline.profitFactor?.toFixed(4) ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
