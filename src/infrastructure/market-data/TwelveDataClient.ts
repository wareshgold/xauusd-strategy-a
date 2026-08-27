import type { Candle } from '../../domain/market/Candle.js';

interface TwelveDataValue {
  datetime: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume?: string;
}

interface TwelveDataResponse {
  status?: string;
  code?: number;
  message?: string;
  values?: TwelveDataValue[];
}

export interface TwelveDataClientOptions {
  readonly apiKey: string;
  readonly baseUrl?: string;
  readonly fetchImpl?: typeof fetch;
}

export interface TimeSeriesRequest {
  readonly symbol: string;
  readonly interval: '1min' | '5min';
  readonly outputSize: number;
  readonly startDate?: string;
  readonly endDate?: string;
}

export class TwelveDataClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(private readonly options: TwelveDataClientOptions) {
    if (!options.apiKey.trim()) {
      throw new Error('Twelve Data API key is required');
    }

    this.baseUrl = options.baseUrl ?? 'https://api.twelvedata.com';
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  async getTimeSeries(request: TimeSeriesRequest): Promise<Candle[]> {
    const url = new URL('/time_series', this.baseUrl);
    url.searchParams.set('symbol', request.symbol);
    url.searchParams.set('interval', request.interval);
    url.searchParams.set('outputsize', String(request.outputSize));
    url.searchParams.set('timezone', 'UTC');
    url.searchParams.set('apikey', this.options.apiKey);

    if (request.startDate) url.searchParams.set('start_date', request.startDate);
    if (request.endDate) url.searchParams.set('end_date', request.endDate);

    const response = await this.fetchImpl(url);
    if (!response.ok) {
      throw new Error(`Twelve Data HTTP error: ${response.status}`);
    }

    const body = (await response.json()) as TwelveDataResponse;
    if (!body.values) {
      throw new Error(`Twelve Data API error${body.code ? ` ${body.code}` : ''}: ${body.message ?? 'missing values'}`);
    }

    return body.values.map((value) => {
      const candle: Candle = {
        timestamp: normalizeUtcTimestamp(value.datetime),
        open: parsePrice(value.open, value.datetime),
        high: parsePrice(value.high, value.datetime),
        low: parsePrice(value.low, value.datetime),
        close: parsePrice(value.close, value.datetime),
        ...(value.volume !== undefined ? { volume: parsePrice(value.volume, value.datetime) } : {}),
      };

      return candle;
    });
  }
}

function parsePrice(value: string, timestamp: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`Invalid numeric value at ${timestamp}`);
  return parsed;
}

function normalizeUtcTimestamp(value: string): string {
  // Twelve Data returns naive timestamps when timezone=UTC. Preserve the
  // provider's minute precision while making the timezone explicit.
  return value.endsWith('Z') ? value : `${value.replace(' ', 'T')}Z`;
}
