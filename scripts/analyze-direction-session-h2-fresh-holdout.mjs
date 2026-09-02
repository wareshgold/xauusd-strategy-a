import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-direction-session-h2-fresh-holdout');
const TIMEFRAMES = ['1min', '5min'];
const TOTAL_CANDLES = 15000;
const FRESH_HOLDOUT_CANDLES = 5000;
const CANDIDATE_DIRECTION = 'SELL';
const CANDIDATE_SESSION = 'NEW_YORK';

function quantile(values, q) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

function maxDrawdown(rs) {
  let equity = 0;
  let peak = 0;
  let maxDd = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDd = Math.max(maxDd, peak - equity);
  }
  return maxDd;
}

function maxConsecutiveLosses(rs) {
  let current = 0;
  let max = 0;
  for (const r of rs) {
    if (r <= 0) current += 1;
    else current = 0;
    max = Math.max(max, current);
  }
  return max;
}

function summarize(rows) {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const grossProfit = wins.reduce((a, b) => a + b, 0);
  const grossLoss = -losses.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : null,
    avgR: rs.length ? totalR / rs.length : null,
    totalR,
    profitFactor: grossLoss ? grossProfit / grossLoss : (grossProfit ? null : 0),
    maxDrawdownR: maxDrawdown(rs),
    maxConsecutiveLosses: maxConsecutiveLosses(rs),
  };
}

function excursion(candles, trade) {
  const risk = Math.abs(Number(trade.entry) - Number(trade.stopLoss));
  if (!(risk > 0)) return null;
  let mae = 0;
  let mfe = 0;
  let firstMaeBar = Infinity;
  let firstMfeBar = Infinity;
  let barsToExit = 0;
  let mfeBeforeExitR = 0;
  for (let i = Number(trade.entryIndex) + 1; i < candles.length; i += 1) {
    const c = candles[i];
    const favorable = trade.direction === 'BUY' ? c.high - trade.entry : trade.entry - c.low;
    const adverse = trade.direction === 'BUY' ? trade.entry - c.low : c.high - trade.entry;
    const mfeR = favorable / risk;
    const maeR = adverse / risk;
    if (mfeR > mfe) mfe = mfeR;
    if (maeR > mae) mae = maeR;
    if (mfeR > 0 && firstMfeBar === Infinity) firstMfeBar = i - trade.entryIndex;
    if (maeR >= 1 && firstMaeBar === Infinity) firstMaeBar = i - trade.entryIndex;
    const sl = trade.direction === 'BUY' ? c.low <= trade.stopLoss : c.high >= trade.stopLoss;
    const tp2 = trade.tp2 == null ? false : trade.direction === 'BUY' ? c.high >= trade.tp2 : c.low <= trade.tp2;
    const tp1 = trade.direction === 'BUY' ? c.high >= trade.tp1 : c.low <= trade.tp1;
    if (sl || tp2 || tp1) {
      barsToExit = i - trade.entryIndex;
      mfeBeforeExitR = mfe;
      break;
    }
  }
  return {
    maeR: mae,
    mfeR: mfe,
    mfeBeforeMae: firstMfeBar < firstMaeBar,
    maeBeforeMfe: firstMaeBar < firstMfeBar,
    barsToExit,
    mfeBeforeExitR,
  };
}

function addExcursionStats(summary, rows, candles) {
  const xs = rows.map((t) => excursion(candles, t)).filter(Boolean);
  return {
    ...summary,
    maeR: { p50: quantile(xs.map((x) => x.maeR), 0.5), p90: quantile(xs.map((x) => x.maeR), 0.9) },
    mfeR: { p50: quantile(xs.map((x) => x.mfeR), 0.5), p90: quantile(xs.map((x) => x.mfeR), 0.9) },
    mfeBeforeMaeRate: xs.length ? xs.filter((x) => x.mfeBeforeMae).length / xs.length : null,
    maeBeforeMfeRate: xs.length ? xs.filter((x) => x.maeBeforeMfe).length / xs.length : null,
    medianBarsToExit: quantile(xs.map((x) => x.barsToExit), 0.5),
    medianMfeBeforeExitR: quantile(xs.map((x) => x.mfeBeforeExitR), 0.5),
  };
}

