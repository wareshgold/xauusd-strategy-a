import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT=resolve(fileURLToPath(new URL('..',import.meta.url)));
const candles=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[];
const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PRE=10000;
const WINDOWS=[['DEV_1',0,1999],['DEV_2',2000,3999],['DEV_3',4000,5999],['VAL_1',6000,7999],['VAL_2',8000,9999]];
const CFG={breakoutLookback:5,followThrough:{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true},spike:{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}};
const EMA_PERIODS=[50,100];

function maxConsecutiveLosses(rows){let max=0,cur=0;for(const x of [...rows].sort((a,b)=>a.entryIndex-b.entryIndex)){if(x.r<=0){cur++;max=Math.max(max,cur);}else cur=0;}return max;}
function stats(rows){const n=rows.length,w=rows.filter(x=>x.r>0),l=rows.filter(x=>x.r<=0),grossWin=w.reduce((s,x)=>s+x.r,0),grossLoss=-l.reduce((s,x)=>s+x.r,0),total=rows.reduce((s,x)=>s+x.r,0);return{n,avgR:n?total/n:null,PF:grossLoss?grossWin/grossLoss:null,WR:n?w.length/n:null,totalR:total,maxConsecLoss:maxConsecutiveLosses(rows)};}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=960&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION';}
function windowName(i){return WINDOWS.find(([,s,e])=>i>=s&&i<=e)?.[0]??'UNKNOWN';}
function replay(i){const v=candles.slice(0,i+1);if(v.length<60)return null;const bo=detectBreakout(v,CFG.breakoutLookback),ft=detectFollowThrough(v,bo,CFG.followThrough),sp=detectSpikeCandidates(v,bo,ft,CFG.spike);for(const s of sp.candidates){if(s.endIndex>=i)continue;const co=detectFirstCorrection(v,s);if(!co||co.correctionExtremeIndex>=i)continue;const tr=detectEntryTrigger(v,co);if(!tr||tr.index!==i)continue;const b=bo.find(x=>x.index===s.breakoutIndex&&x.direction===s.direction),f=ft.find(x=>x.breakoutIndex===s.breakoutIndex&&x.direction===s.direction);if(b&&f)return{tr,b,f,s,co};}return null;}

// EMA is computed causally over the full historical series. At entry i, only candles <= i are used.
function closesAt(i){const c=candles[i];return Number(c.close);}
function emaSeries(period){const out=Array(candles.length).fill(null),alpha=2/(period+1);let ema=null;for(let i=0;i<candles.length;i++){const close=closesAt(i);if(!Number.isFinite(close))continue;if(ema===null)ema=close;else ema=alpha*close+(1-alpha)*ema;out[i]=ema;}return out;}
const ema50=emaSeries(50),ema100=emaSeries(100);

const raw=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
let mismatch=0;const rows=[];
for(const t of raw){const entryIndex=Number(t.entryIndex),r=replay(entryIndex);if(!r||r.tr.timestamp!==t.entryTime||r.tr.direction!==t.direction){mismatch++;continue;}
  const close=closesAt(entryIndex),e50=ema50[entryIndex],e100=ema100[entryIndex],p50=ema50[entryIndex-1],p100=ema100[entryIndex-1];
  if(![close,e50,e100,p50,p100].every(Number.isFinite))continue;
  rows.push({r:Number(t.rMultiple),entryIndex,direction:t.direction,session:session(t.entryTime),window:windowName(entryIndex),close,ema50:e50,ema100:e100,ema50Delta:close-e50,ema100Delta:close-e100,ema50Slope:e50-p50,ema100Slope:e100-p100});
}

function audit(rows,filter){const a=rows.filter(filter);const perWindow=WINDOWS.map(([w])=>{const q=a.filter(x=>x.window===w);return{window:w,...stats(q)}});const observed=perWindow.filter(x=>x.n>0),positive=observed.filter(x=>x.avgR>0).length,negative=observed.filter(x=>x.avgR<0).length;return{overall:stats(a),perWindow,observedWindows:observed.length,positiveWindows:positive,negativeWindows:negative,signConsistency:observed.length?Math.max(positive,negative)/observed.length:null};}
function sensitivity(rows,filter){const a=rows.filter(filter).sort((x,y)=>y.r-x.r);const totals=[1,2,3].map(k=>{const keep=a.slice(k);return{removeTop:k,...stats(keep)}});return totals;}
function alignmentAudit(period){const bull=rows.filter(x=>x[`ema${period}Delta`]>0),bear=rows.filter(x=>x[`ema${period}Delta`]<0);const alignedBuy=bull.filter(x=>x.direction==='BUY'),misBuy=bear.filter(x=>x.direction==='BUY'),alignedSell=bear.filter(x=>x.direction==='SELL'),misSell=bull.filter(x=>x.direction==='SELL');return{
  bull:{all:stats(bull),BUY:stats(alignedBuy),SELL:stats(misSell)},
  bear:{all:stats(bear),BUY:stats(misBuy),SELL:stats(alignedSell)},
  aligned:{BUY:stats(alignedBuy),SELL:stats(alignedSell)},
  misaligned:{BUY:stats(misBuy),SELL:stats(misSell)},
  alignedBuy:sensitivity(rows,x=>x.direction==='BUY'&&x[`ema${period}Delta`]>0),
  alignedSell:sensitivity(rows,x=>x.direction==='SELL'&&x[`ema${period}Delta`]<0),
  windows:{
    alignedBuy:audit(rows,x=>x.direction==='BUY'&&x[`ema${period}Delta`]>0),
    misalignedBuy:audit(rows,x=>x.direction==='BUY'&&x[`ema${period}Delta`]<0),
    alignedSell:audit(rows,x=>x.direction==='SELL'&&x[`ema${period}Delta`]<0),
    misalignedSell:audit(rows,x=>x.direction==='SELL'&&x[`ema${period}Delta`]>0)
  }
};}
function slopeAudit(period){const bull=rows.filter(x=>x[`ema${period}Slope`]>0),bear=rows.filter(x=>x[`ema${period}Slope`]<0);return{bull:stats(bull),bear:stats(bear),windows:{bull:audit(rows,x=>x[`ema${period}Slope`]>0),bear:audit(rows,x=>x[`ema${period}Slope`]<0)}};}

