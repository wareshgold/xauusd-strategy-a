import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PATH_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-trigger-microstructure-root-cause');
const PRE = 10000;
const MIN_N = 15;

function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a,b)=>a+b,0), gl = -losses.reduce((a,b)=>a+b,0);
  let eq=0, peak=0, dd=0, cl=0, maxCL=0;
  for (const r of rs) { eq += r; peak=Math.max(peak,eq); dd=Math.max(dd,peak-eq); cl=r<0?cl+1:0; maxCL=Math.max(maxCL,cl); }
  return { n:rs.length, wins:wins.length, losses:losses.length, winRate:rs.length?wins.length/rs.length:0, avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0, totalR:rs.reduce((a,b)=>a+b,0), PF:gl?gp/gl:null, maxDD:dd, maxCL };
}
function key(c){return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`}
function finite(x){return Number.isFinite(Number(x));}
function bucket(name, rows, pred, baseline){
  const s=metrics(rows.filter(pred));
  return {name,...s,deltaAvgR:s.avgR-baseline.avgR,pass:s.n>=MIN_N&&s.avgR>0&&s.PF!==null&&s.PF>=1};
}
function candleStats(c){
  const o=Number(c.open),h=Number(c.high),l=Number(c.low),cl=Number(c.close);
  const range=h-l;
  const body=Math.abs(cl-o);
  const upper=h-Math.max(o,cl);
  const lower=Math.min(o,cl)-l;
  return {range,body,bodyFraction:range?body/range:null,upperWickFraction:range?upper/range:null,lowerWickFraction:range?lower/range:null,closeLocation:range?(cl-l)/range:null,directionalBody:range?(cl-o)/range:null};
}
function describe(rows, candles){
  for(const r of rows){
    const i=Number(r.index); const c=candles[i]; if(!c) continue;
    const s=candleStats(c); const dir=r.direction;
    Object.assign(r,{triggerBodyFraction:s.bodyFraction,triggerCloseLocation:s.closeLocation,triggerDirectionalBody:dir==='BUY'?s.directionalBody:-s.directionalBody,triggerOppositeWickFraction:dir==='BUY'?s.lowerWickFraction:s.upperWickFraction,triggerWithDirection:(s.directionalBody>0&&dir==='BUY')||(s.directionalBody<0&&dir==='SELL'),triggerRange:s.range,triggerBody:s.body,triggerUpperWick:s.upperWickFraction,triggerLowerWick:s.lowerWickFraction});
  }
}
function thresholds(rows, field, values, baseline){return values.map(([name,p])=>bucket(`${field}:${name}`,rows,p,baseline));}

async function run(timeframe){
  const tf=timeframe;
  const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')).candles;
  const path=JSON.parse(await readFile(resolve(PATH_DIR,`${tf}.json`),'utf8'));
  const base=JSON.parse(await readFile(resolve(BASE_DIR,`${tf}.json`),'utf8'));
  const cutoff=candles[PRE]?.timestamp;
  const trades=(base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&finite(t.rMultiple)&&new Date(t.entryTime)<new Date(cutoff));
  const map=new Map(trades.map(t=>[key({index:t.entryIndex,direction:t.direction,entry:t.entry,stopLoss:t.stopLoss,tp1:t.tp1}),t]));
  const rows=[];
  for(const c of (path.baselineSelected??[]).filter(c=>c.index<PRE)){const t=map.get(key(c));if(t)rows.push({...c,r:Number(t.rMultiple),result:t.result});}
  describe(rows,candles);
  const baseline=metrics(rows);
  const bins=[
    ...thresholds(rows,'delay',[['<=1',r=>r.triggerDelay<=1],['>=2',r=>r.triggerDelay>=2]],baseline),
    ...thresholds(rows,'depth',[['<25%',r=>r.correctionDepth<.25],['>=25%',r=>r.correctionDepth>=.25]],baseline),
    ...thresholds(rows,'extension',[['<10%',r=>r.triggerExtension<.10],['>=10%',r=>r.triggerExtension>=.10]],baseline),
    ...thresholds(rows,'stopToImpulse',[['<25%',r=>r.stopToImpulse<.25],['25-50%',r=>r.stopToImpulse>=.25&&r.stopToImpulse<.50],['>=50%',r=>r.stopToImpulse>=.50]],baseline),
    ...thresholds(rows,'bodyFraction',[['<25%',r=>r.triggerBodyFraction<.25],['25-50%',r=>r.triggerBodyFraction>=.25&&r.triggerBodyFraction<.50],['50-75%',r=>r.triggerBodyFraction>=.50&&r.triggerBodyFraction<.75],['>=75%',r=>r.triggerBodyFraction>=.75]],baseline),
    ...thresholds(rows,'closeLocation',[['<25%',r=>r.triggerCloseLocation<.25],['25-50%',r=>r.triggerCloseLocation>=.25&&r.triggerCloseLocation<.50],['50-75%',r=>r.triggerCloseLocation>=.50&&r.triggerCloseLocation<.75],['>=75%',r=>r.triggerCloseLocation>=.75]],baseline),
    ...thresholds(rows,'directionalBody',[['<0',r=>r.triggerDirectionalBody<0],['0-25%',r=>r.triggerDirectionalBody>=0&&r.triggerDirectionalBody<.25],['25-50%',r=>r.triggerDirectionalBody>=.25&&r.triggerDirectionalBody<.50],['>=50%',r=>r.triggerDirectionalBody>=.50]],baseline),
    ...thresholds(rows,'oppositeWick',[['<25%',r=>r.triggerOppositeWickFraction<.25],['25-50%',r=>r.triggerOppositeWickFraction>=.25&&r.triggerOppositeWickFraction<.50],['>=50%',r=>r.triggerOppositeWickFraction>=.50]],baseline)
  ];
  const interaction=[];
  const predicates=[['delay<=1',r=>r.triggerDelay<=1],['delay>=2',r=>r.triggerDelay>=2],['body>=50',r=>r.triggerBodyFraction>=.5],['close>=75',r=>r.triggerCloseLocation>=.75],['dirBody>=50',r=>r.triggerDirectionalBody>=.5],['oppWick<25',r=>r.triggerOppositeWickFraction<.25],['depth<25',r=>r.correctionDepth<.25],['ext<10',r=>r.triggerExtension<.10]];
  for(let a=0;a<predicates.length;a++) for(let b=a+1;b<predicates.length;b++){const [na,pa]=predicates[a],[nb,pb]=predicates[b];const s=bucket(`${na} AND ${nb}`,rows,r=>pa(r)&&pb(r),baseline);if(s.n>=MIN_N)interaction.push(s);}
  interaction.sort((a,b)=>b.avgR-a.avgR);
  const winners=rows.filter(r=>r.r>0), losers=rows.filter(r=>r.r<0); const featureSummary={};
  for(const f of ['triggerBodyFraction','triggerCloseLocation','triggerDirectionalBody','triggerOppositeWickFraction','triggerDelay','correctionDepth','triggerExtension','stopToImpulse']){const vals=arr=>arr.map(r=>Number(r[f])).filter(Number.isFinite).sort((a,b)=>a-b);const stat=arr=>{const v=vals(arr);const q=p=>v.length?v[Math.min(v.length-1,Math.floor((v.length-1)*p))]:null;return {n:v.length,p10:q(.1),p25:q(.25),p50:q(.5),p75:q(.75),p90:q(.9),mean:v.length?v.reduce((a,b)=>a+b,0)/v.length:null};};featureSummary[f]={winners:stat(winners),losers:stat(losers)};}
  const report={strategy:'Strategy A',mode:'ENTRY_TRIGGER_MICROSTRUCTURE_ROOT_CAUSE_PREHOLDOUT',timeframe:tf,candles:candles.length,scope:{preHoldoutCandles:PRE,freshHoldoutExcluded:true},methodology:{outcomeSource:'canonical baseline',featureSource:'direct baseline-path forensic plus trigger candle OHLC',purpose:'diagnostic mechanism attribution only; no threshold optimization or production change',minN:MIN_N},parity:{baselineResolved:trades.length,forensicMatched:rows.length},baseline,descriptors:bins,topInteractions:interaction.slice(0,20),featureSummary,outcome:{winners:metrics(winners),losers:metrics(losers)}};
  await mkdir(OUT_DIR,{recursive:true}); const out=resolve(OUT_DIR,`${tf}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: n=${baseline.n} avgR=${baseline.avgR.toFixed(4)} PF=${baseline.PF?.toFixed(4)??'n/a'} matched=${rows.length}`);
  for(const d of bins) console.log(`  ${d.name}: n=${d.n} avgR=${d.avgR.toFixed(4)} PF=${d.PF?.toFixed(3)??'n/a'} delta=${d.deltaAvgR.toFixed(4)} pass=${d.pass}`);
  console.log(`  top interactions: ${interaction.slice(0,8).map(x=>`${x.name} n=${x.n} avgR=${x.avgR.toFixed(3)} PF=${x.PF?.toFixed(2)??'n/a'}`).join(' | ')}`);
  console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
