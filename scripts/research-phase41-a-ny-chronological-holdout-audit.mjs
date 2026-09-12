import { execFileSync } from 'node:child_process';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PHASE40='scripts/research-phase40-a-ny-leave-one-out-robustness.mjs';
const OUT=resolve(ROOT,'data/reports/strategy-a-phase41-a-ny-chronological-holdout-audit');
execFileSync('node',[PHASE40],{cwd:ROOT,stdio:'inherit'});
const source=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-phase40-a-ny-leave-one-out-robustness/5min.json'),'utf8'));
const rows=[...(source.leaveOneOut??[])].length?null:null;
const phase40=source;
const overall=phase40.overall;
const fullRows=[];
for(const x of phase40.leaveOneOut??[]){}
// Reconstruct the original 15 observations from leave-one-out totals is not valid; use the Phase40 source report's embedded rows if available.
const report=await readFile(resolve(ROOT,'data/reports/strategy-a-phase40-a-ny-leave-one-out-robustness/5min.json'),'utf8');
if(!report.includes('removedR')) throw new Error('Phase40 report missing leave-one-out observations');
const loo=phase40.leaveOneOut;
const n=loo.length;
// Derive each original R exactly from overall totalR and the corresponding leave-one-out totalR.
for(const x of loo) fullRows.push({entryTime:x.removedEntryTime,r:overall.totalR-x.totalR});
fullRows.sort((a,b)=>a.entryTime.localeCompare(b.entryTime));
function stats(values){const v=values.filter(Number.isFinite),w=v.filter(x=>x>0),l=v.filter(x=>x<=0),gw=w.reduce((s,x)=>s+x,0),gl=Math.abs(l.reduce((s,x)=>s+x,0));return{n:v.length,WR:v.length?w.length/v.length:null,avgR:v.length?v.reduce((s,x)=>s+x,0)/v.length:null,PF:gl?gw/gl:null,totalR:v.reduce((s,x)=>s+x,0),positiveN:w.length,negativeN:l.length};}
function sliceStats(name,rows){return{name,...stats(rows.map(x=>x.r)),from:rows[0]?.entryTime??null,to:rows.at(-1)?.entryTime??null};}
const cut60=Math.floor(n*0.6),cut80=Math.floor(n*0.8);
const first60=fullRows.slice(0,cut60),middle20=fullRows.slice(cut60,cut80),last20=fullRows.slice(cut80),last40=fullRows.slice(cut60);
const result={strategy:phase40.strategy,mode:'PHASE41_A_NY_CHRONOLOGICAL_HOLDOUT_AUDIT',timeframe:'5min',sourcePhase:'Phase40 fixed A/New York counterfactual hypothesis',hypothesis:{archetype:'LOSS_A_NO_PRE_FAVORABLE',originalDirection:'BUY',session:'NEW_YORK',counterfactualDirection:'SELL',ruleChanged:false},overall,slices:{FIRST_60:sliceStats('FIRST_60',first60),MIDDLE_20:sliceStats('MIDDLE_20',middle20),LAST_20:sliceStats('LAST_20',last20),LAST_40:sliceStats('LAST_40',last40)},observations:fullRows,methodology:{researchOnly:true,noOptimization:true,noRuleChange:true,chronologicalOnly:true,warning:'This is a chronological holdout audit inside the existing 15-case sample, not a true external out-of-sample validation. The hypothesis was selected before this audit, but the available history is too short for a strong OOS claim.'},status:'COUNTERFACTUAL_ONLY_CHRONOLOGICAL_HOLDOUT_AUDIT'};
await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE41_A_NY_CHRONOLOGICAL_HOLDOUT_AUDIT N=${n}`);
for(const s of Object.values(result.slices)) console.log(`${s.name} N=${s.n} WR=${s.WR===null?'undefined':(s.WR*100).toFixed(2)+'%'} avgR=${s.avgR===null?'undefined':s.avgR.toFixed(6)} PF=${s.PF===null?'undefined':s.PF.toFixed(6)} totalR=${s.totalR.toFixed(6)} FROM=${s.from} TO=${s.to}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);console.log('STATUS=COUNTERFACTUAL_ONLY_CHRONOLOGICAL_HOLDOUT_AUDIT');