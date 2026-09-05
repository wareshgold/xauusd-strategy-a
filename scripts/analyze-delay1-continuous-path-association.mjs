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
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-continuous-path-association');
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const CHECKPOINTS = [1, 2, 3];
const HORIZONS = [5, 10, 20];
const FEATURES = ['mae', 'mfe', 'mfeMaeRatio', 'deltaMae', 'deltaMfe'];

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
const pf = rs => { const w=rs.filter(x=>x>0).reduce((a,b)=>a+b,0); const l=-rs.filter(x=>x<0).reduce((a,b)=>a+b,0); return l>0?w/l:null; };
const stats = rows => { const rs=rows.map(r=>r.rMultiple).filter(Number.isFinite); return {n:rs.length,avgR:mean(rs),PF:pf(rs),WR:rs.length?rs.filter(x=>x>0).length/rs.length:null,totalR:rs.reduce((a,b)=>a+b,0)}; };

function buildCandidate(candles,index){
  const v=candles.slice(0,index+1); if(v.length<Math.max(CONTEXT.emaPeriod,7)) return null;
  const bo=detectBreakout(v,5); const ft=detectFollowThrough(v,5?bo:bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true});
  const sp=detectSpikeCandidates(v,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8});
  for(const spike of sp.candidates){
    if(spike.endIndex>=index) continue;
    const correction=detectFirstCorrection(v,spike); if(!correction||correction.correctionExtremeIndex>=index) continue;
    const trigger=detectEntryTrigger(v,correction); if(!trigger||trigger.index!==index||index-correction.correctionExtremeIndex!==1) continue;
    const projection=projectLeg2(v,correction); if(!projection) continue; const inv=getInvalidationRule(correction);
    const ema=buildEMAContext(v.map(c=>c.close),CONTEXT); if(!ema) continue;
    const location=buildLocationContext(trigger.entryPrice,CONTEXT); const session=buildSessionContext(trigger.timestamp,CONTEXT);
    const quality=scoreSetup(spike,{ema,location,session}); if(!quality.tradeAllowed) continue;
    const risk=Math.abs(trigger.entryPrice-inv.invalidationLevel), reward=Math.abs(projection.tp1-trigger.entryPrice);
    if(!(risk>0&&reward>0)) continue;
    if(!(trigger.direction==='BUY'?projection.tp1>trigger.entryPrice:projection.tp1<trigger.entryPrice)) continue;
    return {entryIndex:index,entryTime:trigger.timestamp,direction:trigger.direction,entry:trigger.entryPrice,stopLoss:inv.invalidationLevel,tp1:projection.tp1};
  }
  return null;
}

function path(candles,c){
  const i=Number(c.entryIndex),e=Number(c.entry),s=Number(c.stopLoss),d=c.direction,risk=Math.abs(e-s);
  if(!Number.isInteger(i)||!Number.isFinite(e)||!Number.isFinite(s)||risk<=0)return [];
  const out=[]; let mae=0,mfe=0;
  for(let j=i+1;j<=Math.min(candles.length-1,i+20);j++){
    const x=candles[j];
    const adverse=Math.max(0,(d==='BUY'?e-x.low:x.high-e)/risk);
    const favorable=Math.max(0,(d==='BUY'?x.high-e:e-x.low)/risk);
    const prevMae=mae,prevMfe=mfe;
    mae=Math.max(mae,adverse); mfe=Math.max(mfe,favorable);
    out.push({bar:j-i,mae,mfe,deltaMae:mae-prevMae,deltaMfe:mfe-prevMfe,mfeMaeRatio:mae>0?mfe/mae:null});
  }
  return out;
}

function featureAt(p,checkpoint,feature){
  const x=p.find(z=>z.bar===checkpoint); if(!x)return null;
  return x[feature];
}

