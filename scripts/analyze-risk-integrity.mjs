import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-risk-integrity');
const BUCKETS = [0.01, 0.05, 0.10, 0.20, 0.50];

function percentile(values, p) {
  if (!values.length) return null;
  const a = [...values].sort((x, y) => x - y);
  const i = (a.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (i - lo);
}

function stats(trades) {
  const closed = trades.filter(t => Number.isFinite(t.rMultiple));
  const wins = closed.filter(t => t.rMultiple > 0);
  const losses = closed.filter(t => t.rMultiple < 0);
  const grossWin = wins.reduce((s, t) => s + t.rMultiple, 0);
  const grossLoss = Math.abs(losses.reduce((s, t) => s + t.rMultiple, 0));
  return {
    trades: closed.length,
    wins: wins.length,
    losses: losses.length,
    winRate: closed.length ? wins.length / closed.length : 0,
    averageR: closed.length ? closed.reduce((s, t) => s + t.rMultiple, 0) / closed.length : 0,
    profitFactor: grossLoss ? grossWin / grossLoss : null,
  };
}

function riskRows(trades) {
  const closed = trades.filter(t => Number.isFinite(t.rMultiple) && Number.isFinite(t.riskDistance) && t.riskDistance > 0);
  const risks = closed.map(t => t.riskDistance);
  return BUCKETS.map(p => {
    const threshold = percentile(risks, p);
    const excluded = closed.filter(t => t.riskDistance <= threshold);
    const retained = closed.filter(t => t.riskDistance > threshold);
    return {
      percentile: p,
      thresholdRiskDistance: threshold,
      excluded: stats(excluded),
      retained: stats(retained),
      excludedR: excluded.reduce((s, t) => s + t.rMultiple, 0),
      retainedR: retained.reduce((s, t) => s + t.rMultiple, 0),
    };
  });
}

function analyze(report) {
  const trades = report.trades ?? [];
  const closed = trades.filter(t => Number.isFinite(t.rMultiple) && Number.isFinite(t.riskDistance) && t.riskDistance > 0);
  const risks = closed.map(t => t.riskDistance);
  const byRiskAscending = [...closed].sort((a, b) => a.riskDistance - b.riskDistance);
  const tiny = byRiskAscending.slice(0, Math.min(20, byRiskAscending.length));
  return {
    strategy: report.strategy,
    timeframe: report.timeframe,
    candles: report.candles,
    baselineMetrics: report.metrics,
    riskDistribution: {
      min: Math.min(...risks),
      p01: percentile(risks, .01),
      p05: percentile(risks, .05),
      p10: percentile(risks, .10),
      p25: percentile(risks, .25),
      p50: percentile(risks, .50),
      p75: percentile(risks, .75),
      p90: percentile(risks, .90),
      p95: percentile(risks, .95),
      max: Math.max(...risks),
    },
    byLowRiskPercentile: riskRows(trades),
    smallestRiskTrades: tiny,
    diagnosticOnly: true,
    conclusionRule: 'Do not change Strategy A parameters from this report alone. A minimum-risk rule is justified only if it improves out-of-sample performance after a pre-registered threshold is selected from training data.',
  };
}

await mkdir(OUTPUT, { recursive: true });
for (const timeframe of ['1min', '5min']) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const analysis = analyze(report);
  await writeFile(resolve(OUTPUT, `${timeframe}.json`), JSON.stringify(analysis, null, 2));
  console.log(`${timeframe}: minRisk=${analysis.riskDistribution.min.toFixed(5)} p01=${analysis.riskDistribution.p01.toFixed(5)} p05=${analysis.riskDistribution.p05.toFixed(5)} p10=${analysis.riskDistribution.p10.toFixed(5)}`);
  for (const row of analysis.byLowRiskPercentile) {
    console.log(`  <=p${row.percentile * 100}: threshold=${row.thresholdRiskDistance.toFixed(5)} excluded=${row.excluded.trades} PF=${row.excluded.profitFactor?.toFixed(4) ?? 'n/a'} avgR=${row.excluded.averageR.toFixed(4)} | retainedPF=${row.retained.profitFactor?.toFixed(4) ?? 'n/a'} retainedAvgR=${row.retained.averageR.toFixed(4)}`);
  }
}
