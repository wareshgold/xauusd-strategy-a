import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT=resolve(process.cwd());
const PRE=10000, DEV=6000, H=[1,3,5,10,20];
const THRESHOLDS=[0.25,0.5,0.75,1];
const TIME_BUCKETS=[['<=1',1],['2-3',3],['4-5',5],['6-10',10],['11-20',20]];
const OUT=resolve(ROOT,'data/reports/strategy-a-delay1-excursion-budget-time-outcome');
const BASE_DIR=resolve(ROOT,'data/reports/strategy-a-baseline');
const BREAKOUT_LOOKBACK=5, FT_MAX_BARS=2, SPIKE_MAX_CANDLES=8, SPIKE_MIN_DIRECTIONAL_FRACTION=.5, SPIKE_MAX_OVERLAP_FRACTION=.8;
const CONTEXT={emaPeriod:60,roundStep:50,roundDistance:5,tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:780,endMinutes:1320}],avoidWindows:[]};
const key=c=>`${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
const median=a=>{if(!a.length)return null;const s=[...a].sort((x,y)=>x-y),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2};
const pct=(n,d)=>d?n/d:null;
const pf=rs=>{const g=rs.filter(x=>x>0).reduce((a,b)=>a+b,0),l=-rs.filter(x=>x<0).reduce((a,b)=>a+b,0);return l?g/l:null};

function build(candles,index){
  const v=candles.slice(0,index+1);
  if(v.length<Math.max(BREAKOUT_LOOKBACK+2,CONTEXT.emaPeriod))return[];
  const bo=detectBreakout(v,BREAKOUT_LOOKBACK);
  const ft=detectFollowThrough(v,bo,{maxBarsAfterBreakout:FT_MAX_BARS,requireCloseBeyondBrokenLevel:true});
  const sp=detectSpikeCandidates(v,bo,ft,{maxCandles:SPIKE_MAX_CANDLES,minDirectionalFraction:SPIKE_MIN_DIRECTIONAL_FRACTION,maxOverlapFraction:SPIKE_MAX_OVERLAP_FRACTION});
  const out=[];
  for(const spike of sp.candidates){
    if(spike.endIndex>=index)continue;
    const correction=detectFirstCorrection(v,spike);
    if(!correction||correction.correctionExtremeIndex>=index)continue;
    const trigger=detectEntryTrigger(v,correction);
    if(!trigger||trigger.index!==index)continue;
    const projection=projectLeg2(v,correction); if(!projection)continue;
    const inv=getInvalidationRule(correction),ema=buildEMAContext(v.map(c=>c.close),CONTEXT); if(!ema)continue;
    const location=buildLocationContext(trigger.entryPrice,CONTEXT),session=buildSessionContext(trigger.timestamp,CONTEXT),quality=scoreSetup(spike,{ema,location,session});
    if(!quality.tradeAllowed)continue;
    const risk=Math.abs(trigger.entryPrice-inv.invalidationLevel),reward=Math.abs(projection.tp1-trigger.entryPrice);
    if(!(risk>0&&reward>0&&(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice)))continue;
    out.push({entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:inv.invalidationLevel,tp1:projection.tp1,session:session.session,correction});
  }
  return out;
}

function analyze(candles,candidate,trade){
  const i=Number(candidate.entryIndex),e=Number(candidate.entry),s=Number(candidate.stopLoss),d=String(candidate.direction).toUpperCase(),r=Math.abs(e-s);
  if(!Number.isInteger(i)||!Number.isFinite(e)||!Number.isFinite(s)||!r||!['BUY','SELL'].includes(d))return null;
  const path=[];
  for(let j=i+1;j<=Math.min(candles.length-1,i+20);j++){
    const favorable=(d==='BUY'?candles[j].high-e:e-candles[j].low)/r;
    const adverse=(d==='BUY'?e-candles[j].low:candles[j].high-e)/r;
    path.push({b:j-i,f:favorable,a:adverse});
  }
  const firstAt=(level)=>{for(const x of path){if(x.a>=level)return x.b;}return null;};
  const firstFav=(level)=>{for(const x of path){if(x.f>=level)return x.b;}return null;};
  const firstAdv={};
  for(const level of THRESHOLDS)firstAdv[level]=firstAt(level);
  const firstPlus1=firstFav(1), firstMinus1=firstAt(1);
  const horizons={};
  for(const h of H){
    const q=path.filter(x=>x.b<=h);
    let plusBar=null,minusBar=null;
    for(const x of q){if(plusBar===null&&x.f>=1)plusBar=x.b;if(minusBar===null&&x.a>=1)minusBar=x.b;}
    horizons[h]={mfe:Math.max(0,...q.map(x=>x.f)),mae:Math.max(0,...q.map(x=>x.a)),favFirst:plusBar!==null&&(minusBar===null||plusBar<minusBar),advFirst:minusBar!==null&&(plusBar===null||minusBar<plusBar),sameBar:plusBar!==null&&minusBar!==null&&plusBar===minusBar,plusReach:plusBar!==null,minusReach:minusBar!==null};
  }
  return {entryIndex:i,entryTime:candidate.entryTime,direction:d,entry:e,stopLoss:s,risk:r,rMultiple:Number(trade.rMultiple),firstAdv,horizons,firstPlus1,firstMinus1};
}

function outcomeSummary(rows){
  const x=rows.filter(r=>Number.isFinite(r.rMultiple));
  return {n:x.length,avgR:mean(x.map(r=>r.rMultiple)),pf:pf(x.map(r=>r.rMultiple)),winRate:pct(x.filter(r=>r.rMultiple>0).length,x.length),medianMFEH20:median(x.map(r=>r.horizons[20].mfe)),medianMAEH20:median(x.map(r=>r.horizons[20].mae)),plus1First:pct(x.filter(r=>r.horizons[20].favFirst).length,x.length),minus1First:pct(x.filter(r=>r.horizons[20].advFirst).length,x.length),sameBar:pct(x.filter(r=>r.horizons[20].sameBar).length,x.length)};
}

function timeSummary(rows,threshold){
  const reached=rows.filter(r=>r.firstAdv[threshold]!==null);
  const buckets={};
  for(const[name,maxBars]of TIME_BUCKETS){
    const x=reached.filter(r=>{const b=r.firstAdv[threshold];return name==='<=1'?b<=1:(b>=({'2-3':2,'4-5':4,'6-10':6,'11-20':11}[name])&&b<=maxBars);});
    buckets[name]={n:x.length,rate:pct(x.length,reached.length),shareOfAll:pct(x.length,rows.length),...outcomeSummary(x),medianTimeToExcursion:median(x.map(r=>r.firstAdv[threshold]))};
  }
  const never=reached.length===rows.length?[]:rows.filter(r=>r.firstAdv[threshold]===null);
  return {thresholdR:threshold,reachedN:reached.length,reachedRate:pct(reached.length,rows.length),neverN:never.length,neverRate:pct(never.length,rows.length),buckets};
}

async function run(tf){
  const raw=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')),candles=raw.candles??raw;
  const base=JSON.parse(await readFile(resolve(BASE_DIR,`${tf}.json`),'utf8'));
  const cutoff=new Date(candles[PRE].timestamp);
  const canonical=new Map((base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<cutoff).map(t=>[key(t),t]));
  const rows=[];
  for(let i=0;i<PRE;i++){
    const cs=build(candles,i);if(!cs.length)continue;
    const candidate=cs[0],trade=canonical.get(key(candidate));if(!trade||candidate.entryIndex-candidate.correction.correctionExtremeIndex!==1)continue;
    const row=analyze(candles,candidate,trade);if(row)rows.push(row);
  }
  const dev=rows.filter(r=>r.entryIndex<DEV),val=rows.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE);
  const report={strategy:'Strategy A',mode:'DELAY1_EXCURSION_BUDGET_TIME_OUTCOME',scope:{preHoldoutCandles:PRE,devCandles:DEV,valCandles:PRE-DEV,delayExactly:1,freshHoldoutExcluded:true},methodology:{thresholdsR:THRESHOLDS,timeBuckets:TIME_BUCKETS.map(([name,maxBars])=>({name,maxBars})),horizons:H,noOptimization:true,noFreshHoldout:true,productionUntouched:true,note:'For each Delay=1 trade, measure the first candle after entry on which adverse excursion reaches each threshold. Time buckets are descriptive and must not be treated as live filters. Same-bar OHLC ordering remains ambiguous.'},DEV:{...outcomeSummary(dev),byThreshold:Object.fromEntries(THRESHOLDS.map(t=>[`-${t}R`,timeSummary(dev,t)]))},VAL:{...outcomeSummary(val),byThreshold:Object.fromEntries(THRESHOLDS.map(t=>[`-${t}R`,timeSummary(val,t)]))},allPreHoldout:{...outcomeSummary(rows),byThreshold:Object.fromEntries(THRESHOLDS.map(t=>[`-${t}R`,timeSummary(rows,t)]))},rows};
  await mkdir(OUT,{recursive:true});const out=resolve(OUT,`${tf}.json`);await writeFile(out,JSON.stringify(report,null,2));
  const print=(label,s)=>{console.log(`${label}: n=${s.n} AvgR=${s.avgR?.toFixed(3)} PF=${s.pf?.toFixed(3)} WR=${(100*s.winRate).toFixed(1)} MFE/MAE H20=${s.medianMFEH20?.toFixed(2)}/${s.medianMAEH20?.toFixed(2)}`);for(const[k,v]of Object.entries(s.byThreshold)){console.log(`  ${k}: reached=${v.reachedN}/${s.n} (${(100*v.reachedRate).toFixed(1)}%) never=${v.neverN}`);for(const[b,x]of Object.entries(v.buckets))console.log(`    ${b}: n=${x.n} share=${(100*x.shareOfAll).toFixed(1)} AvgR=${x.avgR?.toFixed(3)} PF=${x.pf?.toFixed(3)} WR=${x.winRate===null?'null':(100*x.winRate).toFixed(1)} medT=${x.medianTimeToExcursion??'null'}`)}};
  console.log(`\n=== ${tf} DELAY1 EXCURSION BUDGET × TIME × OUTCOME ===`);print('DEV',report.DEV);print('VAL',report.VAL);console.log(`Report -> ${out}`);
}
for(const tf of ['1min','5min'])await run(tf);