function intervalFeature(p,start,end,feature){
  const xs=p.filter(z=>z.bar>start&&z.bar<=end); if(!xs.length)return null;
  if(feature==='deltaMae')return Math.max(...xs.map(z=>z.mae))- (p.find(z=>z.bar===start)?.mae??0);
  if(feature==='deltaMfe')return Math.max(...xs.map(z=>z.mfe))- (p.find(z=>z.bar===start)?.mfe??0);
  return p.find(z=>z.bar===end)?.[feature] ?? null;
}

function rank(a){
  const s=a.map((x,i)=>({x,i})).sort((u,v)=>u.x-v.x); const r=Array(a.length); let k=0;
  while(k<s.length){let j=k+1;while(j<s.length&&s[j].x===s[k].x)j++;const avg=(k+j-1)/2+1;for(let q=k;q<j;q++)r[s[q].i]=avg;k=j;}
  return r;
}
function spearman(xs,ys){
  const rows=xs.map((x,i)=>({x,y:ys[i]})).filter(z=>Number.isFinite(z.x)&&Number.isFinite(z.y)); if(rows.length<5)return null;
  const rx=rank(rows.map(z=>z.x)),ry=rank(rows.map(z=>z.y)); const mx=mean(rx),my=mean(ry);
  let num=0,dx=0,dy=0;for(let i=0;i<rx.length;i++){const a=rx[i]-mx,b=ry[i]-my;num+=a*b;dx+=a*a;dy+=b*b;} return dx&&dy?num/Math.sqrt(dx*dy):null;
}

function quantileCuts(values,q=5){
  const xs=values.filter(Number.isFinite).sort((a,b)=>a-b); if(xs.length<q)return null;
  const cuts=[]; for(let k=1;k<q;k++){const pos=(xs.length-1)*k/q; const lo=Math.floor(pos),hi=Math.ceil(pos); cuts.push(xs[lo]+(xs[hi]-xs[lo])*(pos-lo));} return cuts;
}
function bucket(x,cuts){ if(!Number.isFinite(x)||!cuts)return null; let i=0;while(i<cuts.length&&x>cuts[i])i++;return i+1; }
function bucketStats(rows){
  const out=[];for(let b=1;b<=5;b++){const xs=rows.filter(r=>r.bucket===b);out.push({bucket:b,...stats(xs),featureMedian:xs.length?median(xs.map(r=>r.feature)):null});}return out;
}
const median = a => {const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const m=Math.floor(x.length/2);return x.length%2?x[m]:(x[m-1]+x[m])/2;};

async function loadBaseline(tf,candles){
  const report=JSON.parse(await readFile(resolve(BASE,`${tf}.json`),'utf8')); const cutoff=new Date(candles[PRE].timestamp);
  return (report.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<cutoff);
}

