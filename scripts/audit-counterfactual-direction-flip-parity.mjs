import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=resolve(fileURLToPath(new URL('..',import.meta.url)));
const candles=(JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[]);
const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PRE=10000;

function simulate(entryIndex,entry,sl,tp,direction){
 for(let i=entryIndex+1;i<candles.length;i++){
  const c=candles[i],high=Number(c.high),low=Number(c.low);
  const hitSL=direction==='BUY'?low<=sl:high>=sl;
  const hitTP=direction==='BUY'?high>=tp:low<=tp;
  if(hitSL&&hitTP)return {result:'AMBIGUOUS',exitIndex:i,r:null};
  if(hitSL)return {result:'SL',exitIndex:i,r:-1};
  if(hitTP)return {result:'TP1',exitIndex:i,r:Math.abs(tp-entry)/Math.abs(entry-sl)};
 }
 return {result:'OPEN_END',exitIndex:null,r:null};
}

function equivalent(a,b){
 if(a.result!==b.result)return false;
 if(a.r==null||b.r==null)return a.r===b.r;
 return Math.abs(a.r-b.r)<1e-9;
}

const canonical=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
const rows=[];
for(const t of canonical){
 const entryIndex=Number(t.entryIndex),entry=Number(t.entry),sl=Number(t.stopLoss),tp=Number(t.tp1),direction=t.direction;
 const original=simulate(entryIndex,entry,sl,tp,direction);
 const risk=Math.abs(entry-sl),reward=Math.abs(tp-entry),flipDirection=direction==='BUY'?'SELL':'BUY';
 const flipSL=flipDirection==='BUY'?entry-risk:entry+risk;
 const flipTP=flipDirection==='BUY'?entry+reward:entry-reward;
 const flipped=simulate(entryIndex,entry,flipSL,flipTP,flipDirection);
 rows.push({entryIndex,entryTime:t.entryTime,direction,storedResult:t.result,storedR:Number(t.rMultiple),replayedResult:original.result,replayedR:original.r,originalParity:equivalent({result:t.result,r:Number(t.rMultiple)},original),flipDirection,flipSL,flipTP,flippedResult:flipped.result,flippedR:flipped.r,flipExitIndex:flipped.exitIndex});
}

const originalMismatches=rows.filter(x=>!x.originalParity);
const flipWins=rows.filter(x=>x.flippedR>0),flipLosses=rows.filter(x=>x.flippedR<=0),flipAmbiguous=rows.filter(x=>x.flippedResult==='AMBIGUOUS'),flipOpen=rows.filter(x=>x.flippedResult==='OPEN_END');
const byOriginalDirection={BUY:rows.filter(x=>x.direction==='BUY'),SELL:rows.filter(x=>x.direction==='SELL')};
function summary(rs){const resolved=rs.filter(x=>Number.isFinite(x.flippedR));return{n:rs.length,resolved:resolved.length,wins:resolved.filter(x=>x.flippedR>0).length,losses:resolved.filter(x=>x.flippedR<=0).length,avgR:resolved.length?resolved.reduce((s,x)=>s+x.flippedR,0)/resolved.length:null};}
const report={strategy:'Strategy A / SP2L',mode:'COUNTERFACTUAL_DIRECTION_FLIP_PARITY_AUDIT',timeframe:'5min',canonical:canonical.length,originalReplay:{mismatches:originalMismatches.length,expected:canonical.length,actual:canonical.length,parityRate:canonical.length?1-originalMismatches.length/canonical.length:null},flip:{resolved:flipWins.length+flipLosses.length,ambiguous:flipAmbiguous.length,openEnd:flipOpen.length,wins:flipWins.length,losses:flipLosses.length,byOriginalDirection:{BUY:summary(byOriginalDirection.BUY),SELL:summary(byOriginalDirection.SELL)}},methodology:'Independent OHLC replay of both the stored canonical direction and its mirrored counterfactual using identical entryIndex+1 start timing. The original replay is the validation gate: if stored baseline outcomes cannot be reproduced, the flip result is not accepted as a valid counterfactual.',status:originalMismatches.length===0?'PARITY_CONFIRMED_COUNTERFACTUAL_REVIEW_REQUIRED':'PARITY_FAILED_DO_NOT_TRUST_FLIP',mismatchExamples:originalMismatches.slice(0,20),rows};
const outDir=resolve(ROOT,'data/reports/strategy-a-phase-counterfactual-direction-flip-audit');await mkdir(outDir,{recursive:true});const out=resolve(outDir,'parity-5min.json');await writeFile(out,JSON.stringify(report,null,2));
console.log(`PHASE_COUNTERFACTUAL_DIRECTION_FLIP_PARITY 5min CANONICAL=${canonical.length} ORIGINAL_MISMATCH=${originalMismatches.length} FLIP_RESOLVED=${flipWins.length+flipLosses.length} FLIP_AMBIGUOUS=${flipAmbiguous.length} FLIP_OPEN_END=${flipOpen.length}`);
console.log(`ORIGINAL_PARITY=${canonical.length?((canonical.length-originalMismatches.length)/canonical.length*100).toFixed(2):'n/a'}%`);
console.log(`FLIP_FROM_ORIGINAL_BUY N=${summary(byOriginalDirection.BUY).n} W=${summary(byOriginalDirection.BUY).wins} L=${summary(byOriginalDirection.BUY).losses} avgR=${summary(byOriginalDirection.BUY).avgR?.toFixed(6)}`);
console.log(`FLIP_FROM_ORIGINAL_SELL N=${summary(byOriginalDirection.SELL).n} W=${summary(byOriginalDirection.SELL).wins} L=${summary(byOriginalDirection.SELL).losses} avgR=${summary(byOriginalDirection.SELL).avgR?.toFixed(6)}`);
console.log(`REPORT=${out}`);
console.log(`STATUS=${report.status}`);