const result={strategy:'Strategy A / SP2L',mode:'PHASE_30_DIRECTIONAL_CONTEXT_ALIGNMENT_AUDIT',timeframe:'5min',scope:{rawBaselinePre:raw.length,canonicalReplayed:rows.length,dev:rows.filter(x=>x.window.startsWith('DEV')).length,val:rows.filter(x=>x.window.startsWith('VAL')).length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:210,rawBaselinePre:raw.length,canonicalReplayed:rows.length,replayMismatch:mismatch},overall:stats(rows),ema:{EMA50:alignmentAudit(50),EMA100:alignmentAudit(100),slope:{EMA50:slopeAudit(50),EMA100:slopeAudit(100)}},temporalWindows:Object.fromEntries(WINDOWS.map(([w])=>[w,stats(rows.filter(x=>x.window===w))])),methodology:{purpose:'Descriptive audit of whether existing canonical BUY/SELL outcomes align with entry-time directional context. EMA50 and EMA100 are research diagnostics only and are not treated as Poorsamadi-canonical rules.',regimes:['close>EMA50','close<EMA50','close>EMA100','close<EMA100','EMA50 slope>0','EMA50 slope<0','EMA100 slope>0','EMA100 slope<0'],alignment:'BUY aligned when close is above EMA; SELL aligned when close is below EMA. Opposite side is misaligned.',emaCalculation:'Causal recursive EMA using candles through the entry candle only; no future candles.',fixedChronologicalWindows:WINDOWS,metrics:['N','avgR','PF','WR','totalR','maxConsecLoss','positiveWindows','negativeWindows','signConsistency'],topWinnerSensitivity:true,noThresholdSearch:true,noOptimization:true,noNewTradingRule:true,noFreshHoldoutAccess:true,productionUntouched:true}};

const out=resolve(ROOT,'data/reports/strategy-a-phase30-directional-context-alignment-audit');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE_30_DIRECTIONAL_CONTEXT_ALIGNMENT_AUDIT 5min N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} replayMismatch=${mismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR*100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)} maxConsecLoss=${result.overall.maxConsecLoss}`);
for(const p of EMA_PERIODS){const a=result.ema[`EMA${p}`];console.log(`EMA${p} ALIGNED BUY N=${a.aligned.BUY.n} avgR=${a.aligned.BUY.avgR?.toFixed(4)} PF=${a.aligned.BUY.PF?.toFixed(4)} WR=${(a.aligned.BUY.WR*100)?.toFixed(2)}% totalR=${a.aligned.BUY.totalR?.toFixed(4)} | SELL N=${a.aligned.SELL.n} avgR=${a.aligned.SELL.avgR?.toFixed(4)} PF=${a.aligned.SELL.PF?.toFixed(4)} WR=${(a.aligned.SELL.WR*100)?.toFixed(2)}% totalR=${a.aligned.SELL.totalR?.toFixed(4)}`);console.log(`EMA${p} MISALIGNED BUY N=${a.misaligned.BUY.n} avgR=${a.misaligned.BUY.avgR?.toFixed(4)} PF=${a.misaligned.BUY.PF?.toFixed(4)} | SELL N=${a.misaligned.SELL.n} avgR=${a.misaligned.SELL.avgR?.toFixed(4)} PF=${a.misaligned.SELL.PF?.toFixed(4)}`);for(const key of ['alignedBuy','misalignedBuy','alignedSell','misalignedSell']){const v=a.windows[key];console.log(`EMA${p} ${key}: `+v.perWindow.map(x=>`${x.window}[N=${x.n},avgR=${x.avgR?.toFixed(3)},PF=${x.PF?.toFixed(3)}]`).join(' '));}}
for(const p of EMA_PERIODS){for(const dir of ['BUY','SELL']){const s=result.ema[`EMA${p}`][dir==='BUY'?'alignedBuy':'alignedSell'];console.log(`SENS EMA${p} ${dir}: -TOP1 avgR=${s[0].avgR?.toFixed(4)} PF=${s[0].PF?.toFixed(4)} | -TOP2 avgR=${s[1].avgR?.toFixed(4)} PF=${s[1].PF?.toFixed(4)} | -TOP3 avgR=${s[2].avgR?.toFixed(4)} PF=${s[2].PF?.toFixed(4)}`);}}
console.log(`REPORT=${resolve(out,'5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