async function run(tf){
  const raw=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')); const candles=raw.candles??raw;
  if(candles.length<PRE)throw new Error(`${tf}: expected ${PRE} candles`);
  const baseline=await loadBaseline(tf,candles),map=new Map(baseline.map(t=>[key(t),t])),rows=[];
  for(let i=0;i<PRE;i++){
    const c=buildCandidate(candles,i);if(!c)continue;const t=map.get(key(c));if(!t)continue;const p=path(candles,c);if(p.length)rows.push({entryIndex:i,rMultiple:Number(t.rMultiple),p});
  }
  const analyses=[];
  for(const cp of CHECKPOINTS){
    for(const h of HORIZONS.filter(x=>x>cp)){
      for(const feature of FEATURES){
        const usable=rows.map(r=>({entryIndex:r.entryIndex,rMultiple:r.rMultiple,feature:featureAt(r.p,cp,feature)})).filter(r=>Number.isFinite(r.feature));
        const dev=usable.filter(r=>r.entryIndex<DEV),val=usable.filter(r=>r.entryIndex>=DEV);
        const cuts=quantileCuts(dev.map(r=>r.feature));
        const apply=val.map(r=>({...r,bucket:bucket(r.feature,cuts)})).filter(r=>r.bucket);
        const devRank=dev.length>=5?spearman(dev.map(r=>r.feature),dev.map(r=>r.rMultiple)):null;
        const valRank=val.length>=5?spearman(val.map(r=>r.feature),val.map(r=>r.rMultiple)):null;
        analyses.push({key:`T${cp}_H${h}_${feature}`,checkpoint:cp,horizon:h,feature,overall:{n:usable.length,spearman:spearman(usable.map(r=>r.feature),usable.map(r=>r.rMultiple))},dev:{n:dev.length,spearman:devRank,quintileCuts:cuts},val:{n:val.length,spearman:valRank,quintiles:bucketStats(apply)}});
      }
    }
  }
  const windows=[];for(let start=0;start<PRE;start+=BLOCK){const end=Math.min(PRE,start+BLOCK),label=start<DEV?`DEV_${String(start/BLOCK+1).padStart(2,'0')}`:`VAL_${String((start-DEV)/BLOCK+1).padStart(2,'0')}`;const wr=rows.filter(r=>r.entryIndex>=start&&r.entryIndex<end);windows.push({label,candleStart:start,candleEndExclusive:end,baseline:stats(wr),associations:CHECKPOINTS.flatMap(cp=>HORIZONS.filter(h=>h>cp).flatMap(h=>FEATURES.map(feature=>{const u=wr.map(r=>({feature:featureAt(r.p,cp,feature),rMultiple:r.rMultiple})).filter(x=>Number.isFinite(x.feature));return {key:`T${cp}_H${h}_${feature}`,n:u.length,spearman:spearman(u.map(x=>x.feature),u.map(x=>x.rMultiple))};})))});}
  const report={strategy:'Strategy A',mode:'DELAY1_CONTINUOUS_PATH_ASSOCIATION',timeframe:tf,scope:{preHoldoutCandles:PRE,devCandles:DEV,valCandles:PRE-DEV,blockCandles:BLOCK,delayExactly:1,checkpoints:CHECKPOINTS,horizons:HORIZONS,freshHoldoutExcluded:true},methodology:{purpose:'Test whether continuous post-entry path state has a stable monotonic association with final canonical outcome without selecting production thresholds.',features:FEATURES,association:'Spearman rank correlation between each continuous path feature at T1/T2/T3 and canonical final R multiple.',oos:'DEV quintile cutpoints are estimated once from DEV and applied unchanged to VAL; quintiles are descriptive only.',chronology:'Five fixed chronological 2,000-candle windows over the first 10,000 candles.',sameBarOHLC:'Canonical baseline outcome excludes AMBIGUOUS; no intrabar order is inferred.',noOptimization:true,diagnosticOnly:true,productionUntouched:true},overall:stats(rows),analyses,windows};
  await mkdir(OUT,{recursive:true});const file=resolve(OUT,`${tf}.json`);await writeFile(file,JSON.stringify(report,null,2));
  console.log(`\n=== ${tf} DELAY1 CONTINUOUS PATH ASSOCIATION ===`);console.log(`joined=${rows.length} AvgR=${report.overall.avgR?.toFixed(3)??'n/a'} PF=${report.overall.PF?.toFixed(3)??'n/a'}`);
  for(const a of analyses){console.log(`${a.key}: overall rho=${a.overall.spearman?.toFixed(3)??'n/a'} DEV rho=${a.dev.spearman?.toFixed(3)??'n/a'} VAL rho=${a.val.spearman?.toFixed(3)??'n/a'} VAL n=${a.val.n}`);}
  console.log('Chronological association summary:');for(const w of windows){const strongest=[...w.associations].filter(x=>Number.isFinite(x.spearman)).sort((a,b)=>Math.abs(b.spearman)-Math.abs(a.spearman)).slice(0,3);console.log(`${w.label}: ${strongest.map(x=>`${x.key}=${x.spearman.toFixed(3)}(n${x.n})`).join(' | ')||'n/a'}`);}
  console.log(`Report -> ${file}`);
}
for(const tf of ['1min','5min'])await run(tf);
