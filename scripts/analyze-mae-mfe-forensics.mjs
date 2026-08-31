import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-mae-mfe-forensics');
const src = (tf) => resolve(ROOT, `data/reports/strategy-a-entry-geometry-forensics/${tf}.json`);
const candleSrc = (tf) => resolve(ROOT, `data/historical/xauusd-${tf}.json`);

function finite(v) { return Number.isFinite(Number(v)); }
function pick(r, keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function timeOf(c) { return c?.time ?? c?.timestamp ?? c?.datetime ?? c?.date ?? null; }
function priceOf(r) { return pick(r, ['entry', 'entryPrice', 'fillPrice', 'price']); }
function resultTime(r) { return r.exitTime ?? r.closeTime ?? r.endTime ?? r.resultTime ?? null; }
function stats(rows) {
  const n = rows.length; if (!n) return { n: 0, avgR: 0, totalR: 0, winRate: 0, PF: null };
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite), wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a,b)=>a+b,0), gl = -losses.reduce((a,b)=>a+b,0);
  return { n, avgR: rs.reduce((a,b)=>a+b,0)/rs.length, totalR: rs.reduce((a,b)=>a+b,0), winRate: wins.length/rs.length, PF: gl ? gp/gl : (gp ? null : 0) };
}
function split(rows) { const a=[...rows].sort((x,y)=>new Date(x.entryTime)-new Date(y.entryTime)), c=Math.floor(a.length/3); return {dev:a.slice(0,c),validation:a.slice(c,2*c),holdout:a.slice(2*c)}; }
function bucket(rows, fn) { return rows.filter(fn); }
function derivePathMetrics(trade, candles) {
  const entryTs=new Date(trade.entryTime).getTime(), exitTs=resultTime(trade)?new Date(resultTime(trade)).getTime():NaN, entry=priceOf(trade), risk=pick(trade,['riskDistance','risk','stopDistance']);
  if(!Number.isFinite(entryTs)||!Number.isFinite(exitTs)||!finite(entry)||!finite(risk)||risk<=0)return {};
  const path=[]; for(let i=0;i<candles.length;i++){const ts=new Date(timeOf(candles[i])).getTime();if(Number.isFinite(ts)&&ts>=entryTs&&ts<=exitTs)path.push({i,c:candles[i]});}
  if(!path.length)return {};
  const buy=trade.direction==='BUY'; let worst=0,best=0,maeIndex=path[0].i,mfeIndex=path[0].i;
  for(const {i,c} of path){const lo=Number(c.low),hi=Number(c.high),adverse=buy?entry-lo:hi-entry,favorable=buy?hi-entry:entry-lo;
    if(Number.isFinite(adverse)&&adverse>worst){worst=adverse;maeIndex=i;} if(Number.isFinite(favorable)&&favorable>best){best=favorable;mfeIndex=i;}}
  const entryIndex=path[0].i;
  return {maeR:Math.max(0,worst)/risk,mfeR:Math.max(0,best)/risk,timeToMfeBars:Math.max(0,mfeIndex-entryIndex),timeToMaeBars:Math.max(0,maeIndex-entryIndex),excursionSource:'historical_ohlc_between_entry_and_exit'};
}
async function report(tf) {
  const [raw,candleRaw]=await Promise.all([readFile(src(tf),'utf8'),readFile(candleSrc(tf),'utf8')]); const source=JSON.parse(raw), candleData=JSON.parse(candleRaw), candles=candleData.candles??candleData;
  const all=(source.tradeRows||[]).filter(r=>finite(r.rMultiple));
  const rows=all.map(r=>({...r,...derivePathMetrics(r,candles),mae:pick(r,['maeR','MAE','maxAdverseExcursionR','maxAdverseR','maxLossR']),mfe:pick(r,['mfeR','MFE','maxFavorableExcursionR','maxFavorableR']),timeToMfeBars:pick(r,['timeToMfeBars','barsToMfe','barsToMaxFavorable']),timeToMaeBars:pick(r,['timeToMaeBars','barsToMae','barsToMaxAdverse'])}));
  const s=split(rows);
  const buckets={mae:{LT_025:r=>r.mae!==null&&r.mae<.25,'025_050':r=>r.mae!==null&&r.mae>=.25&&r.mae<.5,'050_075':r=>r.mae!==null&&r.mae>=.5&&r.mae<.75,'075_100':r=>r.mae!==null&&r.mae>=.75&&r.mae<1,GE_100:r=>r.mae!==null&&r.mae>=1},mfe:{LT_050:r=>r.mfe!==null&&r.mfe<.5,'050_100':r=>r.mfe!==null&&r.mfe>=.5&&r.mfe<1,'100_150':r=>r.mfe!==null&&r.mfe>=1&&r.mfe<1.5,'150_200':r=>r.mfe!==null&&r.mfe>=1.5&&r.mfe<2,GE_200:r=>r.mfe!==null&&r.mfe>=2},timeToMfeBars:{D0_2:r=>r.timeToMfeBars!==null&&r.timeToMfeBars<=2,D3_5:r=>r.timeToMfeBars!==null&&r.timeToMfeBars>=3&&r.timeToMfeBars<=5,D6_8:r=>r.timeToMfeBars!==null&&r.timeToMfeBars>=6&&r.timeToMfeBars<=8,D9_12:r=>r.timeToMfeBars!==null&&r.timeToMfeBars>=9&&r.timeToMfeBars<=12,D13_PLUS:r=>r.timeToMfeBars!==null&&r.timeToMfeBars>=13}};
  const out={strategy:'Strategy A / SP2L',mode:'RESEARCH_MAE_MFE_TRADE_PATH_FORENSICS_V2',timeframe:tf,scope:'Descriptive trade-path analysis; MAE/MFE derived from historical OHLC between entry and exit; no rule selection or holdout optimization',globalCounts:{all:rows.length,dev:s.dev.length,validation:s.validation.length,holdout:s.holdout.length},coverage:{mae:rows.filter(r=>r.mae!==null).length,mfe:rows.filter(r=>r.mfe!==null).length,timeToMfeBars:rows.filter(r=>r.timeToMfeBars!==null).length,timeToMaeBars:rows.filter(r=>r.timeToMaeBars!==null).length},overall:stats(rows),by:{}};
  for(const [name,defs] of Object.entries(buckets)){out.by[name]={};for(const [label,fn] of Object.entries(defs))out.by[name][label]={all:stats(bucket(rows,fn)),dev:stats(bucket(s.dev,fn)),validation:stats(bucket(s.validation,fn)),holdout:stats(bucket(s.holdout,fn))};}
  out.thresholds={}; for(const x of [0.5,1,1.5,2])out.thresholds[`mfe_ge_${x}R`]={all:stats(rows.filter(r=>r.mfe!==null&&r.mfe>=x)),dev:stats(s.dev.filter(r=>r.mfe!==null&&r.mfe>=x)),validation:stats(s.validation.filter(r=>r.mfe!==null&&r.mfe>=x)),holdout:stats(s.holdout.filter(r=>r.mfe!==null&&r.mfe>=x))};
  return out;
}
await mkdir(OUT,{recursive:true}); for(const tf of ['1min','5min']){const r=await report(tf),p=resolve(OUT,`${tf}.json`);await writeFile(p,JSON.stringify(r,null,2));console.log(`${tf}: trades=${r.globalCounts.all} MAE=${r.coverage.mae} MFE=${r.coverage.mfe} timeToMFE=${r.coverage.timeToMfeBars}`);console.log(`Report -> ${p}`);}
