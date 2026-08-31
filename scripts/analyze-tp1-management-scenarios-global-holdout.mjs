import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.ts';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.ts';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.ts';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.ts';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.ts';

const ROOT=resolve(process.cwd());
const OUT=resolve(ROOT,'data/reports/strategy-a-tp1-management-scenarios-global-holdout');
const TIMEFRAMES=['1min','5min'];
const HORIZON=50;
const BREAKOUT_LOOKBACK=5;
const FT_MAX_BARS=2;
const SPIKE_MAX_CANDLES=8;
const SPIKE_MIN_DIRECTIONAL_FRACTION=0.5;
const SPIKE_MAX_OVERLAP_FRACTION=0.8;
const scenarios=[
  {name:'TP1_FULL_EXIT',desc:'100% realized at TP1 for TP1-qualified trades; all non-TP1 trades retain their baseline realized R.'},
  {name:'HALF_TP1_HALF_TP2_OR_BE',desc:'50% realized at TP1; remaining 50% targets deterministic TP2 and moves to breakeven after TP1. If TP2 is not valid, fall back to full TP1 exit.'},
  {name:'HALF_TP1_HALF_TP2_OR_PLUS_025R',desc:'50% realized at TP1; remaining 50% targets deterministic TP2 and uses a fixed +0.25R protected stop after TP1. If TP2 is not valid, fall back to full TP1 exit.'}
];
const finite=v=>Number.isFinite(Number(v));
const num=(r,keys)=>{for(const k of keys)if(finite(r[k]))return Number(r[k]);return null;};
function stats(rows){const rs=rows.map(r=>r.scenarioR).filter(Number.isFinite),w=rs.filter(x=>x>0),l=rs.filter(x=>x<0),gp=w.reduce((a,b)=>a+b,0),gl=-l.reduce((a,b)=>a+b,0);return{n:rs.length,winRate:rs.length?w.length/rs.length:0,PF:gl?gp/gl:(gp?null:0),avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0,totalR:rs.reduce((a,b)=>a+b,0)};}
function split(rows){const a=[...rows].sort((x,y)=>new Date(x.entryTime)-new Date(y.entryTime)),c=Math.floor(a.length/3);return{dev:a.slice(0,c),validation:a.slice(c,2*c),holdout:a.slice(2*c)};}
function reconstructTp2(r,candles){
  const ei=Number(r.entryIndex),entry=num(r,['entry','entryPrice','fillPrice','price']),sl=num(r,['stopLoss','stop','sl']),tp1=num(r,['tp1','takeProfit','target']);
  if(!Number.isInteger(ei)||!finite(entry)||!finite(sl)||!finite(tp1))return null;
  const visible=candles.slice(0,ei+1);
  if(visible.length<BREAKOUT_LOOKBACK+2)return null;
  const breakouts=detectBreakout(visible,BREAKOUT_LOOKBACK);
  const ft=detectFollowThrough(visible,breakouts,{maxBarsAfterBreakout:FT_MAX_BARS,requireCloseBeyondBrokenLevel:true});
  const spikes=detectSpikeCandidates(visible,breakouts,ft,{maxCandles:SPIKE_MAX_CANDLES,minDirectionalFraction:SPIKE_MIN_DIRECTIONAL_FRACTION,maxOverlapFraction:SPIKE_MAX_OVERLAP_FRACTION});
  const direction=String(r.direction).toUpperCase();
  for(const spike of spikes.candidates){
    const correction=detectFirstCorrection(visible,spike);
    if(!correction||correction.correctionExtremeIndex>=ei)continue;
    const projection=projectLeg2(visible,correction);
    if(!projection||projection.direction!==direction)continue;
    const tolerance=Math.max(1e-8,Math.abs(tp1)*1e-8);
    if(Math.abs(projection.tp1-tp1)>tolerance)continue;
    const tp2=direction==='BUY'?projection.projectionFrom+2*projection.leg1Size:projection.projectionFrom-2*projection.leg1Size;
    return{tp2,leg1Size:projection.leg1Size,projectionFrom:projection.projectionFrom};
  }
  return null;
}
function path(r,candles){
  const ei=Number(r.entryIndex),entry=num(r,['entry','entryPrice','fillPrice','price']),sl=num(r,['stopLoss','stop','sl']),tp1=num(r,['tp1','takeProfit','target']);
  if(!Number.isInteger(ei)||!finite(entry)||!finite(sl)||!finite(tp1))return null;
  const buy=String(r.direction).toUpperCase()==='BUY',risk=Math.abs(entry-sl),tp1Distance=Math.abs(tp1-entry);
  if(!(risk>0&&tp1Distance>0)||!(buy?tp1>entry:tp1<entry))return null;
  let tp1Idx=null,slIdx=null;
  for(let i=ei+1;i<candles.length;i++){const c=candles[i],hi=Number(c.high),lo=Number(c.low);if(!finite(hi)||!finite(lo))continue;if(tp1Idx===null&&(buy?hi>=tp1:lo<=tp1))tp1Idx=i;if(slIdx===null&&(buy?lo<=sl:hi>=sl))slIdx=i;if(tp1Idx!==null&&slIdx!==null)break;}
  if(tp1Idx===null||(slIdx!==null&&slIdx<tp1Idx))return null;
  const recon=reconstructTp2(r,candles),tp1R=tp1Distance/risk;
  if(!recon)return{entryTime:r.entryTime,direction:r.direction,tp1R,tp2R:null,barsToTp1:tp1Idx-ei,barsToTp2:null,beIdx:null,tp2Valid:false};
  const tp2=recon.tp2,tp2Distance=Math.abs(tp2-entry),tp2Directional=buy?tp2>tp1:tp2<tp1;
  const validTp2=tp2Directional&&tp2Distance>tp1Distance&&tp2Distance<=tp1Distance*4;
  let tp2Idx=null,protectedIdx=null;
  if(validTp2){for(let i=tp1Idx+1;i<Math.min(candles.length,tp1Idx+1+HORIZON);i++){const c=candles[i],hi=Number(c.high),lo=Number(c.low);if(!finite(hi)||!finite(lo))continue;if(tp2Idx===null&&(buy?hi>=tp2:lo<=tp2))tp2Idx=i;if(protectedIdx===null&&(buy?lo<=entry:hi>=entry))protectedIdx=i;if(tp2Idx!==null||protectedIdx!==null)break;}}
  return{entryTime:r.entryTime,direction:r.direction,tp1R,tp2R:validTp2?tp2Distance/risk:null,barsToTp1:tp1Idx-ei,barsToTp2:tp2Idx===null?null:tp2Idx-tp1Idx,beIdx:protectedIdx===null?null:protectedIdx-tp1Idx,tp2Valid:validTp2};
}
function evaluateQualified(p,name){
  if(name==='TP1_FULL_EXIT')return p.tp1R;
  if(!p.tp2Valid)return p.tp1R;
  const half=p.tp1R*.5;
  if(p.barsToTp2!==null)return half+.5*p.tp2R;
  if(p.beIdx!==null)return name==='HALF_TP1_HALF_TP2_OR_PLUS_025R'?half+.125:half;
  return half-.5;
}
function evaluateUniverse(baseTrades,paths,name){
  const byTime=new Map(paths.map(p=>[p.entryTime,p]));
  return baseTrades.filter(r=>finite(r.rMultiple)).map(r=>{
    const p=byTime.get(r.entryTime);
    const scenarioR=p?evaluateQualified(p,name):Number(r.rMultiple);
    return{entryTime:r.entryTime,direction:r.direction,scenarioR,managed:Boolean(p),tp1Qualified:Boolean(p),tp2Valid:Boolean(p?.tp2Valid)};
  });
}
async function run(tf){
  const[br,cr]=await Promise.all([readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf}.json`),'utf8'),readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')]);
  const base=JSON.parse(br),data=JSON.parse(cr),candles=data.candles??data;
  const baseTrades=(base.trades??[]).filter(r=>finite(r.rMultiple));
  const paths=baseTrades.map(r=>path(r,candles)).filter(Boolean);
  const s=split(baseTrades.map(r=>({entryTime:r.entryTime,r})).map(x=>x));
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_TP1_MANAGEMENT_SCENARIOS_GLOBAL_HOLDOUT_V4',timeframe:tf,scope:'Full resolved trade universe. Entry generation is unchanged. A signal remains valid until TP1 or structural invalidation; management changes only after TP1.',methodology:{universe:'All baseline trades with finite rMultiple are included in every scenario. Trades that never reach TP1 retain their baseline realized R, so scenario expectancy is not conditioned on future TP1 success.',tp1:'minimum objective for TP1-qualified trades',runner:'50% position remains after TP1 in runner scenarios',tp2:'deterministic 2-leg projection reconstructed from the same Strategy A correction/projection logic used to create TP1; no baseline tp2 field is trusted',fallback:'If TP1 is reached but no valid deterministic TP2 is reconstructable, runner scenarios fall back to full TP1 exit rather than dropping the trade',window:`${HORIZON} candles after TP1`,protectedStop:'BE means entry price; +0.25R means entry plus 0.25 initial-risk in the favorable direction',selection:'No optimization; scenarios fixed before holdout'},counts:{baselineResolved:baseTrades.length,tp1Qualified:paths.length,tp2Valid:paths.filter(p=>p.tp2Valid).length,universe:baseTrades.length},scenarios:{}};
  for(const sc of scenarios){const universe=evaluateUniverse(baseTrades,paths,sc.name),sp=split(universe);report.scenarios[sc.name]={description:sc.desc,dev:stats(sp.dev),validation:stats(sp.validation),holdout:stats(sp.holdout),all:stats(universe),managedTrades:universe.filter(x=>x.managed).length,tp2ManagedTrades:universe.filter(x=>x.tp2Valid).length};}
  report.holdoutRows=split(evaluateUniverse(baseTrades,paths,scenarios[0].name)).holdout;
  await mkdir(OUT,{recursive:true});const out=resolve(OUT,`${tf}.json`);await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: baselineResolved=${baseTrades.length} TP1-qualified=${paths.length} TP2-valid=${paths.filter(p=>p.tp2Valid).length}`);
  for(const sc of scenarios){const x=report.scenarios[sc.name];console.log(`  ${sc.name}: DEV n=${x.dev.n} PF=${x.dev.PF?.toFixed(4)??'n/a'} avgR=${x.dev.avgR.toFixed(4)} | VAL n=${x.validation.n} PF=${x.validation.PF?.toFixed(4)??'n/a'} avgR=${x.validation.avgR.toFixed(4)} | HOLDOUT n=${x.holdout.n} PF=${x.holdout.PF?.toFixed(4)??'n/a'} avgR=${x.holdout.avgR.toFixed(4)} totalR=${x.holdout.totalR.toFixed(4)}`);}
  console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES)await run(tf);
