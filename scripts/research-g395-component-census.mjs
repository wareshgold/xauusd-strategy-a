import fs from 'node:fs';

const input = process.argv[2] ?? 'data/historical/xauusd-5min.json';
const output = process.argv[3] ?? 'data/reports/g395-component-census.json';
const raw = JSON.parse(fs.readFileSync(input, 'utf8'));
const candles = raw.candles;
if (!Array.isArray(candles) || candles.length < 3) throw new Error('snapshot must contain at least 3 candles');

const DEV_START = '2026-03-17T15:15:00Z';
const DEV_END = '2026-06-30T23:59:59Z';
const inDev = (ts) => ts >= DEV_START && ts <= DEV_END;

const counters = {
  'PG-H01': 0, 'PG-H02': 0, 'PG-H03': 0, 'PG-H04': 0,
  'ABCD-H01': 0, 'ABCD-H02': 0, 'ABCD-H03': 0,
  'EN-H01': 0, 'EN-H02': 0, 'EN-H03': 0,
  'SL-H01': 0, 'SL-H02': 0,
  'TP-H01': 0, 'TP-H04': 0
};

const bodyHigh = (b) => Math.max(b.open, b.close);
const bodyLow = (b) => Math.min(b.open, b.close);
const observations = [];
let candlesEvaluated = 0;

for (let i = 2; i < candles.length; i += 1) {
  const b0 = candles[i - 2];
  const b1 = candles[i - 1];
  const b2 = candles[i];
  const timestamp = b2.datetime ?? b2.timestamp;
  if (!inDev(timestamp)) continue;
  candlesEvaluated++;

  const pg01 = b2.low > b0.high;
  const pg02 = b0.close > b0.open && b1.close > b1.open && pg01;
  const pg03 = pg01;
  const pg04 = pg01 && b1.low > b0.low;
  const ab01 = b1.high - b0.low;
  const ab02 = bodyHigh(b1) - bodyLow(b0);
  const ab03 = b1.close - b0.close;
  const en01 = b0.low;
  const en02 = b1.low;
  const en03 = (b0.low + b0.high) / 2;
  const sl01 = b0.low;
  const sl02 = bodyLow(b0);
  const tp01 = b2.close + ab01;
  const tp04 = b2.close + (b2.close - b0.low);

  if (pg01) counters['PG-H01']++;
  if (pg02) counters['PG-H02']++;
  if (pg03) counters['PG-H03']++;
  if (pg04) counters['PG-H04']++;
  if (ab01 !== 0) counters['ABCD-H01']++;
  if (ab02 !== 0) counters['ABCD-H02']++;
  if (ab03 !== 0) counters['ABCD-H03']++;
  if (en01 !== 0) counters['EN-H01']++;
  if (en02 !== 0) counters['EN-H02']++;
  if (en03 !== 0) counters['EN-H03']++;
  if (sl01 !== 0) counters['SL-H01']++;
  if (sl02 !== 0) counters['SL-H02']++;
  if (tp01 !== 0) counters['TP-H01']++;
  if (tp04 !== 0) counters['TP-H04']++;

  if (pg01) observations.push({ timestamp, pgH01: pg01, pgH02: pg02, pgH04: pg04 });
}

const total = Object.values(counters).reduce((a, b) => a + b, 0);
const result = {
  gate: 'RESEARCH-ONLY',
  canonical: false,
  dataset: { symbol: raw.symbol, source: raw.source, timeframe: raw.timeframe, timezone: raw.timezone },
  split: { name: 'DEV', start: DEV_START, end: DEV_END },
  candlesEvaluated,
  componentCounts: counters,
  pgapSample: observations.slice(0, 20),
  note: 'Counts are component/counterfactual observations only. They do not constitute Strategy A trades, profitability, canonical geometry, or promotion evidence.'
};
fs.mkdirSync(new URL('../data/reports/', import.meta.url), { recursive: true });
fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ output, candlesEvaluated, totalComponentObservations: total, canonical: false }));
