import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const INPUT=resolve(ROOT,'data/reports/strategy-a-entry-path-forensics');
const BASELINE=resolve(ROOT,'data/reports/strategy-a-baseline');
const OUTPUT=resolve(ROOT,'data/reports/strategy-a-entry-trigger-outcome-forensics');
const FRESH_HOLDOUT_CANDLES=5000;
const PRE_HOLDOUT_CANDLES=10000;

function median(values){if(!values.length)return null;const a=[...values].sort((x,y)=>x-y),m=Math.floor(a.length/2);return a.length%2?a[m]:(a[m-1]+a[m])/2}
function pf(rows){const wins=rows.filter(r=>r.r>0).reduce((s,r)=>s+r.r,0),losses=Math.abs(rows.filter(r=>r.r<0).reduce((s,r)=>s+r.r,0));return losses?wins/losses:null}
function metrics(rows){const closed=rows.filter(r=>r.r!==null),wins=closed.filter(r=>r.r>0),losses=closed.filter(r=>r.r<0);const totalR=closed.reduce((s,r)=>s+r.r,0);let eq=0,peak=0,maxDD=0,streak=0,maxCL=0;for(const r of closed){eq+=r.r;peak=Math.max(peak,eq);maxDD=Math.max(maxDD,peak-eq);streak=r.r<0?streak+1:0;maxCL=Math.max(maxCL,streak)}return {n:closed.length,wins:wins.length,losses:losses.length,winRate:closed.length?wins.length/closed.length:0,avgR:closed.length?totalR/closed.length:0,totalR,PF:pf(closed),maxDD,maxCL,medianR:median(closed.map(r=>r.r))}}
function group(rows,keyFn){const out={};for(const row of rows){const key=keyFn(row);(out[key]??=[]).push(row)}return Object.fromEntries(Object.entries(out).map(([k,v])=>[k,{...metrics(v),medianDelay:median(v.map(r=>r.triggerDelay)),medianCorrectionDepth:median(v.map(r=>r.correctionDepth)),medianTriggerExtension:median(v.map(r=>r.triggerExtension)),medianStopToImpulse:median(v.map(r=>r.stopToImpulse))}]))}
function bins(rows,field,definitions){return Object.fromEntries(definitions.map(b=>{const selected=rows.filter(r=>b.test(r[field]));return [b.name,{...metrics(selected),nRaw:selected.length,medianFeature:median(selected.map(r=>r[field]))}] }))}

