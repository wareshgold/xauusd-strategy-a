import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-entry-geometry-forensics');
const TIMEFRAMES=['1min','5min'];
const LOOKBACK=60;
const IMPULSE_LOOKBACK=20;

function median(a){const x=a.filter(Number.isFinite).sort((p,q)=>p-q);if(!x.length)return null;const m=Math.floor(x.length/2);return x.length%2?x[m]:(x[m-1]+x[m])/2;}
function q(a,p){const x=a.filter(Number.isFinite).sort((m,n)=>m-n);if(!x.length)return null;const z=(x.length-1)*p,l=Math.floor(z),h=Math.ceil(z);return l===h?x[l]:x[l]+(x[h]-x[l])*(z-l);}
function tr(c){return Math.max(c.high-c.low,Math.abs(c.high-c.open),Math.abs(c.low-c.open));}
function sign(d){return d==='BUY'?1:-1;}
function summarize(rows){const a=rows.filter(r=>Number.isFinite(r.rMultiple)),gp=a.filter(r=>r.rMultiple>0).reduce((s,r)=>s+r.rMultiple,0),gl=a.filter(r=>r.rMultiple<0).reduce((s,r)=>s-r.rMultiple,0);return{n:a.length,wins:a.filter(r=>r.rMultiple>0).length,losses:a.filter(r=>r.rMultiple<0).length,PF:gl?gp/gl:null,avgR:a.length?a.reduce((s,r)=>s+r.rMultiple,0)/a.length:0,totalR:a.reduce((s,r)=>s+r.rMultiple,0)};}
function dd(rows){let e=0,p=0,m=0;for(const r of rows.filter(x=>Number.isFinite(x.rMultiple))){e+=r.rMultiple;p=Math.max(p,e);m=Math.max(m,p-e);}return m;}
function bucket(x,cuts,labels){if(!Number.isFinite(x))return null;for(let i=0;i<cuts.length;i++)if(x<cuts[i])return labels[i];return labels.at(-1);}
function byBucket(rows,key,cuts,labels){return labels.map(label=>{const a=rows.filter(r=>bucket(r[key],cuts,labels)===label);return{bucket:label,...summarize(a),maxDD:dd(a)};});}
function half(rows){const m=Math.floor(rows.length/2);return{dev:rows.slice(0,m),oos:rows.slice(m)};}
function stability(rows,key,cuts,labels){const h=half(rows);return labels.map(label=>{const a=h.dev.filter(r=>bucket(r[key],cuts,labels)===label),b=h.oos.filter(r=>bucket(r[key],cuts,labels)===label);return{bucket:label,dev:{...summarize(a),maxDD:dd(a)},oos:{...summarize(b),maxDD:dd(b)},stable:Boolean(b.length>=10&&b.PF!=null&&b.PF>=1&&b.avgR>0)};});}

function feature(candles,t){
 const ei=t.entryIndex;if(!Number.isInteger(ei)||ei<LOOKBACK||!candles[ei])return null;
 const s=sign(t.direction),start=Math.max(LOOKBACK,ei-IMPULSE_LOOKBACK);
 const prior=candles.slice(start,ei),entryC=candles[ei];
 const medianTR=median(candles.slice(ei-LOOKBACK,ei).map(tr)); if(!medianTR||medianTR<=0)return null;
 let impulseIndex=null,best=-Infinity;
 for(let i=start;i<ei;i++){const c=candles[i],score=tr(c)/medianTR,dir=s>0?c.close-c.open:c.open-c.close;if(dir>0&&score>best){best=score;impulseIndex=i;}}
 if(impulseIndex==null)return null;
 const imp=candles[impulseIndex],impRange=tr(imp),impHigh=imp.high,impLow=imp.low;
 const between=candles.slice(impulseIndex+1,ei);
 const retraceExtreme=between.length?(s>0?Math.min(...between.map(c=>c.low)):Math.max(...between.map(c=>c.high))):(s>0?entryC.low:entryC.high);
 const retracement=s>0?(impHigh-retraceExtreme)/impRange:(retraceExtreme-impLow)/impRange;
 const entryLocation=s>0?(t.entry-impLow)/impRange:(impHigh-t.entry)/impRange;
 const distanceFromExtreme=s>0?(impHigh-t.entry)/impRange:(t.entry-impLow)/impRange;
 const bodyFraction=impRange>0?Math.abs(imp.close-imp.open)/impRange:null;
 const delay=ei-impulseIndex;
 const recentTR=between.slice(-5).map(tr),olderTR=between.slice(-15,-5).map(tr);
 const compression=recentTR.length&&olderTR.length?median(recentTR)/median(olderTR):null;
 const stopToImpulse=t.riskDistance/impRange;
 return{...t,impulseIndex,impulseScore:best,impulseRange,impulseBodyFraction:bodyFraction,retracement,entryLocation,distanceFromExtreme,delayFromImpulse:delay,compressionRatio:compression,stopToImpulse,preEntryBars:between.length};
}

