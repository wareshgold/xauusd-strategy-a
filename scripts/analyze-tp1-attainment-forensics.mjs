import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-tp1-attainment-forensics');
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [1, 2, 3, 5, 8, 12, 20, 30, 50];
const MIN_N = 10;

function finite(v) { return Number.isFinite(Number(v)); }
function num(r, keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0), gl = -losses.reduce((a, b) => a + b, 0);
  return { n: rs.length, winRate: rs.length ? wins.length / rs.length : 0, PF: gl ? gp / gl : (gp ? null : 0), avgR: rs.length ? rs.reduce((a,b)=>a+b,0)/rs.length : 0, totalR: rs.reduce((a,b)=>a+b,0) };
}
function split(rows) {
  const a = [...rows].sort((x,y) => new Date(x.entryTime) - new Date(y.entryTime));
  const c = Math.floor(a.length / 3);
  return { dev:a.slice(0,c), validation:a.slice(c,2*c), holdout:a.slice(2*c) };
}
function tp1Index(trade, candles) {
  const entryIndex = Number(trade.entryIndex);
  const entry = num(trade, ['entry','entryPrice','fillPrice','price']);
  const tp1 = num(trade, ['tp1','takeProfit','target']);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(tp1)) return null;
  const buy = String(trade.direction).toUpperCase() === 'BUY';
  for (let i=entryIndex+1;i<candles.length;i++) {
    const c=candles[i];
    if (buy ? Number(c.high) >= tp1 : Number(c.low) <= tp1) return i;
  }
  return null;
}
function slIndex(trade, candles) {
  const entryIndex=Number(trade.entryIndex), stop=num(trade,['stopLoss','stop','sl']);
  if (!Number.isInteger(entryIndex)||!finite(stop)) return null;
  const buy=String(trade.direction).toUpperCase()==='BUY';
  for(let i=entryIndex+1;i<candles.length;i++) { const c=candles[i]; if(buy?Number(c.low)<=stop:Number(c.high)>=stop) return i; }
  return null;
}
function path(trade,candles) {
  const entryIndex=Number(trade.entryIndex), entry=num(trade,['entry','entryPrice','fillPrice','price']), risk=num(trade,['riskDistance','risk','stopDistance']);
  if(!Number.isInteger(entryIndex)||!finite(entry)||!finite(risk)||risk<=0) return null;
  const tp1=num(trade,['tp1','takeProfit','target']);
  const buy=String(trade.direction).toUpperCase()==='BUY';
  const tp1Idx=tp1Index(trade,candles), slIdx=slIndex(trade,candles);
  const firstBarrier = tp1Idx===null?slIdx:slIdx===null?tp1Idx:Math.min(tp1Idx,slIdx);
  let mfe=0, mae=0, mfeBeforeBarrier=0, maeBeforeBarrier=0;
  const maxEnd=Math.min(candles.length-1, firstBarrier ?? candles.length-1);
  for(let i=entryIndex+1;i<=maxEnd;i++) { const c=candles[i], lo=Number(c.low), hi=Number(c.high); if(!Number.isFinite(lo)||!Number.isFinite(hi)) continue; mfe=Math.max(mfe,buy?hi-entry:entry-lo); mae=Math.max(mae,buy?entry-lo:hi-entry); }
  const tp1ReachedBeforeSl = tp1Idx!==null && (slIdx===null || tp1Idx<slIdx);
  const sameCandle = tp1Idx!==null && slIdx!==null && tp1Idx===slIdx;
  const tp1R = Math.abs(tp1-entry)/risk;
  return { tp1Idx, slIdx, firstBarrier, tp1ReachedBeforeSl, sameCandle, barsToTp1:tp1Idx===null?null:tp1Idx-entryIndex, barsToSl:slIdx===null?null:slIdx-entryIndex, tp1R, mfeBeforeBarrier:mfe/risk, maeBeforeBarrier:mae/risk };
}
function enrich(rows,candles) { return rows.map(r=>{const p=path(r,candles); return p?{...r,path:p}:null;}).filter(Boolean); }
function partition(rows) { const s=split(rows); return {all:rows,dev:s.dev,validation:s.validation,holdout:s.holdout}; }
function quantile(xs,p) { const a=xs.filter(Number.isFinite).sort((x,y)=>x-y); return a.length?a[Math.min(a.length-1,Math.floor((a.length-1)*p))]:null; }
function describe(rows) {
  return { n:rows.length, tp1HitRate:rows.length?rows.filter(r=>r.path.tp1ReachedBeforeSl).length/rows.length:0, tp1OrAmbiguousRate:rows.length?rows.filter(r=>r.path.tp1Idx!==null).length/rows.length:0, medianBarsToTp1:quantile(rows.map(r=>r.path.barsToTp1),.5), p75BarsToTp1:quantile(rows.map(r=>r.path.barsToTp1),.75), medianMAEBeforeBarrier:quantile(rows.map(r=>r.path.maeBeforeBarrier),.5), medianMFEBeforeBarrier:quantile(rows.map(r=>r.path.mfeBeforeBarrier),.5) };
}
async function run(tf) {
  const [raw,candleRaw]=await Promise.all([readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf}.json`),'utf8'),readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')]);
  const source=JSON.parse(raw), candleData=JSON.parse(candleRaw), candles=candleData.candles??candleData;
  const rows=enrich((source.trades??[]).filter(r=>finite(r.rMultiple)),candles);
  const parts=partition(rows);
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_TP1_ATTAINMENT_PATH_FORENSICS_V1',timeframe:tf,scope:'Descriptive path analysis of every recorded baseline trade. No entry rule or exit rule is changed. TP1 is treated as the minimum objective; the analysis measures whether TP1 is reached before the invalidation stop and how much adverse excursion occurs on the way.',methodology:{source:'strategy-a-baseline trades + historical OHLC',barrierOrder:'TP1 and SL are replayed from post-entry candles; if both are first touched on the same candle the case is flagged ambiguous and is not counted as TP1-before-SL.',tp1Definition:'directional touch of recorded TP1 level',invalidationDefinition:'directional touch of recorded stopLoss',horizons:HORIZONS,selection:'No candidate optimization; all horizon summaries are descriptive.',important:'This analysis does not permit an early exit merely because price moves against the trade. It explicitly measures the path to the minimum TP1 objective.'},counts:{all:rows.length,dev:parts.dev.length,validation:parts.validation.length,holdout:parts.holdout.length},pathSummary:{all:describe(rows),dev:describe(parts.dev),validation:describe(parts.validation),holdout:describe(parts.holdout)},barrierOutcomes:{all:stats(rows),tp1BeforeSl:stats(rows.filter(r=>r.path.tp1ReachedBeforeSl)),slBeforeTp1:stats(rows.filter(r=>r.path.slIdx!==null && !r.path.tp1ReachedBeforeSl && !r.path.sameCandle)),sameCandle:stats(rows.filter(r=>r.path.sameCandle))},horizonSurvival:{}};
  for(const h of HORIZONS){
    const eligible=rows.filter(r=>Number.isInteger(r.entryIndex)&&r.entryIndex+h<candles.length);
    const reachedByH=eligible.filter(r=>r.path.tp1Idx!==null&&r.path.tp1Idx-r.entryIndex<=h);
    const stillAliveAtH=eligible.filter(r=>r.path.firstBarrier===null||r.path.firstBarrier-r.entryIndex>h);
    const tp1BeforeSlByH=eligible.filter(r=>r.path.tp1ReachedBeforeSl&&r.path.barsToTp1<=h);
    report.horizonSurvival[`H${h}`]={eligibleN:eligible.length,tp1ReachedByH:reachedByH.length,tp1ReachRate:eligible.length?reachedByH.length/eligible.length:0,tp1BeforeSlByH:tp1BeforeSlByH.length,tp1BeforeSlRate:eligible.length?tp1BeforeSlByH.length/eligible.length:0,stillNoBarrierAtH:stillAliveAtH.length};
  }
  const pathClasses=[['tp1_fast_1_3',r=>r.path.tp1ReachedBeforeSl&&r.path.barsToTp1<=3],['tp1_slow_4_8',r=>r.path.tp1ReachedBeforeSl&&r.path.barsToTp1>=4&&r.path.barsToTp1<=8],['tp1_very_slow_9_plus',r=>r.path.tp1ReachedBeforeSl&&r.path.barsToTp1>=9],['sl_before_tp1_low_mae',r=>r.path.slIdx!==null&&!r.path.tp1ReachedBeforeSl&&!r.path.sameCandle&&r.path.maeBeforeBarrier<0.5],['sl_before_tp1_high_mae',r=>r.path.slIdx!==null&&!r.path.tp1ReachedBeforeSl&&!r.path.sameCandle&&r.path.maeBeforeBarrier>=0.5]];
  report.pathClasses={}; for(const [name,fn] of pathClasses) report.pathClasses[name]={all:stats(rows.filter(fn)),dev:stats(parts.dev.filter(fn)),validation:stats(parts.validation.filter(fn)),holdout:stats(parts.holdout.filter(fn))};
  await mkdir(OUT,{recursive:true}); const out=resolve(OUT,`${tf}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: trades=${rows.length} TP1-before-SL=${rows.filter(r=>r.path.tp1ReachedBeforeSl).length} SL-before-TP1=${rows.filter(r=>r.path.slIdx!==null&&!r.path.tp1ReachedBeforeSl&&!r.path.sameCandle).length} ambiguous=${rows.filter(r=>r.path.sameCandle).length}`);
  for(const h of HORIZONS){const x=report.horizonSurvival[`H${h}`]; console.log(`  H${h}: TP1 reached=${x.tp1ReachedByH}/${x.eligibleN} ${(x.tp1ReachRate*100).toFixed(1)}% | TP1-before-SL=${x.tp1BeforeSlByH}/${x.eligibleN} ${(x.tp1BeforeSlRate*100).toFixed(1)}%`);}
  console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES) await run(tf);
