import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=resolve(fileURLToPath(new URL('..',import.meta.url)));
const candles=(JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[]);
const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PRE=10000;
const WINDOWS=[['DEV_1',0,1999],['DEV_2',2000,3999],['DEV_3',4000,5999],['VAL_1',6000,7999],['VAL_2',8000,9999]];

function windowName(i){return WINDOWS.find(([,s,e])=>i>=s&&i<=e)?.[0]??'UNKNOWN';}
function stats(rows){const n=rows.length,w=rows.filter(x=>x.r>0),l=rows.filter(x=>x.r<=0),grossWin=w.reduce((s,x)=>s+x.r,0),grossLoss=-l.reduce((s,x)=>s+x.r,0),total=rows.reduce((s,x)=>s+x.r,0);let maxConsecLoss=0,cur=0;for(const x of [...rows].sort((a,b)=>a.entryIndex-b.entryIndex)){if(x.r<=0){cur++;maxConsecLoss=Math.max(maxConsecLoss,cur)}else cur=0}return{n,avgR:n?total/n:null,PF:grossLoss?grossWin/grossLoss:null,WR:n?w.length/n:null,totalR:total,maxConsecLoss};}
function classify(entryIndex){return windowName(entryIndex);}

// Counterfactual: keep every canonical baseline entry and its original risk/reward geometry,
// but reverse direction. BUY becomes SELL and SELL becomes BUY. The mirrored stop and TP
// distances are derived from the original entry/SL/TP prices. Outcome is re-simulated from
// the entry candle forward using the same OHLC path information available to the research data.
// If mirrored SL and TP are both touched inside one candle, the result is AMBIGUOUS and excluded.
function flipTrade(t){
 const entry=Number(t.entry),sl=Number(t.stopLoss),tp=Number(t.tp1),entryIndex=Number(t.entryIndex);
 if(!Number.isFinite(entry)||!Number.isFinite(sl)||!Number.isFinite(tp)||!Number.isInteger(entryIndex)||entryIndex<0)return null;
 const risk=Math.abs(entry-sl),reward=Math.abs(tp-entry);
 if(!(risk>0&&reward>0))return null;
 const direction=t.direction==='BUY'?'SELL':'BUY';
 const flipSL=direction==='BUY'?entry-risk:entry+risk;
 const flipTP=direction==='BUY'?entry+reward:entry-reward;
 for(let i=entryIndex+1;i<candles.length;i++){
  const c=candles[i]; const high=Number(c.high),low=Number(c.low); if(!Number.isFinite(high)||!Number.isFinite(low))continue;
  const hitSL=direction==='BUY'?low<=flipSL:high>=flipSL;
  const hitTP=direction==='BUY'?high>=flipTP:low<=flipTP;
  if(hitSL&&hitTP)return{r:null,result:'AMBIGUOUS',exitIndex:i,direction,entry,stopLoss:flipSL,tp1:flipTP};
  if(hitSL)return{r:-1,result:'SL',exitIndex:i,direction,entry,stopLoss:flipSL,tp1:flipTP};
  if(hitTP)return{r:reward/risk,result:'TP1',exitIndex:i,direction,entry,stopLoss:flipSL,tp1:flipTP};
 }
 return{r:null,result:'OPEN_END',exitIndex:null,direction,entry,stopLoss:flipSL,tp1:flipTP};
}

const canonical=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
const all=canonical.map(t=>{const f=flipTrade(t);return f?{...f,entryIndex:Number(t.entryIndex),originalDirection:t.direction,originalR:Number(t.rMultiple),window:classify(Number(t.entryIndex)),session:t.session??'UNKNOWN'}:null}).filter(Boolean);
const resolved=all.filter(x=>Number.isFinite(x.r));
const ambiguous=all.filter(x=>x.result==='AMBIGUOUS');
const openEnd=all.filter(x=>x.result==='OPEN_END');
const byWindow=Object.fromEntries(WINDOWS.map(([w])=>[w,stats(resolved.filter(x=>x.window===w))]));
const byOriginalDirection={BUY:stats(resolved.filter(x=>x.originalDirection==='BUY')),SELL:stats(resolved.filter(x=>x.originalDirection==='SELL'))};
const byFlippedDirection={BUY:stats(resolved.filter(x=>x.direction==='BUY')),SELL:stats(resolved.filter(x=>x.direction==='SELL'))};
const result={strategy:'Strategy A / SP2L',mode:'PHASE_COUNTERFACTUAL_DIRECTION_FLIP_AUDIT',timeframe:'5min',scope:{canonicalBaseline:canonical.length,simulated:all.length,resolved:resolved.length,ambiguous:ambiguous.length,openEnd:openEnd.length,dev:resolved.filter(x=>x.window.startsWith('DEV')).length,val:resolved.filter(x=>x.window.startsWith('VAL')).length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:221,actualCanonical:canonical.length,replayMismatch:canonical.length===221?0:null,canonicalSource:'direct baseline trades; no detector replay'},overall:stats(resolved),byWindow,byOriginalDirection,byFlippedDirection,methodology:{purpose:'Counterfactual audit of reversing every canonical BUY/SELL direction while preserving each trade entry and mirroring its original SL/TP distances.',entry:'Original canonical baseline entry price and entryIndex are unchanged.',direction:'BUY becomes SELL; SELL becomes BUY.',riskReward:'Original absolute stop distance and target distance are mirrored around the same entry.',path:'Future 5min OHLC candles after entry are scanned until mirrored SL or TP is touched.',ambiguity:'If mirrored SL and TP are both touched in the same candle, outcome is AMBIGUOUS and excluded from performance statistics.',openEnd:'If neither level is touched before the dataset ends, outcome is OPEN_END and excluded.',warning:'This is a counterfactual diagnostic, not a production strategy or a claim that simply inverting the signal is valid.'}};
const outDir=resolve(ROOT,'data/reports/strategy-a-phase-counterfactual-direction-flip-audit');await mkdir(outDir,{recursive:true});const out=resolve(outDir,'5min.json');await writeFile(out,JSON.stringify(result,null,2));
console.log(`PHASE_COUNTERFACTUAL_DIRECTION_FLIP_AUDIT 5min CANONICAL=${canonical.length} SIM=${all.length} RESOLVED=${resolved.length} AMBIGUOUS=${ambiguous.length} OPEN_END=${openEnd.length}`);
console.log(`OVERALL N=${resolved.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR*100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)} maxConsecLoss=${result.overall.maxConsecLoss}`);
for(const [w,s] of Object.entries(byWindow))console.log(`${w} N=${s.n} avgR=${s.avgR?.toFixed(6)} PF=${s.PF?.toFixed(6)} WR=${(s.WR*100)?.toFixed(2)}% totalR=${s.totalR?.toFixed(6)}`);
console.log(`FLIPPED BUY N=${byFlippedDirection.BUY.n} avgR=${byFlippedDirection.BUY.avgR?.toFixed(6)} PF=${byFlippedDirection.BUY.PF?.toFixed(6)} WR=${(byFlippedDirection.BUY.WR*100)?.toFixed(2)}%`);
console.log(`FLIPPED SELL N=${byFlippedDirection.SELL.n} avgR=${byFlippedDirection.SELL.avgR?.toFixed(6)} PF=${byFlippedDirection.SELL.PF?.toFixed(6)} WR=${(byFlippedDirection.SELL.WR*100)?.toFixed(2)}%`);
console.log(`REPORT=${out}`);
console.log('STATUS=COUNTERFACTUAL_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_PRODUCTION_CHANGE');
