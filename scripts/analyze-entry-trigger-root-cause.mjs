import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PATH_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-trigger-root-cause');
const PRE = 10000;
const MIN_N = 15;

function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a,b)=>a+b,0), gl = -losses.reduce((a,b)=>a+b,0);
  let eq=0, peak=0, dd=0, cl=0, maxCL=0;
  for (const r of rs) { eq += r; peak=Math.max(peak,eq); dd=Math.max(dd,peak-eq); cl=r<0?cl+1:0; maxCL=Math.max(maxCL,cl); }
  return {n:rs.length,wins:wins.length,losses:losses.length,winRate:rs.length?wins.length/rs.length:0,avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0,totalR:rs.reduce((a,b)=>a+b,0),PF:gl?gp/gl:null,maxDD:dd,maxCL};
}
function key(c){return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`}
function summarize(rows, name, predicate, baseline){const s=metrics(rows.filter(predicate));return {name,...s,deltaAvgR:s.avgR-baseline.avgR,pass:s.n>=MIN_N&&s.avgR>0&&s.PF!==null&&s.PF>=1};}
function split(rows, pred){return {all:rows.filter(pred),wins:rows.filter(r=>pred(r)&&r.r>0),losses:rows.filter(r=>pred(r)&&r.r<0)}}

async function run(tf){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')).candles;
 const path=JSON.parse(await readFile(resolve(PATH_DIR,`${tf}.json`),'utf8'));
 const base=JSON.parse(await readFile(resolve(BASE_DIR,`${tf}.json`),'utf8'));
 const cutoff=candles[PRE]?.timestamp;
 const trades=(base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<new Date(cutoff));
 const map=new Map(trades.map(t=>[`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`,t]));
 const rows=[];
 for(const c of (path.baselineSelected??[]).filter(c=>c.index<PRE)){const t=map.get(key(c));if(t)rows.push({...c,r:Number(t.rMultiple),result:t.result});}
 const baseline=metrics(rows);
 const descriptors=[
  summarize(rows,'triggerDelay=0',r=>r.triggerDelay===0,baseline),summarize(rows,'triggerDelay=1',r=>r.triggerDelay===1,baseline),summarize(rows,'triggerDelay>=2',r=>r.triggerDelay>=2,baseline),
  summarize(rows,'correctionDepth<25%',r=>r.correctionDepth<.25,baseline),summarize(rows,'correctionDepth>=25%',r=>r.correctionDepth>=.25,baseline),
  summarize(rows,'triggerExtension<10%',r=>r.triggerExtension<.10,baseline),summarize(rows,'triggerExtension>=10%',r=>r.triggerExtension>=.10,baseline),
  summarize(rows,'stopToImpulse<25%',r=>r.stopToImpulse<.25,baseline),summarize(rows,'stopToImpulse25-50%',r=>r.stopToImpulse>=.25&&r.stopToImpulse<.50,baseline),summarize(rows,'stopToImpulse>=50%',r=>r.stopToImpulse>=.50,baseline),
 ];
 const cells=[];
 const binary=[['delay<=1',r=>r.triggerDelay<=1],['delay>=2',r=>r.triggerDelay>=2],['depth<25',r=>r.correctionDepth<.25],['ext<10',r=>r.triggerExtension<.10],['stop25-50',r=>r.stopToImpulse>=.25&&r.stopToImpulse<.50]];
 for(const [a,pa] of binary)for(const [b,pb] of binary){if(a>=b)continue;const s=summarize(rows,`${a} AND ${b}`,r=>pa(r)&&pb(r),baseline);if(s.n>=MIN_N)cells.push(s)}
 const byOutcome={winners:metrics(rows.filter(r=>r.r>0)),losers:metrics(rows.filter(r=>r.r<0))};
 const outcomeFeature={};
 for(const field of ['triggerDelay','correctionDepth','triggerExtension','stopToImpulse','rr']){
  outcomeFeature[field]={winners:rows.filter(r=>r.r>0).map(r=>r[field]).filter(Number.isFinite),losers:rows.filter(r=>r.r<0).map(r=>r[field]).filter(Number.isFinite)};
 }
 const report={strategy:'Strategy A',mode:'ENTRY_TRIGGER_ROOT_CAUSE_PREHOLDOUT',timeframe,candles:candles.length,scope:{preHoldoutCandles:PRE,freshHoldoutExcluded:true},methodology:{outcomeSource:'canonical baseline',featureSource:'direct baseline-path forensic',purpose:'diagnostic attribution only; no threshold optimization or production change',minN:MIN_N},parity:{baselineResolved:trades.length,forensicMatched:rows.length,baselineMissing:trades.filter(t=>!rows.some(r=>key(r)===`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`)).length},baseline,descriptors,topPairCandidates:cells.sort((a,b)=>b.avgR-a.avgR).slice(0,12),outcome:{byOutcome,outcomeFeature}};
 await mkdir(OUT_DIR,{recursive:true});const out=resolve(OUT_DIR,`${tf}.json`);await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${tf}: n=${baseline.n} avgR=${baseline.avgR.toFixed(4)} PF=${baseline.PF?.toFixed(4)??'n/a'} matched=${rows.length}`);
 for(const d of descriptors)console.log(`  ${d.name}: n=${d.n} avgR=${d.avgR.toFixed(4)} PF=${d.PF?.toFixed(3)??'n/a'} delta=${d.deltaAvgR.toFixed(4)} pass=${d.pass}`);
 console.log(`  top pair: ${report.topPairCandidates.slice(0,5).map(x=>`${x.name} n=${x.n} avgR=${x.avgR.toFixed(3)} PF=${x.PF?.toFixed(2)??'n/a'}`).join(' | ')}`);
 console.log(`Report -> ${out}`);
}
await run('1min');await run('5min');
