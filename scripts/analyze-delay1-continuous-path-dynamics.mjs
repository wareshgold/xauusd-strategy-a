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

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-continuous-path-dynamics');
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const CHECKPOINTS = [1, 2, 3];
const HORIZONS = [5, 10, 20];

const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 },
  ],
  avoidWindows: [],
};

const key = t => `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { const x = a.filter(Number.isFinite).sort((a,b)=>a-b); if (!x.length) return null; const m=Math.floor(x.length/2); return x.length%2 ? x[m] : (x[m-1]+x[m])/2; };
const pct = (n,d) => d ? n/d : null;
const pf = rs => { const w=rs.filter(x=>x>0).reduce((a,b)=>a+b,0); const l=-rs.filter(x=>x<0).reduce((a,b)=>a+b,0); return l>0?w/l:null; };
const stats = rows => { const rs=rows.map(r=>Number(r.rMultiple)).filter(Number.isFinite); return {n:rs.length,avgR:mean(rs),PF:pf(rs),WR:pct(rs.filter(x=>x>0).length,rs.length),totalR:rs.reduce((a,b)=>a+b,0)}; };

function buildCandidate(candles,index){
  const v=candles.slice(0,index+1); if(v.length<Math.max(CONTEXT.emaPeriod,7)) return null;
  const bo=detectBreakout(v,5); const ft=detectFollowThrough(v,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true});
  const sp=detectSpikeCandidates(v,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});
  for(const spike of sp.candidates){
    if(spike.endIndex>=index) continue; const correction=detectFirstCorrection(v,spike); if(!correction||correction.correctionExtremeIndex>=index) continue;
    const trigger=detectEntryTrigger(v,correction); if(!trigger||trigger.index!==index||index-correction.correctionExtremeIndex!==1) continue;
    const projection=projectLeg2(v,correction); if(!projection) continue; const inv=getInvalidationRule(correction);
    const ema=buildEMAContext(v.map(c=>c.close),CONTEXT); if(!ema) continue; const location=buildLocationContext(trigger.entryPrice,CONTEXT); const session=buildSessionContext(trigger.timestamp,CONTEXT);
    const quality=scoreSetup(spike,{ema,location,session}); if(!quality.tradeAllowed) continue;
    const risk=Math.abs(trigger.entryPrice-inv.invalidationLevel), reward=Math.abs(projection.tp1-trigger.entryPrice);
    if(!(risk>0&&reward>0)) continue; if(!(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice)) continue;
    return {entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:inv.invalidationLevel,tp1:projection.tp1};
  }
  return null;
}

function path(candles,c){
  const i=Number(c.entryIndex),e=Number(c.entry),s=Number(c.stopLoss),d=c.direction,risk=Math.abs(e-s); if(!Number.isInteger(i)||!Number.isFinite(e)||!Number.isFinite(s)||risk<=0)return [];
  const out=[]; let cumMae=0,cumMfe=0,prevMae=0,prevMfe=0;
  for(let j=i+1;j<=Math.min(candles.length-1,i+20);j++){
    const x=candles[j]; const adverse=Math.max(0,(d==='BUY'?e-x.low:x.high-e)/risk); const favorable=Math.max(0,(d==='BUY'?x.high-e:e-x.low)/risk);
    cumMae=Math.max(cumMae,adverse); cumMfe=Math.max(cumMfe,favorable);
    out.push({bar:j-i,adverse,favorable,mae:cumMae,mfe:cumMfe,deltaMae:cumMae-prevMae,deltaMfe:cumMfe-prevMfe}); prevMae=cumMae; prevMfe=cumMfe;
  }
  return out;
}

function firstTouch(p,threshold,field){ const x=p.find(z=>z[field]>=threshold); return x?.bar??null; }
function firstEvent(p,start,end){
  let plus=null,stop=null; for(const x of p){if(x.bar<=start||x.bar>end)continue;if(plus===null&&x.favorable>=1)plus=x.bar;if(stop===null&&x.adverse>=1)stop=x.bar;}
  if(plus===null&&stop===null)return 'NONE'; if(plus!==null&&stop!==null&&plus===stop)return 'SAME_BAR_AMBIGUOUS'; if(plus===null)return 'STOP'; if(stop===null)return 'PLUS1'; return plus<stop?'PLUS1':'STOP';
}
function pathMetrics(p,checkpoint,horizon){
  const end=p.filter(x=>x.bar<=horizon), through=p.filter(x=>x.bar<=checkpoint); if(!end.length||!through.length)return null;
  const mae=Math.max(...through.map(x=>x.mae)), mfe=Math.max(...through.map(x=>x.mfe));
  const future=end.filter(x=>x.bar>checkpoint); const maxFutureMae=future.length?Math.max(...future.map(x=>x.mae)):null; const maxFutureMfe=future.length?Math.max(...future.map(x=>x.mfe)):null;
  const tMae25=firstTouch(through,.25,'mae'),tMae50=firstTouch(through,.5,'mae'),tMae75=firstTouch(through,.75,'mae'),tMae1=firstTouch(through,1,'mae');
  const tMfe05=firstTouch(through,.5,'mfe'),tMfe1=firstTouch(through,1,'mfe'),tMfe2=firstTouch(through,2,'mfe');
  const event=firstEvent(p,checkpoint,horizon);
  return {maeAtCheckpoint:mae,mfeAtCheckpoint:mfe,mfeMaeRatio:mae>0?mfe/mae:null,maxMaeByHorizon:maxFutureMae,maxMfeByHorizon:maxFutureMfe,deltaMaeAfterCheckpoint:future.length?Math.max(...future.map(x=>x.mae))-mae:null,deltaMfeAfterCheckpoint:future.length?Math.max(...future.map(x=>x.mfe))-mfe:null,timeToMae25:tMae25,timeToMae50:tMae50,timeToMae75:tMae75,timeToMae1:tMae1,timeToMfe05:tMfe05,timeToMfe1:tMfe1,timeToMfe2:tMfe2,event};
}
function aggregate(rows,checkpoint,horizon){
  const ms=rows.map(r=>pathMetrics(r.p,checkpoint,horizon)).filter(Boolean), rs=rows.map(r=>Number(r.rMultiple)).filter(Number.isFinite), num=(k)=>ms.map(x=>x[k]).filter(Number.isFinite);
  return {n:ms.length,avgR:mean(rs),PF:pf(rs),WR:pct(rs.filter(x=>x>0).length,rs.length),maeMedian:median(num('maeAtCheckpoint')),mfeMedian:median(num('mfeAtCheckpoint')),mfeMaeRatioMedian:median(num('mfeMaeRatio')),deltaMaeMedian:median(num('deltaMaeAfterCheckpoint')),deltaMfeMedian:median(num('deltaMfeAfterCheckpoint')),timeToMae25Median:median(num('timeToMae25')),timeToMae50Median:median(num('timeToMae50')),timeToMae75Median:median(num('timeToMae75')),timeToMae1Median:median(num('timeToMae1')),timeToMfe05Median:median(num('timeToMfe05')),timeToMfe1Median:median(num('timeToMfe1')),timeToMfe2Median:median(num('timeToMfe2')),plus1BeforeStop:pct(ms.filter(x=>x.event==='PLUS1').length,ms.length),stopBeforePlus1:pct(ms.filter(x=>x.event==='STOP').length,ms.length),sameBar:pct(ms.filter(x=>x.event==='SAME_BAR_AMBIGUOUS').length,ms.length),none:pct(ms.filter(x=>x.event==='NONE').length,ms.length)};
}

async function loadBaseline(tf,candles){
  const report=JSON.parse(await readFile(resolve(BASE,`${tf}.json`),'utf8')); const cutoff=new Date(candles[PRE].timestamp);
  return (report.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<cutoff);
}
async function run(tf){
  const raw=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')); const candles=raw.candles??raw; if(candles.length<PRE)throw new Error(`${tf}: expected ${PRE} candles`);
  const baseline=await loadBaseline(tf,candles),map=new Map(baseline.map(t=>[key(t),t])),rows=[];
  for(let i=0;i<PRE;i++){const c=buildCandidate(candles,i);if(!c)continue;const t=map.get(key(c));if(!t)continue;const p=path(candles,c);if(p.length)rows.push({entryIndex:i,entryTime:c.entryTime,direction:c.direction,rMultiple:Number(t.rMultiple),p});}
  const windows=[]; for(let start=0;start<PRE;start+=BLOCK){const end=Math.min(PRE,start+BLOCK),label=start<DEV?`DEV_${String(start/BLOCK+1).padStart(2,'0')}`:`VAL_${String((start-DEV)/BLOCK+1).padStart(2,'0')}`,wr=rows.filter(r=>r.entryIndex>=start&&r.entryIndex<end); const data={}; for(const cp of CHECKPOINTS){for(const h of HORIZONS.filter(x=>x>cp))data[`T${cp}_H${h}`]=aggregate(wr,cp,h);} windows.push({label,candleStart:start,candleEndExclusive:end,startTime:candles[start]?.timestamp??null,endTime:candles[end-1]?.timestamp??null,baseline:stats(wr),metrics:data});}
  const report={strategy:'Strategy A',mode:'DELAY1_CONTINUOUS_POST_ENTRY_PATH_DYNAMICS',timeframe:tf,scope:{preHoldoutCandles:PRE,devCandles:DEV,valCandles:PRE-DEV,blockCandles:BLOCK,delayExactly:1,checkpoints:CHECKPOINTS,horizons:HORIZONS},methodology:{purpose:'Measure continuous post-entry path dynamics without selecting new thresholds.',features:['MAE','MFE','MFE/MAE','delta MAE','delta MFE','time to adverse thresholds','time to favorable thresholds','first +1R vs -1R event'],windowing:'Five fixed chronological 2,000-candle windows: DEV_01..03 and VAL_01..02.',sameBarOHLC:'Same-candle +1R and -1R are classified as SAME_BAR_AMBIGUOUS; no intrabar order inferred.',freshHoldoutExcluded:true,noOptimization:true,diagnosticOnly:true,productionUntouched:true},overall:stats(rows),windows};
  await mkdir(OUT,{recursive:true}); const file=resolve(OUT,`${tf}.json`); await writeFile(file,JSON.stringify(report,null,2));
  console.log(`\n=== ${tf} DELAY1 CONTINUOUS PATH DYNAMICS ===`); console.log(`joined=${rows.length} AvgR=${report.overall.avgR?.toFixed(3)??'n/a'} PF=${report.overall.PF?.toFixed(3)??'n/a'}`);
  for(const w of windows){console.log(`${w.label}: n=${w.baseline.n} AvgR=${w.baseline.avgR?.toFixed(3)??'n/a'} PF=${w.baseline.PF?.toFixed(3)??'n/a'}`);for(const [k,x] of Object.entries(w.metrics)){console.log(`  ${k}: n=${x.n} MAE50=${x.maeMedian?.toFixed(3)??'n/a'} MFE50=${x.mfeMedian?.toFixed(3)??'n/a'} MFE/MAE50=${x.mfeMaeRatioMedian?.toFixed(3)??'n/a'} dMAE50=${x.deltaMaeMedian?.toFixed(3)??'n/a'} dMFE50=${x.deltaMfeMedian?.toFixed(3)??'n/a'} tMAE50=${x.timeToMae50Median??'n/a'} tMFE1=${x.timeToMfe1Median??'n/a'} +1beforeSTOP=${(100*(x.plus1BeforeStop??0)).toFixed(1)}% STOPbefore+1=${(100*(x.stopBeforePlus1??0)).toFixed(1)}% SAME=${(100*(x.sameBar??0)).toFixed(1)}%`);}}
  console.log(`Report -> ${file}`);
}
for(const tf of ['1min','5min'])await run(tf);
