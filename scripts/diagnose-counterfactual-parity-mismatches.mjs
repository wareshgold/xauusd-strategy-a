import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=resolve(fileURLToPath(new URL('..',import.meta.url)));
const candles=(JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[]);
const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PRE=10000;

function simulate(t){
 const entryIndex=Number(t.entryIndex),entry=Number(t.entry),sl=Number(t.stopLoss),tp1=Number(t.tp1),tp2=t.tp2==null?undefined:Number(t.tp2),risk=Math.abs(entry-sl);
 for(let i=entryIndex+1;i<candles.length;i++){
  const c=candles[i],high=Number(c.high),low=Number(c.low);
  const hitSL=t.direction==='BUY'?low<=sl:high>=sl;
  const hitTP1=t.direction==='BUY'?high>=tp1:low<=tp1;
  const hitTP2=tp2===undefined?false:(t.direction==='BUY'?high>=tp2:low<=tp2);
  if(hitSL&&(hitTP1||hitTP2))return{result:'AMBIGUOUS',r:null,exitIndex:i};
  if(hitSL)return{result:'SL',r:-1,exitIndex:i};
  if(hitTP2)return{result:'TP2',r:Math.abs(tp2-entry)/risk,exitIndex:i};
  if(hitTP1)return{result:'TP1',r:Math.abs(tp1-entry)/risk,exitIndex:i};
 }
 return{result:'OPEN',r:null,exitIndex:null};
}
function key(x){return `${x.storedResult}->${x.replayedResult}`;}
const canonical=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
const rows=canonical.map(t=>{const r=simulate(t);return{entryIndex:Number(t.entryIndex),entryTime:t.entryTime,direction:t.direction,entry:Number(t.entry),stopLoss:Number(t.stopLoss),tp1:Number(t.tp1),tp2:t.tp2==null?null:Number(t.tp2),storedResult:t.result,storedR:Number(t.rMultiple),replayedResult:r.result,replayedR:r.r,replayedExitIndex:r.exitIndex,storedExitIndex:t.exitIndex??null,rDelta:Number.isFinite(r.r)?r.r-Number(t.rMultiple):null,parity:r.result===t.result&&((r.r==null&&t.rMultiple==null)||Math.abs(r.r-Number(t.rMultiple))<1e-9)};});
const mismatches=rows.filter(x=>!x.parity);
const counts=Object.fromEntries([...new Set(mismatches.map(key))].sort().map(k=>[k,mismatches.filter(x=>key(x)===k).length]));
const byDirection={BUY:mismatches.filter(x=>x.direction==='BUY').length,SELL:mismatches.filter(x=>x.direction==='SELL').length};
const byStoredResult=Object.fromEntries([...new Set(mismatches.map(x=>x.storedResult))].sort().map(k=>[k,mismatches.filter(x=>x.storedResult===k).length]));
const byReplayResult=Object.fromEntries([...new Set(mismatches.map(x=>x.replayedResult))].sort().map(k=>[k,mismatches.filter(x=>x.replayedResult===k).length]));
const report={strategy:'Strategy A / SP2L',mode:'COUNTERFACTUAL_PARITY_MISMATCH_DIAGNOSTIC',timeframe:'5min',canonical:canonical.length,mismatches:mismatches.length,parityRate:(canonical.length-mismatches.length)/canonical.length,summary:{byDirection,byStoredResult,byReplayResult,transitionCounts:counts,storedExitIndexMissing:mismatches.filter(x=>x.storedExitIndex==null).length,replayExitIndexMissing:mismatches.filter(x=>x.replayedExitIndex==null).length},mismatchExamples:mismatches.slice(0,30),rows:mismatches};
const outDir=resolve(ROOT,'data/reports/strategy-a-phase-counterfactual-direction-flip-audit');await mkdir(outDir,{recursive:true});const out=resolve(outDir,'parity-mismatch-diagnostic-5min.json');await writeFile(out,JSON.stringify(report,null,2));
console.log(`PHASE_COUNTERFACTUAL_PARITY_MISMATCH_DIAGNOSTIC 5min CANONICAL=${canonical.length} MISMATCH=${mismatches.length}`);
console.log(`BY_DIRECTION BUY=${byDirection.BUY} SELL=${byDirection.SELL}`);
console.log(`BY_STORED_RESULT ${JSON.stringify(byStoredResult)}`);
console.log(`BY_REPLAY_RESULT ${JSON.stringify(byReplayResult)}`);
console.log(`TRANSITIONS ${JSON.stringify(counts)}`);
console.log(`STORED_EXIT_INDEX_MISSING=${report.summary.storedExitIndexMissing} REPLAY_EXIT_INDEX_MISSING=${report.summary.replayExitIndexMissing}`);
console.log(`REPORT=${out}`);
console.log('STATUS=DIAGNOSTIC_ONLY_NO_RULE_CHANGE');
