import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-spike-conditional-edge-reopen-sensitivity');
const TIMEFRAMES = [
  { name: '1min', minutes: 1 },
  { name: '5min', minutes: 5 },
];
const LOOKBACK = 60;
const REOPEN_EXCLUSION_MINUTES = [0, 5, 15, 30, 45, 60];
const SPIKE_QUANTILE = 0.90;
const SPIKE_LOOKBACK_BARS = 1;

function median(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
function quantile(values, p) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const x = (a.length - 1) * p, lo = Math.floor(x), hi = Math.ceil(x);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (x - lo);
}
function mean(values) {
  const a = values.filter(Number.isFinite);
  return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
}
function parseTime(value) {
  const d = new Date(value.includes('T') ? value : value.replace(' ', 'T') + 'Z');
  return Number.isNaN(d.getTime()) ? null : d;
}
function trueRange(c, prevClose) {
  return Math.max(c.high - c.low, Math.abs(c.high - prevClose), Math.abs(c.low - prevClose));
}
function isReopenAffected(timestamp, minutes) {
  const d = parseTime(timestamp);
  if (!d || d.getUTCDay() !== 0 || d.getUTCHours() !== 22) return false;
  return true;
}
function minutesSinceReopen(timestamp) {
  const d = parseTime(timestamp);
  if (!d || d.getUTCDay() !== 0) return null;
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  return m - 22 * 60;
}
function summarize(trades) {
  const usable = trades.filter(t => Number.isFinite(t.rMultiple));
  const grossWin = usable.filter(t => t.rMultiple > 0).reduce((s, t) => s + t.rMultiple, 0);
  const grossLoss = usable.filter(t => t.rMultiple < 0).reduce((s, t) => s + Math.abs(t.rMultiple), 0);
  return {
    n: usable.length,
    wins: usable.filter(t => t.rMultiple > 0).length,
    losses: usable.filter(t => t.rMultiple < 0).length,
    winRate: usable.length ? usable.filter(t => t.rMultiple > 0).length / usable.length : null,
    avgR: usable.length ? mean(usable.map(t => t.rMultiple)) : null,
    totalR: usable.reduce((s, t) => s + t.rMultiple, 0),
    profitFactor: grossLoss > 0 ? grossWin / grossLoss : null,
  };
}
function maxDrawdown(trades) {
  let equity = 0, peak = 0, dd = 0;
  for (const t of trades.filter(x => Number.isFinite(x.rMultiple))) {
    equity += t.rMultiple;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
  }
  return dd;
}
function isExcludedByReopen(candleTimestamp, exclusionMinutes) {
  if (exclusionMinutes === 0) return false;
  const d = parseTime(candleTimestamp);
  if (!d || d.getUTCDay() !== 0) return false;
  const delta = d.getUTCHours() * 60 + d.getUTCMinutes() - 22 * 60;
  return delta >= 0 && delta < exclusionMinutes;
}

