import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const BASE=resolve(ROOT,'data/reports/strategy-a-baseline');
const OUT=resolve(ROOT,'data/reports/strategy-a-delay1-path-state-independence');
const PRE=10000,DEV=6000,H=20;
const finite=Number.isFinite;
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
const pf=rs=>{const w=rs.filter(x=>x>0).reduce((a,b)=>a+b,0),l=-rs.filter(x=>x<0).reduce((a,b)=>a+b,0);return l?w/l:null};
const stats=rs=>({n:rs.length,avgR:mean(rs),PF:pf(rs),WR:rs.length?rs.filter(x=>x>0).length/rs.length:null});
const state=x=>x<.25?'S0_LT25':x<.5?'S1_25_50':x<.75?'S2_50_75':x<1?'S3_75_100':'S4_GE1';
const states=['S0_LT25','S1_25_50','S2_50_75','S3_75_100','S4_GE1'];
const horizons=[3,5,10];

async function run(){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8'));
 const candles=raw.candles??raw;
 const baseline=JSON.parse(await readFile(resolve(BASE,'5min.json'),'utf8')).trades??[];
 const usable=baseline.filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE);
 const rows=[];
 for(const t of usable){
   const i=Number(t.entryIndex),entry=Number(t.entry),stop=Number(t.stopLoss),risk=Math.abs(entry-stop);
   if(!(risk>0)||!candles[i+H])continue;
   const path=[];
   for(let h=1;h<=H;h++){
     const c=candles[i+h];
     if(!c)break;
     const mae=(t.direction==='BUY'?entry-c.low:c.high-entry)/risk;
     const mfe=(t.direction==='BUY'?c.high-entry:entry-c.low)/risk;
     path.push({h,mae,mfe});
   }
   if(path.length!==H)continue;
   const statesAt={};
   for(const h of horizons)statesAt[`t${h}`]=state(Math.max(...path.slice(0,h).map(x=>x.mae)));
   rows.push({entryIndex:i,direction:t.direction,rMultiple:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,statesAt});
 }
 const delay1Baseline=usable.filter(t=>Number(t.entryIndex)>0);
 if(rows.length!==210)throw new Error(`Expected 210 complete baseline rows, got ${rows.length}.`);
 const report={strategy:'Strategy A',mode:'DELAY1_PATH_STATE_INDEPENDENCE',timeframe:'5min',scope:{preHoldoutCandles:PRE,devCutoff:DEV,pathHorizon:H,stateHorizons:horizons,fixedStateBands:['<0.25R','0.25-0.50R','0.50-0.75R','0.75-1.00R','>=1.00R'],freshHoldoutAccessed:false},integrity:{baselinePre:usable.length,complete:rows.length,devN:rows.filter(r=>r.entryIndex<DEV).length,valN:rows.filter(r=>r.entryIndex>=DEV).length,freshHoldoutExcluded:true},methodology:{purpose:'Test whether fixed early MAE states provide outcome separation beyond simple retrospective MAE association.',statesFixedExAnte:true,noThresholdOptimization:true,noHorizonSelection:true,noExitRuleCreation:true,noBrokerExecutionModel:true,diagnosticOnly:true,productionUntouched:true},horizons:{},direction:{}};
 for(const h of horizons){
   const table={};
   for(const s of states){
     const all=rows.filter(r=>r.statesAt[`t${h}`]===s),dev=all.filter(r=>r.entryIndex<DEV),val=all.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE),noEx=all.filter(r=>!r.exceptional);
     table[s]={all:stats(all.map(r=>r.rMultiple)),noExceptional:stats(noEx.map(r=>r.rMultiple)),dev:stats(dev.map(r=>r.rMultiple)),val:stats(val.map(r=>r.rMultiple)),devNoExceptional:stats(dev.filter(r=>!r.exceptional).map(r=>r.rMultiple)),valNoExceptional:stats(val.filter(r=>!r.exceptional).map(r=>r.rMultiple)),exceptional:all.filter(r=>r.exceptional).length};
   }
   report.horizons[`T${h}`]=table;
 }
 for(const d of ['BUY','SELL']){const rs=rows.filter(r=>r.direction===d);report.direction[d]={n:rs.length,dev:rs.filter(r=>r.entryIndex<DEV).length,val:rs.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE).length,outcome:stats(rs.map(r=>r.rMultiple))};}
 await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
 console.log(`PHASE_11B_STATE_INDEPENDENCE N=${rows.length} DEV=${report.integrity.devN} VAL=${report.integrity.valN} FRESH=LOCKED`);
 console.log(`INTEGRITY baselinePre=${usable.length} complete=${rows.length} deterministic=true`);
 for(const h of horizons){console.log(`T${h} STATE | ALL / DEV / VAL / DEV_NO_EX / VAL_NO_EX`);for(const s of states){const x=report.horizons[`T${h}`][s];const f=z=>z==null?'NA':z.toFixed(4);console.log(`${s} N=${x.all.n} | ${f(x.all.avgR)} / ${f(x.dev.avgR)} / ${f(x.val.avgR)} / ${f(x.devNoExceptional.avgR)} / ${f(x.valNoExceptional.avgR)} | EX=${x.exceptional}`)}}
 console.log('=== DIRECTION ===');for(const [d,x] of Object.entries(report.direction))console.log(`${d} N=${x.n} DEV=${x.dev} VAL=${x.val} avgR=${x.outcome.avgR?.toFixed(4)??'NA'}`);
 console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_HORIZON_SELECTION NO_RULE NO_FRESH');
}
run().catch(e=>{console.error(e);process.exitCode=1});
