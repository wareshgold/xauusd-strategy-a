import { mkdir, writeFile } from 'node:fs/promises';

const apiKey = process.env.TWELVE_DATA_API_KEY;
if (!apiKey) throw new Error('Missing TWELVE_DATA_API_KEY environment variable');

const symbol = process.env.XAUUSD_SYMBOL ?? 'XAU/USD';
const outputSize = Number(process.env.XAUUSD_OUTPUTSIZE ?? '10000');
if (!Number.isInteger(outputSize) || outputSize < 1 || outputSize > 50000) {
  throw new Error('XAUUSD_OUTPUTSIZE must be an integer between 1 and 50000');
}

const root = new URL('../', import.meta.url);
const outputDir = new URL('data/historical/', root);
await mkdir(outputDir, { recursive: true });

for (const interval of ['1min', '5min']) {
  const url = new URL('https://api.twelvedata.com/time_series');
  url.searchParams.set('symbol', symbol);
  url.searchParams.set('interval', interval);
  url.searchParams.set('outputsize', String(outputSize));
  url.searchParams.set('format', 'JSON');
  url.searchParams.set('apikey', apiKey);

  console.log(`Downloading ${symbol} ${interval} (${outputSize} candles requested)...`);
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Twelve Data HTTP ${response.status} for ${interval}`);
  const payload = await response.json();
  if (payload?.status === 'error') throw new Error(`Twelve Data ${interval}: ${payload.message ?? 'request failed'}`);
  if (!Array.isArray(payload?.values) || payload.values.length === 0) throw new Error(`Twelve Data ${interval}: no candles returned`);

  const seen = new Set();
  const values = [...payload.values]
    .filter((v) => v && typeof v.datetime === 'string')
    .sort((a, b) => a.datetime.localeCompare(b.datetime))
    .filter((v) => !seen.has(v.datetime) && seen.add(v.datetime))
    .map((v) => ({
      timestamp: v.datetime,
      open: Number(v.open),
      high: Number(v.high),
      low: Number(v.low),
      close: Number(v.close),
      ...(v.volume !== undefined ? { volume: Number(v.volume) } : {})
    }));

  if (values.some((v) => [v.open, v.high, v.low, v.close].some((n) => !Number.isFinite(n)))) {
    throw new Error(`Twelve Data ${interval}: invalid OHLC value`);
  }

  const dataset = { symbol: 'XAU/USD', timeframe: interval, source: 'twelvedata', candles: values };
  const path = new URL(`xauusd-${interval}.json`, outputDir);
  await writeFile(path, JSON.stringify(dataset, null, 2) + '\n', 'utf8');
  console.log(`Saved ${values.length} candles -> ${path.pathname}`);
}