async function run(timeframe){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles;
 const baseline=JSON.parse(await readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${timeframe}.json`),'utf8'));
 const rows=baseline.trades.filter(t=>Number.isFinite(t.rMultiple)).map(t=>feature(candles,t)).filter(Boolean).sort((a,b)=>new Date(a.entryTime)-new Date(b.entryTime));
 const defs=[
  ['impulseScore',[1,1.25,1.5,2,2.5,Infinity],['LT_1.00','1.00_1.25','1.25_1.50','1.50_2.00','2.00_2.50','GE_2.50']],
  ['retracement',[0.25,0.5,0.75,1,Infinity],['LT_25%','25_50%','50_75%','75_100%','GE_100%']],
  ['entryLocation',[0.25,0.5,0.75,Infinity],['0_25%','25_50%','50_75%','75_100%']],
  ['distanceFromExtreme',[0.25,0.5,0.75,Infinity],['0_25%','25_50%','50_75%','75_100%']],
  ['delayFromImpulse',[3,6,9,13,Infinity],['D0_2','D3_5','D6_8','D9_12','D13_PLUS']],
  ['impulseBodyFraction',[0.4,0.6,0.8,Infinity],['LT_40%','40_60%','60_80%','GE_80%']],
  ['compressionRatio',[0.75,1,1.25,Infinity],['LT_75%','75_100%','100_125%','GE_125%']],
  ['stopToImpulse',[0.25,0.5,0.75,1,Infinity],['LT_25%','25_50%','50_75%','75_100%','GE_100%']],
 ];
 const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_ENTRY_GEOMETRY_FORENSICS',timeframe,scope:'All baseline trades; pre-entry price geometry only; chronological second-half OOS; no threshold optimization',methodology:{impulse:'strongest directionally aligned candle in the previous 20 bars, normalized by preceding 60-bar median true range',retracement:'maximum adverse excursion after impulse and before entry, divided by impulse true range',entryLocation:'entry position measured from impulse origin toward impulse extreme',distanceFromExtreme:'remaining distance from entry to impulse extreme divided by impulse range',delay:'bars between selected impulse and entry',compression:'median TR of last up to 5 pre-entry bars divided by median TR of preceding up to 10 pre-entry bars',stopToImpulse:'trade risk distance divided by selected impulse true range',lookahead:'all features use candles strictly before entry',promotionGate:'OOS bucket requires n >= 10, PF >= 1, avgR > 0; diagnostic only'}},coverage:{baselineTrades:baseline.trades.length,classifiedTrades:rows.length},overall:{...summarize(rows),maxDD:dd(rows)},features:{},tradeRows:rows,nextResearchQuestion:'Only investigate geometry features whose OOS bucket is positive with adequate sample; then test compact combinations on untouched chronological thirds.'};
 for(const [key,cuts,labels] of defs)report.features[key]={all:byBucket(rows,key,cuts,labels),stability:stability(rows,key,cuts,labels)};
 await mkdir(OUT_DIR,{recursive:true});const out=resolve(OUT_DIR,`${timeframe}.json`);await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${timeframe}: baseline=${baseline.trades.length} classified=${rows.length} PF=${report.overall.PF?.toFixed(4)??'n/a'}`);
 for(const [key] of defs){console.log(`  ${key}:`);for(const x of report.features[key].stability)console.log(`    ${x.bucket}: DEV n=${x.dev.n} PF=${x.dev.PF?.toFixed(4)??'n/a'} | OOS n=${x.oos.n} PF=${x.oos.PF?.toFixed(4)??'n/a'} avgR=${x.oos.avgR.toFixed(4)} stable=${x.stable}`);}
 console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES)await run(tf);
