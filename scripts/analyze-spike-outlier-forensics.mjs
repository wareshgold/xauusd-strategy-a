import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-spike-outlier-forensics');
const LOOKBACK = 60;
const TOP_N = 25;

function finite(x) { return Number.isFinite(x); }
function parseTime(value) {
  const d = new Date(value.includes('T') ? value : value.replace(' ', 'T') + 'Z');
  return Number.isNaN(d.getTime()) ? null : d;
}
function median(values) {
  const a = values.filter(finite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
function classify(c) {
  const range = c.high - c.low;
  const body = Math.abs(c.close - c.open);
  const upperWick = c.high - Math.max(c.open, c.close);
  const lowerWick = Math.min(c.open, c.close) - c.low;
  const bodyShare = range > 0 ? body / range : 0;
  const upperShare = range > 0 ? upperWick / range : 0;
  const lowerShare = range > 0 ? lowerWick / range : 0;
  const parts = [];
  if (bodyShare >= 0.7) parts.push('LARGE_BODY');
  if (upperShare >= 0.35) parts.push('UPPER_WICK');
  if (lowerShare >= 0.35) parts.push('LOWER_WICK');
  return { range, body, upperWick, lowerWick, bodyShare, upperShare, lowerShare, morphology: parts.length ? parts : ['MIXED'] };
}

async function run(timeframe) {
  const data = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
  const candles = data.candles;
  const rows = [];
  const tr = candles.map((c, i) => {
    const prevClose = i > 0 ? candles[i - 1].close : c.open;
    return Math.max(c.high - c.low, Math.abs(c.high - prevClose), Math.abs(c.low - prevClose));
  });
  for (let i = LOOKBACK; i < candles.length; i++) {
    const c = candles[i], prev = candles[i - 1];
    const base = median(tr.slice(i - LOOKBACK, i));
    if (!base || base <= 0) continue;
    const score = tr[i] / base;
    const d = parseTime(c.timestamp);
    const m = classify(c);
    const gapPct = prev?.close ? Math.abs(c.open / prev.close - 1) : null;
    rows.push({
      rank: null, index: i, timestamp: c.timestamp, utcHour: d?.getUTCHours() ?? null, utcMinute: d?.getUTCMinutes() ?? null,
      open: c.open, high: c.high, low: c.low, close: c.close, previousClose: prev?.close ?? null,
      trueRange: tr[i], rollingMedianTrueRange: base, spikeScore: score,
      gapAbsPct: gapPct, ...m,
      direction: c.close > c.open ? 'UP' : c.close < c.open ? 'DOWN' : 'FLAT',
      barsBefore: candles.slice(Math.max(0, i - 3), i).map(x => ({ timestamp: x.timestamp, open: x.open, high: x.high, low: x.low, close: x.close })),
      barsAfter: candles.slice(i + 1, Math.min(candles.length, i + 4)).map(x => ({ timestamp: x.timestamp, open: x.open, high: x.high, low: x.low, close: x.close }))
    });
  }
  rows.sort((a, b) => b.spikeScore - a.spikeScore);
  rows.slice(0, TOP_N).forEach((r, i) => { r.rank = i + 1; });
  const top = rows.slice(0, TOP_N);
  const counts = top.reduce((acc, r) => { for (const m of r.morphology) acc[m] = (acc[m] ?? 0) + 1; return acc; }, {});
  const report = {
    generatedAt: new Date().toISOString(), timeframe, symbol: data.symbol, source: data.source,
    methodology: 'Standard True Range using previous candle close; rolling baseline is median TR over the preceding 60 bars. This is forensic only; no observations are removed and no strategy threshold is changed.',
    summary: { candles: candles.length, topN: TOP_N, maxSpikeScore: top[0]?.spikeScore ?? null, top25MedianScore: median(top.map(r => r.spikeScore)), morphologyCounts: counts },
    outliers: top
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: max=${top[0]?.spikeScore?.toFixed(4) ?? 'n/a'} top25Median=${median(top.map(r => r.spikeScore))?.toFixed(4) ?? 'n/a'} morphology=${JSON.stringify(counts)}`);
  for (const r of top.slice(0, 10)) console.log(`#${r.rank} ${r.timestamp} score=${r.spikeScore.toFixed(2)} TR=${r.trueRange.toFixed(4)} gap=${r.gapAbsPct == null ? 'n/a' : (r.gapAbsPct * 100).toFixed(3) + '%'} bodyShare=${r.bodyShare.toFixed(2)} upper=${r.upperShare.toFixed(2)} lower=${r.lowerShare.toFixed(2)} ${r.morphology.join('+')}`);
  console.log(`Report -> ${out}`);
}
for (const tf of ['1min', '5min']) await run(tf);