async function run(tf) {
  const candles = (await readFile(resolve(ROOT, `data/historical/xauusd-${tf.name}.json`), 'utf8'));
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${tf.name}.json`), 'utf8'));
  const dataset = JSON.parse(candles).candles;

  const tr = dataset.map((c, i) => i > 0 ? trueRange(c, dataset[i - 1].close) : null);
  const normalized = dataset.map((_, i) => {
    if (i < LOOKBACK || !Number.isFinite(tr[i])) return null;
    const base = median(tr.slice(i - LOOKBACK, i));
    return base > 0 ? tr[i] / base : null;
  });

  const results = {};
  for (const exclusionMinutes of REOPEN_EXCLUSION_MINUTES) {
    const eligible = [];
    for (let i = LOOKBACK; i < dataset.length; i++) {
      if (!Number.isFinite(normalized[i])) continue;
      if (isExcludedByReopen(dataset[i].timestamp, exclusionMinutes)) continue;
      eligible.push(i);
    }
    const spikeCut = quantile(eligible.map(i => normalized[i]), SPIKE_QUANTILE);
    const spikeSet = new Set(eligible.filter(i => normalized[i] >= spikeCut));
    const trades = baseline.trades.filter(t => Number.isInteger(t.entryIndex) && Number.isFinite(t.rMultiple));
    const tagged = trades.map(t => {
      const i = t.entryIndex;
      const entryExcluded = i >= 0 && i < dataset.length ? isExcludedByReopen(dataset[i].timestamp, exclusionMinutes) : false;
      const priorSpike = !entryExcluded && spikeSet.has(i - SPIKE_LOOKBACK_BARS);
      const sameBarSpike = !entryExcluded && spikeSet.has(i);
      return { ...t, entryExcluded, priorSpike, sameBarSpike };
    });
    const eligibleTrades = tagged.filter(t => !t.entryExcluded);
    const priorSpikeTrades = eligibleTrades.filter(t => t.priorSpike);
    const sameBarSpikeTrades = eligibleTrades.filter(t => t.sameBarSpike);
    const nonSpikeTrades = eligibleTrades.filter(t => !t.priorSpike && !t.sameBarSpike);
    const all = summarize(eligibleTrades);
    const spike = summarize(priorSpikeTrades);
    const same = summarize(sameBarSpikeTrades);
    const non = summarize(nonSpikeTrades);
    results[String(exclusionMinutes)] = {
      exclusionMinutes,
      eligibleBars: eligible.length,
      spikeCut,
      spikeBars: spikeSet.size,
      tradesExcludedByReopen: tagged.filter(t => t.entryExcluded).length,
      tradeUniverse: all,
      priorBarSpike: { ...spike, maxDrawdownR: maxDrawdown(priorSpikeTrades) },
      sameBarSpike: { ...same, maxDrawdownR: maxDrawdown(sameBarSpikeTrades) },
      nonSpike: { ...non, maxDrawdownR: maxDrawdown(nonSpikeTrades) },
      incrementalAvgR_priorSpikeVsNon: spike.avgR != null && non.avgR != null ? spike.avgR - non.avgR : null,
      incrementalPF_priorSpikeVsNon: spike.profitFactor != null && non.profitFactor != null ? spike.profitFactor - non.profitFactor : null,
      incrementalAvgR_sameBarVsNon: same.avgR != null && non.avgR != null ? same.avgR - non.avgR : null,
    };
  }

  const report = {
    generatedAt: new Date().toISOString(),
    strategy: baseline.strategy,
    timeframe: tf.name,
    data: { candles: dataset.length, from: dataset[0]?.timestamp, to: dataset.at(-1)?.timestamp, source: baseline.source },
    methodology: {
      trueRange: 'max(high-low, abs(high-previousClose), abs(low-previousClose))',
      normalization: `TR / median(previous ${LOOKBACK} bars TR)`,
      spikeDefinition: 'Top 10% normalized TR within each reopen-exclusion sensitivity population; exploratory only.',
      reopenEvent: 'Sunday 22:00 UTC',
      sensitivityWindowsMinutes: REOPEN_EXCLUSION_MINUTES,
      tradeTag: 'priorBarSpike = spike on the immediately preceding bar; sameBarSpike = spike on entry bar.',
      productionImpact: 'None. This is diagnostic; no strategy rule or threshold is changed.',
      multipleTestingWarning: 'The P90 cutoff is recomputed per sensitivity window for descriptive comparability; no window is selected as production from this report.'
    },
    baselineReference: { trades: baseline.metrics?.trades, averageR: baseline.metrics?.averageR, profitFactor: baseline.metrics?.profitFactor },
    results,
    decisionGate: {
      requirement: 'A spike-conditioned edge must beat matched non-spike baseline and survive reopen-window sensitivity before any strategy rule is considered.',
      status: 'RESEARCH_ONLY'
    }
  };
  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf.name}.json`);
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(`\n${tf.name}: baselineTrades=${baseline.metrics?.trades}`);
  for (const k of REOPEN_EXCLUSION_MINUTES) {
    const r = results[String(k)];
    console.log(`${k}m reopen-excl: spikeCut=${r.spikeCut?.toFixed(4)} eligibleTrades=${r.tradeUniverse.n} excludedTrades=${r.tradesExcludedByReopen} priorSpikeN=${r.priorBarSpike.n} priorAvgR=${r.priorBarSpike.avgR?.toFixed(4) ?? 'n/a'} priorPF=${r.priorBarSpike.profitFactor?.toFixed(4) ?? 'n/a'} nonSpikeN=${r.nonSpike.n} nonAvgR=${r.nonSpike.avgR?.toFixed(4) ?? 'n/a'} nonPF=${r.nonSpike.profitFactor?.toFixed(4) ?? 'n/a'} deltaR=${r.incrementalAvgR_priorSpikeVsNon?.toFixed(4) ?? 'n/a'}`);
  }
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
