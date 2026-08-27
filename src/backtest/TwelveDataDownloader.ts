export interface TwelveDataDownloadConfig { readonly apiKey: string; readonly symbol: string; readonly interval: '1min'|'5min'; readonly outputsize?: number; readonly startDate?: string; readonly endDate?: string; readonly timezone?: string; }
export interface TwelveDataResponse { readonly meta?: Record<string, unknown>; readonly values?: readonly Record<string,string>[]; readonly status?: string; readonly message?: string; }

export async function downloadTwelveData(config: TwelveDataDownloadConfig, fetchImpl: typeof fetch = fetch): Promise<TwelveDataResponse> {
  const url = new URL('https://api.twelvedata.com/time_series');
  url.searchParams.set('symbol', config.symbol); url.searchParams.set('interval', config.interval); url.searchParams.set('apikey', config.apiKey); url.searchParams.set('format', 'JSON');
  if (config.outputsize !== undefined) url.searchParams.set('outputsize', String(config.outputsize));
  if (config.startDate) url.searchParams.set('start_date', config.startDate); if (config.endDate) url.searchParams.set('end_date', config.endDate); if (config.timezone) url.searchParams.set('timezone', config.timezone);
  const response = await fetchImpl(url); if (!response.ok) throw new Error(`Twelve Data HTTP ${response.status}`);
  const data = await response.json() as TwelveDataResponse; if (data.status === 'error') throw new Error(data.message ?? 'Twelve Data request failed'); return data;
}
