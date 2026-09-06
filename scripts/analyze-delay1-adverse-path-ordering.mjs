import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PRE=10000, DEV=6000, H=20;
const OUT=resolve(ROOT,'data/reports/strategy-a-adverse-path-ordering');
const finite=Number.isFinite;
const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
const pf=a=>{const w=a.filter(x=>x>0).reduce((s,x)=>s+x,0),l=-a.filter(x=>x<0).reduce((s,x)=>s+x,0);return l?w/l:null};
const wr=a=>a.length?a.filter(x=>x>0).length/a.length:null;
const stats=a=>({n:a.length,avgR:mean(a),PF:pf(a),WR:wr(a)});
const fmt=x=>x==null?'NA':x.toFixed(4);

function barExcursion(c,entry,risk,d){return {mae:(d==='BUY'?entry-c.low:c.high-entry)/risk,mfe:(d==='BUY'?c.high-entry:entry-c.low)/risk};}
function classifyPath(path){
  let maeState='S0_LT25', maxMae=0, firstGE1=null, firstMfe1=null, firstMfe2=null;
  const states=['S0_LT25','S1_25_50','S2_50_75','S3_75_100','S4_GE1'];
  for(const x of path){
    maxMae=Math.max(maxMae,x.mae);
    if(firstGE1==null&&x.mae>=1) firstGE1=x.h;
    if(firstMfe1==null&&x.mfe>=1) firstMfe1=x.h;
    if(firstMfe2==null&&x.mfe>=2) firstMfe2=x.h;
    maeState=x.mae<.25?'S0_LT25':x.mae<.5?'S1_25_50':x.mae<.75?'S2_50_75':x.mae<1?'S3_75_100':'S4_GE1';
  }
  const firstAdverse=path.find(x=>x.mae>0)?.h??null;
  const firstPositiveMfe=path.find(x=>x.mfe>0)?.h??null;
  const ge1=path.filter(x=>x.mae>=1);
  const hit=firstGE1;
  if(hit==null)return {firstGE1:null};
  const prior=path.filter(x=>x.h<hit);
  const priorMaxMfe=prior.length?Math.max(...prior.map(x=>x.mfe)):0;
  const priorMaxMae=prior.length?Math.max(...prior.map(x=>x.mae)):0;
  const mae1AfterMfe1=firstMfe1!=null&&firstMfe1<hit;
  const mae1AfterMfe2=firstMfe2!=null&&firstMfe2<hit;
  const acceleration=hit<=3?'EARLY_1_3':hit<=5?'MID_4_5':hit<=10?'LATE_6_10':'LATE_11_20';
  return {firstGE1:hit,acceleration,priorMaxMfe,priorMaxMae,mae1AfterMfe1,mae1AfterMfe2,firstMfe1,firstMfe2,firstAdverse,firstPositiveMfe};
}
function bucketName(r){
 if(r.event.firstGE1==null)return 'NO_1R';
 return r.event.acceleration;
}
function summarize(rows){
 const rs=rows.map(r=>r.rMultiple);
 return {outcome:stats(rs),n:rows.length,hit1r:rows.length?rows.filter(r=>r.event.firstGE1!=null).length:0,ex:rows.filter(r=>r.exceptional).length};
}
async function main(){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')); const candles=raw.candles??raw;
 const base=(JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8')).trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE);
 const rows=[];
 for(const t of base){
  const i=Number(t.entryIndex),entry=Number(t.entry),risk=Math.abs(entry-Number(t.stopLoss)); if(!(risk>0)||!candles[i+H])continue;
  const path=[];for(let h=1;h<=H;h++)path.push({h,...barExcursion(candles[i+h],entry,risk,t.direction)});
  rows.push({entryIndex:i,direction:t.direction,rMultiple:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,dev:i<DEV,event:classifyPath(path)});
 }
 const hit=rows.filter(r=>r.event.firstGE1!=null);
 const buckets=['EARLY_1_3','MID_4_5','LATE_6_10','LATE_11_20'];
 const report={scope:{baselinePreHoldout:PRE,devCutoff:DEV,pathHorizon:H,trigger:'first cumulative MAE >=1R',ordering:'prior MFE state before first >=1R MAE',freshHoldoutAccessed:false},integrity:{baselinePre:base.length,complete:rows.length,deterministic:true},methodology:{fixedState:true,existingBandsOnly:true,noThresholdOptimization:true,noHorizonSelection:true,noExitRuleCreation:true,noBrokerExecutionModel:true,diagnosticOnly:true,productionUntouched:true}};
 report.overall=summarize(rows);
 report.hit1r=summarize(hit);
 report.hitTiming={};
 for(const b of buckets){const rs=hit.filter(r=>r.event.acceleration===b);report.hitTiming[b]=summarize(rs);}
 report.ordering={};
 for(const key of ['MFE_BEFORE_1R','NO_MFE_BEFORE_1R']){const rs=hit.filter(r=>key==='MFE_BEFORE_1R'?r.event.mae1AfterMfe1:!r.event.mae1AfterMfe1);report.ordering[key]=summarize(rs);}
 report.ordering.mfe2Before1R=summarize(hit.filter(r=>r.event.mae1AfterMfe2));
 report.ordering.noMfe2Before1R=summarize(hit.filter(r=>!r.event.mae1AfterMfe2));
 report.devVal={};for(const k of ['DEV','VAL','DEV_NO_EX','VAL_NO_EX']){const rs=hit.filter(r=>k==='DEV'?r.dev:k==='VAL'?!r.dev&&r.entryIndex<PRE:k==='DEV_NO_EX'?r.dev&&!r.exceptional:!r.dev&&r.entryIndex<PRE&&!r.exceptional);report.devVal[k]=summarize(rs);}
 report.byDirection={};for(const d of ['BUY','SELL'])report.byDirection[d]=summarize(hit.filter(r=>r.direction===d));
 await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
 console.log(`PHASE_11D_ADVERSE_PATH_ORDERING N=${base.length} HIT_1R=${hit.length} DEV=${hit.filter(r=>r.dev).length} VAL=${hit.filter(r=>!r.dev&&r.entryIndex<PRE).length} FRESH=LOCKED`);
 console.log(`INTEGRITY baselinePre=${base.length} complete=${rows.length} deterministic=true`);
 console.log(`HIT_1R avgR=${fmt(report.hit1r.outcome.avgR)} PF=${fmt(report.hit1r.outcome.PF)} WR=${(report.hit1r.outcome.WR*100).toFixed(2)}% EX=${report.hit1r.ex}`);
 for(const b of buckets){const x=report.hitTiming[b];console.log(`${b}: N=${x.n} avgR=${fmt(x.outcome.avgR)} PF=${fmt(x.outcome.PF)} WR=${(x.outcome.WR*100).toFixed(2)}%`)}
 for(const [k,x] of Object.entries(report.ordering))console.log(`${k}: N=${x.n} avgR=${fmt(x.outcome.avgR)} PF=${fmt(x.outcome.PF)} WR=${(x.outcome.WR*100).toFixed(2)}%`);
 console.log('=== DEV / VAL ===');for(const [k,x] of Object.entries(report.devVal))console.log(`${k}: N=${x.n} avgR=${fmt(x.outcome.avgR)} PF=${fmt(x.outcome.PF)} WR=${(x.outcome.WR*100).toFixed(2)}%`);
 console.log('=== DIRECTION ===');for(const [k,x] of Object.entries(report.byDirection))console.log(`${k}: N=${x.n} avgR=${fmt(x.outcome.avgR)} PF=${fmt(x.outcome.PF)} WR=${(x.outcome.WR*100).toFixed(2)}%`);
 console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_HORIZON_SELECTION NO_RULE NO_FRESH');
}
main().catch(e=>{console.error(e);process.exitCode=1});
