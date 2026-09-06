import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PRE=10000, DEV=6000, H=20;
const BASE=resolve(ROOT,'data/reports/strategy-a-baseline');
const OUT=resolve(ROOT,'data/reports/strategy-a-recovery-vs-failure-after-1r');
const finite=Number.isFinite;
const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
const pf=a=>{const w=a.filter(x=>x>0).reduce((s,x)=>s+x,0),l=-a.filter(x=>x<0).reduce((s,x)=>s+x,0);return l?w/l:null};
const stats=a=>({n:a.length,avgR:mean(a),PF:pf(a),WR:a.length?a.filter(x=>x>0).length/a.length:null});

function excursion(c,entry,risk,d){return {mae:(d==='BUY'?entry-c.low:c.high-entry)/risk,mfe:(d==='BUY'?c.high-entry:entry-c.low)/risk};}
function eventState(path,d){
  const hit=path.findIndex(x=>x.mae>=1);
  if(hit<0)return null;
  const later=path.slice(hit+1);
  const recovery1=later.some(x=>x.mfe>=1), recovery2=later.some(x=>x.mfe>=2);
  const firstRecovery1=later.find(x=>x.mfe>=1)?.h??null;
  const firstRecovery2=later.find(x=>x.mfe>=2)?.h??null;
  const maeAt1=path[hit].mae;
  const postMaxMfe=later.length?Math.max(...later.map(x=>x.mfe)):0;
  const postMinMae=later.length?Math.max(...later.map(x=>x.mae)):maeAt1;
  return {hitBar:path[hit].h,maeAt1,recovery1,recovery2,firstRecovery1,firstRecovery2,postMaxMfe,postMaxMae:postMinMae,laterBars:later.length};
}

async function run(){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8'));
 const candles=raw.candles??raw;
 const base=(JSON.parse(await readFile(resolve(BASE,'5min.json'),'utf8')).trades??[])
   .filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE);
 const rows=[];
 for(const t of base){
   const i=Number(t.entryIndex),entry=Number(t.entry),risk=Math.abs(entry-Number(t.stopLoss));
   if(!(risk>0)||!candles[i+H])continue;
   const path=[];for(let h=1;h<=H;h++)path.push({h,...excursion(candles[i+h],entry,risk,t.direction)});
   const e=eventState(path,t.direction);if(e)rows.push({entryIndex:i,direction:t.direction,rMultiple:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,dev:i<DEV,event:e});
 }
 if(rows.length<1)throw new Error('No complete baseline rows with >=1R MAE found.');
 const hitRows=rows;
 const report={scope:{baselinePreHoldout:PRE,devCutoff:DEV,pathHorizon:H,triggerState:'first cumulative MAE >=1R',recoveryDefinition:'strictly later bars reach cumulative MFE >=1R or >=2R',freshHoldoutAccessed:false},integrity:{baselinePre:base.length,completeBaseline:base.length,adverseHitRows:hitRows.length,deterministic:true},methodology:{fixedState:true,noThresholdOptimization:true,noHorizonSelection:true,noExitRuleCreation:true,noBrokerExecutionModel:true,diagnosticOnly:true,productionUntouched:true}};
 const populations={ALL:hitRows,NO_EXCEPTIONAL:hitRows.filter(r=>!r.exceptional),DEV:hitRows.filter(r=>r.dev),VAL:hitRows.filter(r=>!r.dev&&r.entryIndex<PRE),DEV_NO_EXCEPTIONAL:hitRows.filter(r=>r.dev&&!r.exceptional),VAL_NO_EXCEPTIONAL:hitRows.filter(r=>!r.dev&&r.entryIndex<PRE&&!r.exceptional)};
 report.populations={};for(const [k,rs] of Object.entries(populations))report.populations[k]={outcome:stats(rs.map(r=>r.rMultiple)),recovery1:rs.length?rs.filter(r=>r.event.recovery1).length/rs.length:null,recovery2:rs.length?rs.filter(r=>r.event.recovery2).length/rs.length:null};
 report.byHitTiming={};for(const bucket of ['1-3','4-5','6-10','11-20']){const rs=hitRows.filter(r=>{const h=r.event.hitBar;return bucket==='1-3'?h<=3:bucket==='4-5'?h>=4&&h<=5:bucket==='6-10'?h>=6&&h<=10:h>=11});report.byHitTiming[bucket]={n:rs.length,outcome:stats(rs.map(r=>r.rMultiple)),recovery1:rs.length?rs.filter(r=>r.event.recovery1).length/rs.length:null,recovery2:rs.length?rs.filter(r=>r.event.recovery2).length/rs.length:null};}
 report.byDirection={};for(const d of ['BUY','SELL']){const rs=hitRows.filter(r=>r.direction===d);report.byDirection[d]={n:rs.length,outcome:stats(rs.map(r=>r.rMultiple)),recovery1:rs.length?rs.filter(r=>r.event.recovery1).length/rs.length:null,recovery2:rs.length?rs.filter(r=>r.event.recovery2).length/rs.length:null};}
 await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
 console.log(`PHASE_11C_RECOVERY_VS_FAILURE N=${base.length} HIT_1R=${hitRows.length} DEV=${populations.DEV.length} VAL=${populations.VAL.length} FRESH=LOCKED`);
 console.log(`INTEGRITY baselinePre=${base.length} complete=${base.length} adverseHitRows=${hitRows.length} deterministic=true`);
 for(const [k,x] of Object.entries(report.populations)){const f=v=>v==null?'NA':(v*100).toFixed(2)+'%';console.log(`${k}: N=${x.outcome.n} avgR=${x.outcome.avgR?.toFixed(4)??'NA'} PF=${x.outcome.PF?.toFixed(4)??'NA'} WR=${x.outcome.WR==null?'NA':(x.outcome.WR*100).toFixed(2)+'%'} | REC1=${f(x.recovery1)} REC2=${f(x.recovery2)}`)}
 console.log('=== FIRST >=1R MAE HIT TIMING ===');for(const [k,x] of Object.entries(report.byHitTiming))console.log(`${k}: N=${x.n} avgR=${x.outcome.avgR?.toFixed(4)??'NA'} REC1=${x.recovery1==null?'NA':(x.recovery1*100).toFixed(2)+'%'} REC2=${x.recovery2==null?'NA':(x.recovery2*100).toFixed(2)+'%'}`);
 console.log('=== DIRECTION ===');for(const [d,x] of Object.entries(report.byDirection))console.log(`${d}: N=${x.n} avgR=${x.outcome.avgR?.toFixed(4)??'NA'} REC1=${x.recovery1==null?'NA':(x.recovery1*100).toFixed(2)+'%'} REC2=${x.recovery2==null?'NA':(x.recovery2*100).toFixed(2)+'%'}`);
 console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_HORIZON_SELECTION NO_RULE NO_FRESH');
}
run().catch(e=>{console.error(e);process.exitCode=1});
