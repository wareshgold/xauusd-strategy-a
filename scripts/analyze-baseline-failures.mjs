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

function stats(trades) {
  const closed = trades.filter(t => Number.isFinite(t.rMultiple));
  const wins = closed.filter(t => t.rMultiple > 0), losses = closed.filter(t => t.rMultiple < 0);
  const gw = wins.reduce((s, t) => s + t.rMultiple, 0), gl = Math.abs(losses.reduce((s, t) => s + t.rMultiple, 0));
  return { trades: closed.length, wins: wins.length, losses: losses.length, winRate: closed.length ? wins.length / closed.length : 0, averageR: closed.length ? closed.reduce((s, t) => s + t.rMultiple, 0) / closed.length : 0, profitFactor: gl ? gw / gl : null };
}

function group(trades, keyFn) {
  const m = new Map();
  for (const t of trades) { const k = keyFn(t); if (!m.has(k)) m.set(k, []); m.get(k).push(t); }
  return Object.fromEntries([...m].map(([k, v]) => [k, stats(v)]));
}

function sessionOf(t) {
  const h = Number(String(t.entryTime).slice(11, 13));
  return h >= 7 && h < 13 ? 'LONDON_ONLY' : h >= 13 && h < 16 ? 'OVERLAP' : h >= 16 && h < 22 ? 'NEW_YORK_ONLY' : 'OUTSIDE';
}

function intersectionAnalysis(closed) {
  const directions = [...new Set(closed.map(t => t.direction))].sort();
  const sessions = ['LONDON_ONLY', 'OVERLAP', 'NEW_YORK_ONLY', 'OUTSIDE'];
  const out = {};
  for (const direction of directions) {
    for (const session of sessions) {
      const subset = closed.filter(t => t.direction === direction && sessionOf(t) === session);
      if (!subset.length) continue;
      const p99 = percentile(subset.map(t => t.rMultiple), 0.99);
      const robust = subset.filter(t => t.rMultiple <= p99);
      out[`${direction}__${session}`] = {
        raw: stats(subset),
        robustWithoutTop1PercentR: { excludedTrades: subset.length - robust.length, ...stats(robust) },
        p99R: p99,
        minRisk: Math.min(...subset.map(t => t.riskDistance).filter(Number.isFinite)),
        maxR: Math.max(...subset.map(t => t.rMultiple))
      };
    }
  }
  return out;
}

function analyze(report) {
  const trades = report.trades ?? [];
  const closed = trades.filter(t => Number.isFinite(t.rMultiple));
  const rs = closed.map(t => t.rMultiple);
  const risk = closed.map(t => t.riskDistance).filter(Number.isFinite);
  const p99 = percentile(rs, .99);
  const robust = closed.filter(t => t.rMultiple <= p99);
  return {
    timeframe: report.timeframe,
    candles: report.candles,
    baselineMetrics: report.metrics,
    resultCounts: Object.fromEntries(['TP1', 'TP2', 'SL', 'AMBIGUOUS', 'OPEN'].map(k => [k, trades.filter(t => t.result === k).length])),
    byDirection: group(closed, t => t.direction),
    bySession: group(closed, sessionOf),
    directionSessionIntersection: intersectionAnalysis(closed),
    rDistribution: { min: Math.min(...rs), p50: percentile(rs, .5), p90: percentile(rs, .9), p95: percentile(rs, .95), p99, max: Math.max(...rs) },
    riskDistance: { min: Math.min(...risk), p01: percentile(risk, .01), p05: percentile(risk, .05), p50: percentile(risk, .5) },
    extremeWinners: [...closed].sort((a, b) => b.rMultiple - a.rMultiple).slice(0, 15),
    extremeLosses: [...closed].sort((a, b) => a.rMultiple - b.rMultiple).slice(0, 10),
    robustWithoutTop1PercentR: { excludedTrades: closed.length - robust.length, ...stats(robust) },
    researchNote: 'Diagnostic only; no parameters or trading rules changed. Direction-session intersections are descriptive hypotheses, not optimized trading rules.'
  };
}

await mkdir(OUTPUT, { recursive: true });
for (const timeframe of ['1min', '5min']) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const a = analyze(report);
  await writeFile(resolve(OUTPUT, `${timeframe}.json`), JSON.stringify(a, null, 2));
  console.log(`${timeframe}: trades=${a.baselineMetrics.trades} PF=${a.baselineMetrics.profitFactor?.toFixed(4)} robustPF=${a.robustWithoutTop1PercentR.profitFactor?.toFixed(4) ?? 'n/a'} medianR=${a.rDistribution.p50.toFixed(4)} minRisk=${a.riskDistance.min.toFixed(5)}`);
  for (const [key, value] of Object.entries(a.directionSessionIntersection)) {
    console.log(`  ${key}: n=${value.raw.trades} PF=${value.raw.profitFactor?.toFixed(4) ?? 'n/a'} avgR=${value.raw.averageR.toFixed(4)} robustPF=${value.robustWithoutTop1PercentR.profitFactor?.toFixed(4) ?? 'n/a'} robustAvgR=${value.robustWithoutTop1PercentR.averageR.toFixed(4)} excluded=${value.robustWithoutTop1PercentR.excludedTrades}`);
  }
}
