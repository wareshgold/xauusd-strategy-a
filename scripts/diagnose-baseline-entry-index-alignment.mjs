import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=resolve(fileURLToPath(new URL('..',import.meta.url)));
const candles=(JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[]);
const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PRE=10000;
const canonical=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));

function candleTime(c){return c?.timestamp??c?.time??c?.datetime??c?.dateTime??null;}
function priceOrientation(t){
 const entry=Number(t.entry),sl=Number(t.stopLoss),tp=Number(t.tp1);
 return t.direction==='BUY'?(sl<entry&&entry<tp):(tp<entry&&entry<sl);
}
const rows=canonical.map(t=>{
 const i=Number(t.entryIndex), c=candles[i];
 const ct=candleTime(c), expected=String(t.entryTime);
 return {entryIndex:i,entryTime:expected,candleTime:ct,timeMatch:ct===expected,direction:t.direction,entry:Number(t.entry),stopLoss:Number(t.stopLoss),tp1:Number(t.tp1),orientationValid:priceOrientation(t),result:t.result,rMultiple:Number(t.rMultiple)};
});
const timeMismatch=rows.filter(x=>!x.timeMatch),orientationMismatch=rows.filter(x=>!x.orientationValid);
const report={strategy:'Strategy A / SP2L',mode:'BASELINE_ENTRY_INDEX_ALIGNMENT_DIAGNOSTIC',timeframe:'5min',canonical:rows.length,candleCount:candles.length,timeAlignment:{mismatches:timeMismatch.length,matchRate:rows.length?1-timeMismatch.length/rows.length:null},priceOrientation:{mismatches:orientationMismatch.length,validRate:rows.length?1-orientationMismatch.length/rows.length:null},mismatchExamples:timeMismatch.slice(0,30),orientationExamples:orientationMismatch.slice(0,30),status:timeMismatch.length===0&&orientationMismatch.length===0?'ALIGNMENT_CONFIRMED':'ALIGNMENT_MISMATCH_FOUND'};
const outDir=resolve(ROOT,'data/reports/strategy-a-phase-counterfactual-direction-flip-audit');await mkdir(outDir,{recursive:true});const out=resolve(outDir,'entry-index-alignment-5min.json');await writeFile(out,JSON.stringify(report,null,2));
console.log(`PHASE_BASELINE_ENTRY_INDEX_ALIGNMENT 5min CANONICAL=${rows.length} TIME_MISMATCH=${timeMismatch.length} ORIENTATION_MISMATCH=${orientationMismatch.length}`);
console.log(`TIME_MATCH=${(report.timeAlignment.matchRate*100).toFixed(2)}% ORIENTATION_VALID=${(report.priceOrientation.validRate*100).toFixed(2)}%`);
for(const x of timeMismatch.slice(0,10))console.log(`TIME_MISMATCH index=${x.entryIndex} stored=${x.entryTime} candle=${x.candleTime} dir=${x.direction}`);
console.log(`REPORT=${out}`);
console.log(`STATUS=${report.status}`);