async function run(timeframe) {
  const baselinePath = resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`);
  const candlesPath = resolve(ROOT, `data/historical/xauusd-${timeframe}.json`);
  const source = JSON.parse(await readFile(baselinePath, 'utf8'));
  const candles = JSON.parse(await readFile(candlesPath, 'utf8')).candles ?? [];
  if (candles.length < TOTAL_CANDLES) throw new Error(`${timeframe}: expected at least ${TOTAL_CANDLES} candles, found ${candles.length}`);

  const splitIndex = candles.length - FRESH_HOLDOUT_CANDLES;
  const holdoutCutoff = candles[splitIndex]?.timestamp;
  if (!holdoutCutoff) throw new Error(`${timeframe}: missing holdout cutoff timestamp`);

  const holdout = (source.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .filter((t) => new Date(t.entryTime) >= new Date(holdoutCutoff))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const frozen = holdout.filter((t) => t.direction === CANDIDATE_DIRECTION && t.session === CANDIDATE_SESSION);
  const baselineSummary = addExcursionStats(summarize(holdout), holdout, candles);
  const frozenSummary = addExcursionStats(summarize(frozen), frozen, candles);

  const report = {
    strategy: 'Strategy A',
    mode: 'RESEARCH_H2_FRESH_HOLDOUT_CONFIRMATION',
    timeframe,
    symbol: source.symbol ?? 'XAUUSD',
    warning: 'Single frozen confirmation test. No optimization or production rule change is performed by this report.',
    hypothesis: 'Frozen H2 candidate SELL + NEW_YORK qualified on the pre-holdout DEV/VAL gate and is tested once on the reserved fresh holdout.',
    methodology: {
      totalCandles: candles.length,
      freshHoldoutCandles: FRESH_HOLDOUT_CANDLES,
      splitIndex,
      holdoutFrom: holdoutCutoff,
      holdoutTo: candles[candles.length - 1]?.timestamp ?? null,
      candidate: 'SELL + NEW_YORK',
      baselineComparison: 'All eligible baseline trades in the same fresh holdout.',
      noOptimization: true,
    },
    baseline: baselineSummary,
    frozenCandidate: frozenSummary,
    comparison: {
      deltaAvgR: frozenSummary.avgR == null || baselineSummary.avgR == null ? null : frozenSummary.avgR - baselineSummary.avgR,
      deltaProfitFactor: frozenSummary.profitFactor == null || baselineSummary.profitFactor == null ? null : frozenSummary.profitFactor - baselineSummary.profitFactor,
      deltaWinRate: frozenSummary.winRate == null || baselineSummary.winRate == null ? null : frozenSummary.winRate - baselineSummary.winRate,
      deltaTotalR: frozenSummary.totalR - baselineSummary.totalR,
    },
    verdict: frozenSummary.n < 10
      ? 'INCONCLUSIVE'
      : (frozenSummary.avgR > 0 && frozenSummary.profitFactor >= 1 && frozenSummary.avgR > baselineSummary.avgR && frozenSummary.totalR > 0 ? 'CONFIRMED' : 'REJECTED'),
    conclusion: frozenSummary.n < 10
      ? 'Holdout sample is too small for the predefined minimum of 10 trades; do not promote the filter.'
      : (frozenSummary.avgR > 0 && frozenSummary.profitFactor >= 1 && frozenSummary.avgR > baselineSummary.avgR && frozenSummary.totalR > 0
        ? 'Frozen SELL + NEW_YORK remains positive and improves AvgR versus the fresh-holdout baseline. This confirms the research hypothesis for this test, but does not by itself justify changing production Strategy A without a final robustness review.'
        : 'Frozen SELL + NEW_YORK does not satisfy the fresh-holdout confirmation criteria. Reject the filter and return research to entry/trigger mechanics.'),
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: baseline n=${baselineSummary.n} avgR=${baselineSummary.avgR?.toFixed(4)} PF=${baselineSummary.profitFactor?.toFixed(4) ?? 'n/a'} | frozen SELL+NEW_YORK n=${frozenSummary.n} avgR=${frozenSummary.avgR?.toFixed(4)} PF=${frozenSummary.profitFactor?.toFixed(4) ?? 'n/a'} | verdict=${report.verdict}`);
  console.log(`  frozen totalR=${frozenSummary.totalR.toFixed(4)} winRate=${((frozenSummary.winRate ?? 0) * 100).toFixed(2)}% maxDD=${frozenSummary.maxDrawdownR.toFixed(4)}R maxCL=${frozenSummary.maxConsecutiveLosses}`);
  console.log(`Report -> ${out}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
