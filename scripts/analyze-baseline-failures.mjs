import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-failure-analysis');

function percentile(values, p) {
  if (!values.length) return null;
  const a = [...values].sort((x, y) => x - y);
  const i = (a.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (i - lo);
}

function summarize(report) {
  const trades = report.trades ?? [];
  const closed = trades.filter(t => t.rMultiple !== null && Number.isFinite(t.rMultiple));
  const wins = closed.filter(t => t.rMultiple > 0);
  const losses = closed.filter(t => t.rMultiple < 0);
  const rs = closed.map(t => t.rMultiple);
  const risk = closed.map(t => t.riskDistance).filter(Number.isFinite);
  const outlierCut = percentile(rs, 0.99);
  const robust = outlierCut === null ? [] : closed.filter(t => t.rMultiple <= outlierCut);
  const grossWin = wins.reduce((s,t) => s + t.rMultiple, 0);
  const grossLoss = Math.abs(losses.reduce((s,t) => s + t.rMultiple, 0));
  const robustWins = robust.filter(t => t.rMultiple > 0);
  const robustLosses = robust.filter(t => t.rMultiple < 0);
  const robustGrossLoss = Math.abs(robustLosses.reduce((s,t) => s + t.rMultiple, 0));
  const byResult = Object.fromEntries(['TP1','TP2','SL','AMBIGUOUS','OPEN'].map(k => [k, trades.filter(t => t.result === k).length]));
  const byDirection = Object.fromEntries(['BUY','SELL'].map(k => {
    const x = closed.filter(t => t.direction === k);
    return [k, { trades:x.length, winRate:x.length ? x.filter(t => t.rMultiple > 0).length / x.length : 0, averageR:x.length ? x.reduce((s,t)=>s+t.rMultiple,0)/x.length : 0 }];
  }));
  return {
    timeframe: report.timeframe,
    candles: report.candles,
    source: report.source,
    baselineMetrics: report.metrics,
    resultCounts: byResult,
    direction: byDirection,
    rDistribution: { min:Math.min(...rs), p50:percentile(rs,.5), p90:percentile(rs,.9), p95:percentile(rs,.95), p99:outlierCut, max:Math.max(...rs) },
    riskDistance: { min:Math.min(...risk), p50:percentile(risk,.5), p05:percentile(risk,.05) },
    extremeWinners: [...closed].sort((a,b)=>b.rMultiple-a.rMultiple).slice(0,10),
    extremeLosses: [...closed].sort((a,b)=>a.rMultiple-b.rMultiple).slice(0,10),
    robustWithoutTop1PercentR: {
      excludedTrades: closed.length - robust.length,
      trades: robust.length,
      winRate: robust.length ? robustWins.length / robust.length : 0,
      averageR: robust.length ? robust.reduce((s,t)=>s+t.rMultiple,0)/robust.length : 0,
      profitFactor: robustGrossLoss ? robustWins.reduce((s,t)=>s+t.rMultiple,0)/robustGrossLoss : null,
    },
    researchNote: 'Descriptive diagnostic only. No strategy parameters are changed and no outlier rule is proposed as a trading rule.'
  };
}

await mkdir(OUTPUT, { recursive:true });
for (const timeframe of ['1min','5min']) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const analysis = summarize(report);
  await writeFile(resolve(OUTPUT, `${timeframe}.json`), JSON.stringify(analysis, null, 2));
  console.log(`${timeframe}: trades=${analysis.baselineMetrics.trades} maxR=${analysis.rDistribution.max.toFixed(4)} p99=${analysis.rDistribution.p99.toFixed(4)} robustPF=${analysis.robustWithoutTop1PercentR.profitFactor?.toFixed(4) ?? 'n/a'} robustAvgR=${analysis.robustWithoutTop1PercentR.averageR.toFixed(4)}`);
}
