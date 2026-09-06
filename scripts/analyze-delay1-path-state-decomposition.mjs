import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const BASE=resolve(ROOT,'data/reports/strategy-a-baseline');
const FIXED=resolve(ROOT,'data/reports/strategy-a-delay1-fixed-horizon-exit-economics');
const OUT=resolve(ROOT,'data/reports/strategy-a-delay1-path-state-decomposition');
const PRE=10000,DEV=6000,H=20;
const finite=Number.isFinite;
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
const pf=rs=>{const w=rs.filter(x=>x>0).reduce((a,b)=>a+b,0),l=-rs.filter(x=>x<0).reduce((a,b)=>a+b,0);return l?w/l:null};
const stats=rs=>({n:rs.length,avgR:mean(rs),PF:pf(rs),WR:rs.length?rs.filter(x=>x>0).length/rs.length:null});
const key=t=>`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
const fixedState=x=>x<.25?'S0_LT25':x<.5?'S1_25_50':x<.75?'S2_50_75':x<1?'S3_75_100':'S4_GE1';
const phase=x=>x===0?'FLAT':x>0?'POSITIVE':'NEGATIVE';

async function run(){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8'));
 const candles=raw.candles??raw;
 const baseline=JSON.parse(await readFile(resolve(BASE,'5min.json'),'utf8')).trades??[];
 const fixed=JSON.parse(await readFile(resolve(FIXED,'5m.json'),'utf8'));
 if(fixed.integrity?.matched!==144||fixed.integrity?.rows!==144)throw new Error('Phase 10F integrity is not 144/144; refusing Phase 11.');
 const indices=[...new Set(fixed.delay1EntryIndices??[])].sort((a,b)=>a-b);
 if(indices.length!==144)throw new Error(`Expected 144 DELAY1 indices, got ${indices.length}.`);
 const usable=baseline.filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE);
 const map=new Map(usable.map(t=>[key(t),t]));
 const rows=[];
 for(const i of indices){
   const t=usable.find(x=>Number(x.entryIndex)===i);
   if(!t)throw new Error(`Missing baseline DELAY1 row at index ${i}.`);
   const entry=Number(t.entry),stop=Number(t.stopLoss),risk=Math.abs(entry-stop);
   if(!(risk>0))throw new Error(`Invalid risk at index ${i}.`);
   const path=[];
   for(let h=1;h<=H;h++){
     const c=candles[i+h];
     if(!c)throw new Error(`Incomplete path at index ${i}.`);
     const mae=(t.direction==='BUY'?entry-c.low:c.high-entry)/risk;
     const mfe=(t.direction==='BUY'?c.high-entry:entry-c.low)/risk;
     path.push({h,mae,mfe,net:(t.direction==='BUY'?c.close-entry:entry-c.close)/risk});
   }
   const early={};
   for(const h of [1,3,5,10]){const p=path.slice(0,h);early[`t${h}`]={mae:Math.max(...p.map(x=>x.mae)),mfe:Math.max(...p.map(x=>x.mfe)),net:p[p.length-1].net};}
   const stateAt={};
   for(const h of [3,5,10])stateAt[`t${h}`]=fixedState(early[`t${h}`].mae);
   const final=path[19];
   const laterRecovery={};
   for(const h of [3,5,10]){const later=path.slice(h);laterRecovery[`t${h}`]={mfe:Math.max(...later.map(x=>x.mfe)),mae:Math.max(...later.map(x=>x.mae))};}
   rows.push({entryIndex:i,direction:t.direction,rMultiple:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,path,early,stateAt,laterRecovery,finalNet:final.net});
 }
 const populations={ALL:rows,NO_EXCEPTIONAL:rows.filter(r=>!r.exceptional),DEV:rows.filter(r=>r.entryIndex<DEV),VAL:rows.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE)};
 const describe=(rs,fn)=>stats(rs.map(fn));
 const stateTables={};
 for(const h of [3,5,10]){
   const states=['S0_LT25','S1_25_50','S2_50_75','S3_75_100','S4_GE1'];
   stateTables[`T${h}`]={};
   for(const s of states){const all=rows.filter(r=>r.stateAt[`t${h}`]===s),dev=all.filter(r=>r.entryIndex<DEV),val=all.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE),normal=all.filter(r=>!r.exceptional);stateTables[`T${h}`][s]={n:all.length,devN:dev.length,valN:val.length,all:stats(all.map(r=>r.rMultiple)),noExceptional:stats(normal.map(r=>r.rMultiple)),dev:stats(dev.map(r=>r.rMultiple)),val:stats(val.map(r=>r.rMultiple)),exceptional:all.filter(r=>r.exceptional).length,laterMFE:stats(all.map(r=>r.laterRecovery[`t${h}`].mfe)),laterMAE:stats(all.map(r=>r.laterRecovery[`t${h}`].mae))};}
 }
 const transitions={};
 for(const [a,b] of [[3,5],[3,10],[5,10]]){const table={};for(const s of ['S0_LT25','S1_25_50','S2_50_75','S3_75_100','S4_GE1']){const subset=rows.filter(r=>r.stateAt[`t${a}`]===s);const counts={};for(const r of subset){const z=r.stateAt[`t${b}`];counts[z]=(counts[z]??0)+1;}table[s]={n:subset.length,counts};}transitions[`T${a}_TO_T${b}`]=table;}
 const direction={};for(const d of ['BUY','SELL']){const rs=rows.filter(r=>r.direction===d);direction[d]={n:rs.length,dev:rs.filter(r=>r.entryIndex<DEV).length,val:rs.filter(r=>r.entryIndex>=DEV).length,outcome:stats(rs.map(r=>r.rMultiple)),t3:describe(rs,r=>r.early.t3.mae),t5:describe(rs,r=>r.early.t5.mae),t10:describe(rs,r=>r.early.t10.mae)};}
 const report={strategy:'Strategy A',mode:'DELAY1_PATH_STATE_DECOMPOSITION',timeframe:'5min',scope:{preHoldoutCandles:PRE,devCutoff:DEV,pathHorizon:H,stateHorizons:[3,5,10],fixedStateBands:['<0.25R','0.25-0.50R','0.50-0.75R','0.75-1.00R','>=1.00R'],freshHoldoutAccessed:false},integrity:{baselinePre:usable.length,delay1:indices.length,matched:rows.length,rows:rows.length,devN:91,valN:53,pathComplete:true,deterministic:true},methodology:{purpose:'Descriptive decomposition of early cumulative MAE states, later recovery, and state transitions using fixed ex-ante bands.',statesFixedExAnte:true,noThresholdOptimization:true,noHorizonSelection:true,noExitRuleCreation:true,noBrokerExecutionModel:true,baselineOutcomeRetainedSeparately:true,freshHoldoutExcluded:true,productionUntouched:true},stateTables,transitions,direction};
 await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
 console.log(`PHASE_11_PATH_STATE_DECOMPOSITION N=144 DEV=91 VAL=53 FRESH=LOCKED`);
 console.log(`INTEGRITY baselinePre=${usable.length} delay1=144 matched=144 pathComplete=true deterministic=true`);
 for(const h of [3,5,10]){console.log(`T${h} STATES:`);for(const s of ['S0_LT25','S1_25_50','S2_50_75','S3_75_100','S4_GE1']){const x=stateTables[`T${h}`][s];console.log(`${s} N=${x.n} DEV=${x.devN} VAL=${x.valN} | ALL avgR=${x.all.avgR?.toFixed(4)??'NA'} PF=${x.all.PF?.toFixed(4)??'NA'} | DEV=${x.dev.avgR?.toFixed(4)??'NA'} | VAL=${x.val.avgR?.toFixed(4)??'NA'} | LATER_MFE=${x.laterMFE.avgR?.toFixed(4)??'NA'}`)}}
 console.log('=== TRANSITIONS ===');for(const [name,t] of Object.entries(transitions)){console.log(name);for(const [s,x] of Object.entries(t))console.log(`${s} N=${x.n} ${JSON.stringify(x.counts)}`)}
 console.log('=== DIRECTION ===');for(const [d,x] of Object.entries(direction))console.log(`${d} N=${x.n} DEV=${x.dev} VAL=${x.val} avgR=${x.outcome.avgR?.toFixed(4)??'NA'} | t3Sp=${x.t3?.avgR}`);
 console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_HORIZON_SELECTION NO_RULE NO_FRESH');
}
run().catch(e=>{console.error(e);process.exitCode=1});