async function run(timeframe){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles;
 const pathReport=JSON.parse(await readFile(resolve(INPUT,`${timeframe}.json`),'utf8'));
 const baselineReport=JSON.parse(await readFile(resolve(BASELINE,`${timeframe}.json`),'utf8'));
 const cutoffIndex=Math.min(PRE_HOLDOUT_CANDLES,candles.length-FRESH_HOLDOUT_CANDLES);
 const cutoffTime=candles[cutoffIndex]?.timestamp;
 if(!cutoffTime)throw new Error(`${timeframe}: missing deterministic pre-holdout cutoff timestamp`);

 // Use the canonical baseline backtest's resolved trade outcomes as the sole outcome source.
 // The direct path forensic can contain candidate rows that never receive a resolved outcome
 // (e.g. AMBIGUOUS/OPEN in the canonical backtest). Those rows are diagnostic candidates,
 // not parity failures, so parity is measured against the resolved baseline universe.
 const baselineTrades=(baselineReport.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<new Date(cutoffTime));
 const selected=pathReport.baselineSelected??[];
 const selectedPreHoldout=selected.filter(c=>c.index<cutoffIndex);
 const key=c=>`${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
 const byKey=new Map();
 for(const t of baselineTrades)byKey.set(`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`,t);
 const rows=[];
 const unmatched=[];
 for(const c of selectedPreHoldout){
  const t=byKey.get(key(c));
  if(!t){unmatched.push(c);continue}
  rows.push({...c,r:Number(t.rMultiple),result:t.result});
 }
 const matchedBaselineKeys=new Set(rows.map(key));
 const missingBaseline=baselineTrades.filter(t=>!matchedBaselineKeys.has(`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`));
 const reportOut={strategy:'Strategy A',mode:'BASELINE_ENTRY_TRIGGER_OUTCOME_FORENSICS',timeframe,candles:candles.length,scope:{preHoldoutCandles:cutoffIndex,freshHoldoutCandles:FRESH_HOLDOUT_CANDLES,excludedFreshHoldout:true},parity:{baselineTradesPreHoldout:baselineTrades.length,forensicSelectedPreHoldout:selectedPreHoldout.length,resolvedBaselineMatched:rows.length,forensicUnmatchedOutcomeCandidates:unmatched.length,baselineMissingFromForensics:missingBaseline.length,matchRateAgainstResolvedBaseline:baselineTrades.length?rows.length/baselineTrades.length:0,fullResolvedBaselineCoverage:missingBaseline.length===0,outcomeSource:'data/reports/strategy-a-baseline; no outcome recomputation',joinKey:'entryIndex + direction + entry + stopLoss + tp1',note:'Forensic-selected rows without a canonical resolved baseline outcome are excluded from outcome attribution and are not counted as parity failures.'},overall:metrics(rows),byDirection:group(rows,r=>r.direction),bySession:group(rows,r=>r.session),byDirectionSession:group(rows,r=>`${r.direction}_${r.session}`),features:{triggerDelay:bins(rows,'triggerDelay',[{name:'0',test:v=>v===0},{name:'1',test:v=>v===1},{name:'2',test:v=>v===2},{name:'3+',test:v=>v>=3}]),correctionDepth:bins(rows,'correctionDepth',[{name:'<25%',test:v=>v<.25},{name:'25-50%',test:v=>v>=.25&&v<.5},{name:'50-75%',test:v=>v>=.5&&v<.75},{name:'75%+',test:v=>v>=.75}]),triggerExtension:bins(rows,'triggerExtension',[{name:'<5%',test:v=>v<.05},{name:'5-10%',test:v=>v>=.05&&v<.10},{name:'10-20%',test:v=>v>=.10&&v<.20},{name:'20%+',test:v=>v>=.20}]),stopToImpulse:bins(rows,'stopToImpulse',[{name:'<25%',test:v=>v<.25},{name:'25-50%',test:v=>v>=.25&&v<.5},{name:'50-100%',test:v=>v>=.5&&v<1},{name:'100%+',test:v=>v>=1}]),rewardRisk:bins(rows,'rr',[{name:'<1.5',test:v=>v<1.5},{name:'1.5-3',test:v=>v>=1.5&&v<3},{name:'3-5',test:v=>v>=3&&v<5},{name:'5+',test:v=>v>=5}])}};
 await mkdir(OUTPUT,{recursive:true});const out=resolve(OUTPUT,`${timeframe}.json`);await writeFile(out,JSON.stringify(reportOut,null,2));
 console.log(`${timeframe}: baselinePreHoldout=${baselineTrades.length} forensicSelected=${selectedPreHoldout.length} resolvedMatched=${rows.length} forensicUnmatched=${unmatched.length} baselineMissing=${missingBaseline.length}`);
 console.log(`  parity: resolvedBaselineCoverage=${(reportOut.parity.matchRateAgainstResolvedBaseline*100).toFixed(2)}% fullResolvedBaselineCoverage=${reportOut.parity.fullResolvedBaselineCoverage}`);
 console.log(`  outcome parity: avgR=${reportOut.overall.avgR.toFixed(4)} PF=${reportOut.overall.PF?.toFixed(4)??'n/a'} maxDD=${reportOut.overall.maxDD.toFixed(4)}R`);
 for(const [k,v] of Object.entries(reportOut.features))console.log(`  ${k}:`,Object.entries(v).map(([b,m])=>`${b} n=${m.n} avgR=${m.avgR.toFixed(4)} PF=${m.PF?.toFixed(3)??'n/a'}`).join(' | '));
 console.log(`Report -> ${out}`);
}
await run('1min');await run('5min');
