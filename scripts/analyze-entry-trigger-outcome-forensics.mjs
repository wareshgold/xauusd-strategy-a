import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const INPUT=resolve(ROOT,'data/reports/strategy-a-entry-path-forensics');
const OUTPUT=resolve(ROOT,'data/reports/strategy-a-entry-trigger-outcome-forensics');
const FRESH_HOLDOUT_CANDLES=5000;
const PRE_HOLDOUT_CANDLES=10000;

function median(values){if(!values.length)return null;const a=[...values].sort((x,y)=>x-y),m=Math.floor(a.length/2);return a.length%2?a[m]:(a[m-1]+a[m])/2}
function pf(rows){const wins=rows.filter(r=>r.r>0).reduce((s,r)=>s+r.r,0),losses=Math.abs(rows.filter(r=>r.r<0).reduce((s,r)=>s+r.r,0));return losses?wins/losses:null}
function metrics(rows){const closed=rows.filter(r=>r.r!==null),wins=closed.filter(r=>r.r>0),losses=closed.filter(r=>r.r<0);const totalR=closed.reduce((s,r)=>s+r.r,0);let eq=0,peak=0,maxDD=0,streak=0,maxCL=0;for(const r of closed){eq+=r.r;peak=Math.max(peak,eq);maxDD=Math.max(maxDD,peak-eq);streak=r.r<0?streak+1:0;maxCL=Math.max(maxCL,streak)}return {n:closed.length,wins:wins.length,losses:losses.length,winRate:closed.length?wins.length/closed.length:0,avgR:closed.length?totalR/closed.length:0,totalR,PF:pf(closed),maxDD,maxCL,medianR:median(closed.map(r=>r.r))}}
function evaluate(candles,candidate){const risk=Math.abs(candidate.entry-candidate.stopLoss);for(let i=candidate.index+1;i<candles.length;i++){const c=candles[i],sl=candidate.direction==='BUY'?c.low<=candidate.stopLoss:c.high>=candidate.stopLoss,tp=candidate.direction==='BUY'?c.high>=candidate.tp1:c.low<=candidate.tp1;if(sl&&tp)return {...candidate,r:-1,result:'AMBIGUOUS'};if(sl)return {...candidate,r:-1,result:'SL'};if(tp)return {...candidate,r:Math.abs(candidate.tp1-candidate.entry)/risk,result:'TP1'};}return {...candidate,r:null,result:'OPEN'} }
function group(rows,keyFn){const out={};for(const row of rows){const key=keyFn(row);(out[key]??=[]).push(row)}return Object.fromEntries(Object.entries(out).map(([k,v])=>[k,{...metrics(v),medianDelay:median(v.map(r=>r.triggerDelay)),medianCorrectionDepth:median(v.map(r=>r.correctionDepth)),medianTriggerExtension:median(v.map(r=>r.triggerExtension)),medianStopToImpulse:median(v.map(r=>r.stopToImpulse))}]))}
function bins(rows,field,bins){return Object.fromEntries(bins.map(b=>{const selected=rows.filter(r=>b.test(r[field]));return [b.name,{...metrics(selected),nRaw:selected.length,medianFeature:median(selected.map(r=>r[field]))}] }))}

async function run(timeframe){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles;
 const report=JSON.parse(await readFile(resolve(INPUT,`${timeframe}.json`),'utf8'));
 const pre=report.baselineSelected.filter(c=>c.index<PRE_HOLDOUT_CANDLES && c.index<candles.length-FRESH_HOLDOUT_CANDLES);
 const rows=pre.map(c=>evaluate(candles,c));
 const triggerDelayBins=[{name:'0',test:v=>v===0},{name:'1',test:v=>v===1},{name:'2',test:v=>v===2},{name:'3+',test:v=>v>=3}];
 const correctionDepthBins=[{name:'<25%',test:v=>v<.25},{name:'25-50%',test:v=>v>=.25&&v<.5},{name:'50-75%',test:v=>v>=.5&&v<.75},{name:'75%+',test:v=>v>=.75}];
 const triggerExtensionBins=[{name:'<5%',test:v=>v<.05},{name:'5-10%',test:v=>v>=.05&&v<.10},{name:'10-20%',test:v=>v>=.10&&v<.20},{name:'20%+',test:v=>v>=.20}];
 const stopToImpulseBins=[{name:'<25%',test:v=>v<.25},{name:'25-50%',test:v=>v>=.25&&v<.5},{name:'50-100%',test:v=>v>=.5&&v<1},{name:'100%+',test:v=>v>=1}];
 const reportOut={strategy:'Strategy A',mode:'BASELINE_ENTRY_TRIGGER_OUTCOME_FORENSICS',timeframe,candles:candles.length,scope:{preHoldoutCandles:PRE_HOLDOUT_CANDLES,freshHoldoutCandles:FRESH_HOLDOUT_CANDLES,excludedFreshHoldout:true},methodology:'Research-only attribution of already-selected baseline candidates to their realized backtest outcome. No future candle is used for feature construction; outcome evaluation uses the same first-touch SL/TP semantics as the baseline engine. Fixed bins are diagnostic and are not production filters.',overall:metrics(rows),byDirection:group(rows,r=>r.direction),bySession:group(rows,r=>r.session),byDirectionSession:group(rows,r=>`${r.direction}_${r.session}`),features:{triggerDelay:bins(rows,'triggerDelay',triggerDelayBins),correctionDepth:bins(rows,'correctionDepth',correctionDepthBins),triggerExtension:bins(rows,'triggerExtension',triggerExtensionBins),stopToImpulse:bins(rows,'stopToImpulse',stopToImpulseBins),rewardRisk:bins(rows,'rr',[{name:'<1.5',test:v=>v<1.5},{name:'1.5-3',test:v=>v>=1.5&&v<3},{name:'3-5',test:v=>v>=3&&v<5},{name:'5+',test:v=>v>=5}])}};
 await mkdir(OUTPUT,{recursive:true});const out=resolve(OUTPUT,`${timeframe}.json`);await writeFile(out,JSON.stringify(reportOut,null,2));
 console.log(`${timeframe}: preHoldout=${rows.length} wins=${reportOut.overall.wins} losses=${reportOut.overall.losses} avgR=${reportOut.overall.avgR.toFixed(4)} PF=${reportOut.overall.PF?.toFixed(4)??'n/a'} maxDD=${reportOut.overall.maxDD.toFixed(4)}R`);
 for(const [k,v] of Object.entries(reportOut.features)){console.log(`  ${k}:`,Object.entries(v).map(([b,m])=>`${b} n=${m.n} avgR=${m.avgR.toFixed(4)} PF=${m.PF?.toFixed(3)??'n/a'}`).join(' | '))}
 console.log(`Report -> ${out}`);
}
await run('1min');await run('5min');
