import { readFile, writeFile } from 'node:fs/promises';

const root = new URL('../', import.meta.url);
const dataDir = new URL('data/historical/', root);
const reportDir = new URL('data/reports/', root);
await import('node:fs/promises').then(({ mkdir }) => mkdir(reportDir, { recursive: true }));

const datasets = [
  { timeframe: '1min', path: new URL('xauusd-1min.json', dataDir), expectedMinutes: 1 },
  { timeframe: '5min', path: new URL('xauusd-5min.json', dataDir), expectedMinutes: 5 }
];

function fail(message) {
  throw new Error(message);
}

function parseDataset(text, timeframe) {
  let dataset;
  try {
    dataset = JSON.parse(text);
  } catch {
    fail(`${timeframe}: invalid JSON`);
  }
  if (!dataset || !Array.isArray(dataset.candles)) fail(`${timeframe}: missing candles array`);
  if (dataset.symbol !== 'XAU/USD') fail(`${timeframe}: unexpected symbol ${dataset.symbol}`);
  if (dataset.timeframe !== timeframe) fail(`${timeframe}: unexpected timeframe ${dataset.timeframe}`);
  return dataset;
}

function audit(dataset, expectedMinutes) {
  const candles = dataset.candles;
  const timestamps = candles.map((c) => c.timestamp);
  const duplicateTimestamps = timestamps.length - new Set(timestamps).size;
  const invalidOhlc = [];
  const nonChronological = [];
  const gaps = [];
  const suspiciousGaps = [];

  for (let i = 0; i < candles.length; i += 1) {
    const c = candles[i];
    const values = [c.open, c.high, c.low, c.close];
    if (!c || typeof c.timestamp !== 'string' || values.some((n) => !Number.isFinite(n))) {
      invalidOhlc.push(i);
      continue;
    }
    if (!(c.high >= Math.max(c.open, c.close) && c.low <= Math.min(c.open, c.close) && c.high >= c.low)) {
      invalidOhlc.push(i);
    }
    if (i > 0) {
      const previous = new Date(`${candles[i - 1].timestamp.replace(' ', 'T')}Z`);
      const current = new Date(`${c.timestamp.replace(' ', 'T')}Z`);
      const diffMinutes = (current.getTime() - previous.getTime()) / 60000;
      if (!Number.isFinite(diffMinutes) || diffMinutes <= 0) nonChronological.push(i);
      if (diffMinutes > expectedMinutes) {
        const gap = {
          from: candles[i - 1].timestamp,
          to: c.timestamp,
          minutes: diffMinutes,
          missingBars: Math.max(0, Math.round(diffMinutes / expectedMinutes) - 1)
        };
        gaps.push(gap);
        const fromDay = previous.getUTCDay();
        const toDay = current.getUTCDay();
        const weekendLike = fromDay === 5 || fromDay === 6 || fromDay === 0 || toDay === 6 || toDay === 0 || (fromDay === 5 && toDay === 1);
        if (!weekendLike) suspiciousGaps.push(gap);
      }
    }
  }

  const first = candles[0]?.timestamp ?? null;
  const last = candles.at(-1)?.timestamp ?? null;
  const spanMinutes = first && last
    ? (new Date(`${last.replace(' ', 'T')}Z`).getTime() - new Date(`${first.replace(' ', 'T')}Z`).getTime()) / 60000
    : 0;

  return {
    symbol: dataset.symbol,
    timeframe: dataset.timeframe,
    source: dataset.source,
    timezone: dataset.timezone,
    candleCount: candles.length,
    firstTimestamp: first,
    lastTimestamp: last,
    spanMinutes,
    duplicateTimestamps,
    invalidOhlcCount: invalidOhlc.length,
    nonChronologicalCount: nonChronological.length,
    gapCount: gaps.length,
    suspiciousGapCount: suspiciousGaps.length,
    largestGapMinutes: gaps.reduce((max, gap) => Math.max(max, gap.minutes), 0),
    suspiciousGaps: suspiciousGaps.slice(0, 20),
    pass: duplicateTimestamps === 0 && invalidOhlc.length === 0 && nonChronological.length === 0
  };
}

const results = [];
for (const spec of datasets) {
  const text = await readFile(spec.path, 'utf8');
  const dataset = parseDataset(text, spec.timeframe);
  results.push(audit(dataset, spec.expectedMinutes));
}

const report = {
  generatedAt: new Date().toISOString(),
  status: results.every((r) => r.pass) ? 'PASS' : 'FAIL',
  datasets: results
};

await writeFile(new URL('dataset-audit.json', reportDir), JSON.stringify(report, null, 2) + '\n', 'utf8');

for (const result of results) {
  console.log(`${result.timeframe}: ${result.pass ? 'PASS' : 'FAIL'} | candles=${result.candleCount} | ${result.firstTimestamp} -> ${result.lastTimestamp} | duplicates=${result.duplicateTimestamps} | invalidOHLC=${result.invalidOhlcCount} | nonChronological=${result.nonChronologicalCount} | gaps=${result.gapCount} | suspiciousGaps=${result.suspiciousGapCount}`);
}
console.log(`Report -> ${new URL('dataset-audit.json', reportDir).pathname}`);

if (report.status !== 'PASS') process.exitCode = 1;
