import { mkdir, writeFile } from 'node:fs/promises';

const apiKey = process.env.TWELVE_DATA_API_KEY;
if (!apiKey) throw new Error('Missing TWELVE_DATA_API_KEY environment variable');

const symbol = process.env.XAUUSD_SYMBOL ?? 'XAU/USD';
const requestedSize = Number(process.env.XAUUSD_OUTPUTSIZE ?? '10000');
const perRequest = Math.min(Number(process.env.XAUUSD_CHUNK_SIZE ?? '5000'), 5000);
const timezone = process.env.XAUUSD_TIMEZONE ?? 'UTC';
const maxRetries = Number(process.env.XAUUSD_MAX_RETRIES ?? '5');
const rateLimitWaitMs = Number(process.env.XAUUSD_RATE_LIMIT_WAIT_MS ?? '65000');

if (!Number.isInteger(requestedSize) || requestedSize < 1 || requestedSize > 50000) {
  throw new Error('XAUUSD_OUTPUTSIZE must be an integer between 1 and 50000');
}
if (!Number.isInteger(perRequest) || perRequest < 1 || perRequest > 5000) {
  throw new Error('XAUUSD_CHUNK_SIZE must be an integer between 1 and 5000');
}
if (!Number.isInteger(maxRetries) || maxRetries < 0 || maxRetries > 10) {
  throw new Error('XAUUSD_MAX_RETRIES must be an integer between 0 and 10');
}
if (!Number.isInteger(rateLimitWaitMs) || rateLimitWaitMs < 1000) {
  throw new Error('XAUUSD_RATE_LIMIT_WAIT_MS must be an integer >= 1000');
}

const root = new URL('../', import.meta.url);
const outputDir = new URL('data/historical/', root);
await mkdir(outputDir, { recursive: true });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function previousMinute(timestamp) {
  const date = new Date(`${timestamp.replace(' ', 'T')}Z`);
  if (Number.isNaN(date.getTime())) throw new Error(`Invalid Twelve Data timestamp: ${timestamp}`);
  date.setUTCMinutes(date.getUTCMinutes() - 1);
  return date.toISOString().slice(0, 16).replace('T', 'T') + ':00';
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

  for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
    const response = await fetch(url);
    const body = await response.text();
    let payload;
    try {
      payload = JSON.parse(body);
    } catch {
      throw new Error(`Twelve Data ${interval}: invalid JSON response (HTTP ${response.status})`);
    }

    const message = payload?.message ?? 'request failed';
    const isRateLimited = response.status === 429 || /run out of API credits|rate limit|too many requests/i.test(message);

    if (response.ok && payload?.status !== 'error') {
      if (!Array.isArray(payload?.values) || payload.values.length === 0) {
        throw new Error(`Twelve Data ${interval}: no candles returned`);
      }
      return payload.values;
    }

    if (!isRateLimited || attempt >= maxRetries) {
      if (!response.ok) {
        throw new Error(`Twelve Data HTTP ${response.status} for ${interval}: ${message}`);
      }
      throw new Error(`Twelve Data ${interval}: ${message}`);
    }

    const waitMs = rateLimitWaitMs + attempt * 5000;
    console.warn(
      `Twelve Data ${interval}: rate limited (HTTP ${response.status}). ` +
      `Waiting ${Math.ceil(waitMs / 1000)}s before retry ${attempt + 1}/${maxRetries}...`
    );
    await sleep(waitMs);
  }

  throw new Error(`Twelve Data ${interval}: exhausted rate-limit retries`);
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
