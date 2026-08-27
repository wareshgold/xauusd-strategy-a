import { mkdir, writeFile } from 'node:fs/promises';

const apiKey = process.env.TWELVE_DATA_API_KEY;
if (!apiKey) throw new Error('Missing TWELVE_DATA_API_KEY environment variable');

const symbol = process.env.XAUUSD_SYMBOL ?? 'XAU/USD';
const requestedSize = Number(process.env.XAUUSD_OUTPUTSIZE ?? '10000');
const perRequest = Math.min(Number(process.env.XAUUSD_CHUNK_SIZE ?? '5000'), 5000);
const timezone = process.env.XAUUSD_TIMEZONE ?? 'UTC';

if (!Number.isInteger(requestedSize) || requestedSize < 1 || requestedSize > 50000) {
  throw new Error('XAUUSD_OUTPUTSIZE must be an integer between 1 and 50000');
}
if (!Number.isInteger(perRequest) || perRequest < 1 || perRequest > 5000) {
  throw new Error('XAUUSD_CHUNK_SIZE must be an integer between 1 and 5000');
}

const root = new URL('../', import.meta.url);
const outputDir = new URL('data/historical/', root);
await mkdir(outputDir, { recursive: true });

function previousMinute(timestamp) {
  const date = new Date(`${timestamp.replace(' ', 'T')}Z`);
  if (Number.isNaN(date.getTime())) throw new Error(`Invalid Twelve Data timestamp: ${timestamp}`);
  date.setUTCMinutes(date.getUTCMinutes() - 1);
  return date.toISOString().slice(0, 16).replace('T', ' ') + ':00';
}

async function requestChunk(interval, outputsize, endDate) {
  const url = new URL('https://api.twelvedata.com/time_series');
  url.searchParams.set('symbol', symbol);
  url.searchParams.set('interval', interval);
  url.searchParams.set('outputsize', String(outputsize));
  url.searchParams.set('format', 'JSON');
  url.searchParams.set('timezone', timezone);
  url.searchParams.set('apikey', apiKey);
  if (endDate) url.searchParams.set('end_date', endDate);

  const response = await fetch(url);
  const body = await response.text();
  let payload;
  try {
    payload = JSON.parse(body);
  } catch {
    throw new Error(`Twelve Data ${interval}: invalid JSON response (HTTP ${response.status})`);
  }

  if (!response.ok) {
    throw new Error(`Twelve Data HTTP ${response.status} for ${interval}: ${payload?.message ?? 'request failed'}`);
  }
  if (payload?.status === 'error') {
    throw new Error(`Twelve Data ${interval}: ${payload.message ?? 'request failed'}`);
  }
  if (!Array.isArray(payload?.values) || payload.values.length === 0) {
    throw new Error(`Twelve Data ${interval}: no candles returned`);
  }

  return payload.values;
}

for (const interval of ['1min', '5min']) {
  console.log(`Downloading ${symbol} ${interval} (${requestedSize} candles requested, max ${perRequest} per API request)...`);

  const rawValues = [];
  let endDate;
  while (rawValues.length < requestedSize) {
    const remaining = requestedSize - rawValues.length;
    const chunkSize = Math.min(perRequest, remaining);
    const chunk = await requestChunk(interval, chunkSize, endDate);
    rawValues.push(...chunk);

    if (chunk.length < chunkSize || rawValues.length >= requestedSize) break;
    const oldest = chunk
      .filter((v) => v && typeof v.datetime === 'string')
      .map((v) => v.datetime)
      .sort()[0];
    if (!oldest) throw new Error(`Twelve Data ${interval}: chunk contained no valid timestamps`);
    endDate = previousMinute(oldest);
  }

  const seen = new Set();
  const values = rawValues
    .filter((v) => v && typeof v.datetime === 'string')
    .sort((a, b) => a.datetime.localeCompare(b.datetime))
    .filter((v) => !seen.has(v.datetime) && seen.add(v.datetime))
    .slice(-requestedSize)
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
  if (values.length < requestedSize) {
    console.warn(`Twelve Data ${interval}: requested ${requestedSize}, received ${values.length} unique candles`);
  }

  const dataset = { symbol: 'XAU/USD', timeframe: interval, source: 'twelvedata', timezone, candles: values };
  const path = new URL(`xauusd-${interval}.json`, outputDir);
  await writeFile(path, JSON.stringify(dataset, null, 2) + '\n', 'utf8');
  console.log(`Saved ${values.length} candles -> ${path.pathname}`);
}
