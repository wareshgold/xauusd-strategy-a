import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-spike-data-integrity');
const TIMEFRAMES = [
  { name: '1min', minutes: 1 },
  { name: '5min', minutes: 5 }
];
const LOOKBACK = 60;

function finite(n) { return Number.isFinite(n); }
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
function quantile(values, q) {
  const a = values.filter(finite).sort((x, y) => x - y);
  if (!a.length) return null;
  const p = (a.length - 1) * q;
  const lo = Math.floor(p), hi = Math.ceil(p);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (p - lo);
}

function audit(candles, expectedMinutes) {
  const issues = [];
  const trs = [];
  const scores = [];
  let duplicateTimestamps = 0;
  let nonChronological = 0;
  let invalidOhlc = 0;
  let gaps = 0;
  let suspiciousGaps = 0;
  let largestGapMinutes = 0;
  let maxAbsReturn = 0;
  let maxTr = 0;

  for (let i = 0; i < candles.length; i++) {
    const c = candles[i];
    if (!c || ![c.open, c.high, c.low, c.close].every(finite) || !parseTime(c.timestamp)) {
      invalidOhlc++;
      if (issues.length < 20) issues.push({ type: 'invalid_ohlc_or_timestamp', index: i });
      trs.push(null);
      continue;
    }
    if (!(c.high >= Math.max(c.open, c.close) && c.low <= Math.min(c.open, c.close) && c.high >= c.low)) {
      invalidOhlc++;
      if (issues.length < 20) issues.push({ type: 'invalid_ohlc', index: i, candle: c });
    }
    if (i > 0) {
      const prev = candles[i - 1];
      const prevD = parseTime(prev.timestamp), d = parseTime(c.timestamp);
      const diff = (d.getTime() - prevD.getTime()) / 60000;
      if (diff <= 0 || !finite(diff)) nonChronological++;
      if (diff > expectedMinutes) {
        gaps++;
        largestGapMinutes = Math.max(largestGapMinutes, diff);
        const fromDay = prevD.getUTCDay(), toDay = d.getUTCDay();
        const weekendLike = fromDay === 5 || fromDay === 6 || fromDay === 0 || toDay === 6 || toDay === 0 || (fromDay === 5 && toDay === 1);
        if (!weekendLike) suspiciousGaps++;
      }
      const prevClose = prev.close;
      if (finite(prevClose) && prevClose !== 0) maxAbsReturn = Math.max(maxAbsReturn, Math.abs(c.open / prevClose - 1));
    }
    const prevClose = i > 0 && finite(candles[i - 1]?.close) ? candles[i - 1].close : c.open;
    const tr = Math.max(c.high - c.low, Math.abs(c.high - prevClose), Math.abs(c.low - prevClose));
    trs.push(tr);
    maxTr = Math.max(maxTr, tr);
    if (i >= LOOKBACK) {
      const base = median(trs.slice(i - LOOKBACK, i));
      scores.push(base && base > 0 ? tr / base : null);
    } else scores.push(null);
  }

  const usableScores = scores.filter(finite);
  const p90 = quantile(usableScores, 0.90);
  const p95 = quantile(usableScores, 0.95);
  const p999 = quantile(usableScores, 0.999);
  const top = [...usableScores].sort((a, b) => b - a).slice(0, 20);

  return {
    candles: candles.length,
    duplicateTimestamps: candles.length - new Set(candles.map(c => c.timestamp)).size,
    invalidOhlc,
    nonChronological,
    gaps,
    suspiciousGaps,
    largestGapMinutes,
    maxAbsOpenToPreviousCloseReturn: maxAbsReturn,
    maxTrueRange: maxTr,
    correctedTrueRangeScore: {
      lookbackBars: LOOKBACK,
      p50: quantile(usableScores, 0.50),
      p90,
      p95,
      p999,
      max: top[0] ?? null,
      top20: top
    },
    issueSamples: issues,
    pass: invalidOhlc === 0 && nonChronological === 0 && (candles.length - new Set(candles.map(c => c.timestamp)).size) === 0 && suspiciousGaps === 0
  };
}

await mkdir(REPORT_DIR, { recursive: true });
const results = [];
for (const tf of TIMEFRAMES) {
  const path = resolve(ROOT, `data/historical/xauusd-${tf.name}.json`);
  const dataset = JSON.parse(await readFile(path, 'utf8'));
  results.push({ timeframe: tf.name, symbol: dataset.symbol, source: dataset.source, first: dataset.candles[0]?.timestamp ?? null, last: dataset.candles.at(-1)?.timestamp ?? null, ...audit(dataset.candles, tf.minutes) });
}
const report = {
  generatedAt: new Date().toISOString(),
  methodology: 'Integrity audit plus corrected standard True Range using previous candle close. No strategy threshold is changed.',
  status: results.every(r => r.pass) ? 'PASS' : 'FAIL',
  results
};
await writeFile(resolve(REPORT_DIR, 'integrity.json'), JSON.stringify(report, null, 2) + '\n');
for (const r of results) console.log(`${r.timeframe}: ${r.pass ? 'PASS' : 'FAIL'} candles=${r.candles} duplicates=${r.duplicateTimestamps} invalidOHLC=${r.invalidOhlc} nonChronological=${r.nonChronological} suspiciousGaps=${r.suspiciousGaps} correctedP90=${r.correctedTrueRangeScore.p90?.toFixed(4) ?? 'n/a'} correctedMax=${r.correctedTrueRangeScore.max?.toFixed(4) ?? 'n/a'}`);
console.log(`Report -> ${resolve(REPORT_DIR, 'integrity.json')}`);
