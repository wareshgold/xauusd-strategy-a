import { normalizeHistoricalCandles, type HistoricalDataset } from './HistoricalCandle.js';

export function parseTwelveDataCsv(csv: string, timeframe: '1min'|'5min' = '1min'): HistoricalDataset {
  const lines=csv.trim().split(/\r?\n/).filter(Boolean); if(lines.length<2) throw new Error('CSV contains no candle rows');
  const header=lines[0]!.split(',').map(x=>x.trim().toLowerCase());
  const index=(name:string)=>{const i=header.indexOf(name);if(i<0)throw new Error(`Missing Twelve Data CSV column: ${name}`);return i;};
  const ti=index('datetime'), oi=index('open'), hi=index('high'), li=index('low'), ci=index('close'); const vi=header.indexOf('volume');
  const rows=lines.slice(1).map(line=>{const p=line.split(','); const n=(i:number)=>Number(p[i]); const row={timestamp:p[ti]!,open:n(oi),high:n(hi),low:n(li),close:n(ci),...(vi>=0?{volume:n(vi)}:{})}; if(!Number.isFinite(row.open)||!Number.isFinite(row.high)||!Number.isFinite(row.low)||!Number.isFinite(row.close))throw new Error(`Invalid OHLC row: ${line}`); return row;});
  rows.sort((a,b)=>a.timestamp.localeCompare(b.timestamp)); return normalizeHistoricalCandles(rows,timeframe,'twelvedata');
}
