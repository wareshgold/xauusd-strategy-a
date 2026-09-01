import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT=resolve(ROOT,'data/reports/strategy-a-spike-structure-attribution');
const LOOKBACK=60, FIXED_SPIKE=2.0, MIN_CELL_N=20, BOOT=5000;
const TF=['1min','5min'], REOPEN=[0,15,30,45,60];
const mean=a=>{const v=a.filter(Number.isFinite);return v.length?v.reduce((s,x)=>s+x,0)/v.length:null};
const median=a=>{const v=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!v.length)return null;const m=Math.floor(v.length/2);return v.length%2?v[m]:(v[m-1]+v[m])/2};
const q=(a,p)=>{const v=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!v.length)return null;const x=(v.length-1)*p,l=Math.floor(x),h=Math.ceil(x);return l===h?v[l]:v[l]+(v[h]-v[l])*(x-l)};
const parse=s=>{const d=new Date(s.includes('T')?s:s.replace(' ','T')+'Z');return Number.isNaN(d.getTime())?null:d};
const tr=(c,p)=>Math.max(c.high-c.low,Math.abs(c.high-p),Math.abs(c.low-p));
const excluded=(ts,mins)=>{if(!mins)return false;const d=parse(ts);if(!d||d.getUTCDay()!==0)return false;const delta=d.getUTCHours()*60+d.getUTCMinutes()-1320;return delta>=0&&delta<mins};
const metrics=rows=>{const r=rows.map(x=>x.r).filter(Number.isFinite),w=r.filter(x=>x>0),l=r.filter(x=>x<0);return{n:r.length,wins:w.length,losses:l.length,winRate:r.length?w.length/r.length:null,avgR:mean(r),totalR:r.reduce((s,x)=>s+x,0),profitFactor:l.length?w.reduce((s,x)=>s+x,0)/-l.reduce((s,x)=>s+x,0):null}};
function boot(a,b){if(a.length<MIN_CELL_N||b.length<MIN_CELL_N)return null;let seed=0x12345678,r=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296};const z=[];for(let k=0;k<BOOT;k++){let x=0,y=0;for(let i=0;i<a.length;i++)x+=a[Math.floor(r()*a.length)];for(let i=0;i<b.length;i++)y+=b[Math.floor(r()*b.length)];z.push(x/a.length-y/b.length)}z.sort((x,y)=>x-y);return{lo:q(z,.025),hi:q(z,.975),iterations:BOOT}}
function compare(rows){const a=rows.filter(x=>x.spike).map(x=>({r:x.rMultiple})),b=rows.filter(x=>!x.spike).map(x=>({r:x.rMultiple})),ma=metrics(a),mb=metrics(b);return{spike:ma,nonSpike:mb,deltaR:ma.avgR!=null&&mb.avgR!=null?ma.avgR-mb.avgR:null,bootstrap95:boot(a.map(x=>x.r),b.map(x=>x.r))}}
function overlap(x){if(!Number.isFinite(x))return'NA';if(x<.25)return'<.25';if(x<.5)return'.25-.5';if(x<.75)return'.5-.75';return'>=.75'}
const fmt=x=>Number.isFinite(x)?x.toFixed(4):'n/a';
async function run(tf){
 const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')).candles;
 const baseline=JSON.parse(await readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf}.json`),'utf8'));
 const resolvedTrades=baseline.trades.filter(t=>Number.isFinite(t.rMultiple));
 if(baseline.metrics?.trades!==resolvedTrades.length)throw new Error(`${tf}: baseline mismatch metrics.trades=${baseline.metrics?.trades} resolvedTrades=${resolvedTrades.length} rawTrades=${baseline.trades?.length}`);
 const idx=new Map(candles.map((c,i)=>[c.timestamp,i]));const trv=candles.map((c,i)=>i?tr(c,candles[i-1].close):null);
 const score=candles.map((_,i)=>i>=LOOKBACK?(()=>{const b=median(trv.slice(i-LOOKBACK,i));return b>0?trv[i]/b:null})():null);
 const trades=resolvedTrades.map(t=>{const i=Number.isInteger(t.entryIndex)?t.entryIndex:idx.get(t.entryTime);if(i==null||i<LOOKBACK||!Number.isFinite(t.rMultiple))return null;return{...t,index:i,priorScore:score[i-1]}}).filter(Boolean);
 const sensitivity={};
 for(const mins of REOPEN){const eligible=trades.filter(t=>!excluded(t.entryTime,mins));const tagged=eligible.map(t=>({...t,spike:Number.isFinite(t.priorScore)&&t.priorScore>=FIXED_SPIKE,descriptiveSpike:Number.isFinite(t.priorScore)&&t.priorScore>=q(eligible.map(x=>x.priorScore),.9)}));const cut=q(eligible.map(x=>x.priorScore),.9);const groups={structureScore:{},qualityGrade:{},session:{},direction:{},pgap:{},emaAligned:{},overlap:{}};
  for(const v of ['0','1','2','3+']){const r=tagged.filter(t=>{const x=t.structureScore;if(x==null)return v==='NA';const bucket=x<=0?'0':x===1?'1':x===2?'2':'3+';return bucket===v});if(r.length>=MIN_CELL_N)groups.structureScore[v]=compare(r)}
  for(const v of ['A','B','C','D','NA']){const r=tagged.filter(t=>(t.qualityGrade??'NA')===v);if(r.length>=MIN_CELL_N)groups.qualityGrade[v]=compare(r)}
  for(const v of ['LONDON','NEW_YORK','ASIA','OVERLAP','NA']){const r=tagged.filter(t=>(t.session??'NA')===v);if(r.length>=MIN_CELL_N)groups.session[v]=compare(r)}
  for(const v of ['BUY','SELL','NA']){const r=tagged.filter(t=>(t.direction??'NA')===v);if(r.length>=MIN_CELL_N)groups.direction[v]=compare(r)}
  for(const v of ['true','false','NA']){const r=tagged.filter(t=>String(t.hasPGAPEvidence??'NA')===v);if(r.length>=MIN_CELL_N)groups.pgap[v]=compare(r)}
  for(const v of ['true','false','NA']){const r=tagged.filter(t=>String(t.emaAligned??'NA')===v);if(r.length>=MIN_CELL_N)groups.emaAligned[v]=compare(r)}
  for(const v of ['<.25','.25-.5','.5-.75','>=.75','NA']){const r=tagged.filter(t=>overlap(t.overlapScore)===v);if(r.length>=MIN_CELL_N)groups.overlap[v]=compare(r)}
  sensitivity[String(mins)]={reopenExclusionMinutes:mins,eligibleTrades:eligible.length,fixedSpikeThreshold:FIXED_SPIKE,fixedSpikeN:tagged.filter(t=>t.spike).length,nonSpikeN:tagged.filter(t=>!t.spike).length,descriptiveP90Cut:cut,fixedOverall:compare(tagged),descriptiveP90Overall:compare(tagged.map(t=>({...t,spike:t.descriptiveSpike}))),groups};}
 const report={generatedAt:new Date().toISOString(),timeframe:tf,methodology:{spike:'prior-bar TR / median(previous 60 TR) >= fixed 2.0',descriptiveP90:'P90 is reported only for descriptive comparison and is never promoted',reopen:'Sunday 22:00 UTC, 0/15/30/45/60 minute sensitivity',minimumInteractionCellN:MIN_CELL_N,bootstrapIterations:BOOT,resolvedTradePolicy:'Only trades with finite rMultiple are included; raw baseline trades without a resolved outcome are excluded because canonical baseline metrics count resolved outcomes only.'},baselineReference:{rawTrades:baseline.trades?.length,resolvedTrades:resolvedTrades.length,metricsTrades:baseline.metrics?.trades,averageR:baseline.metrics?.averageR,profitFactor:baseline.metrics?.profitFactor},sensitivities:sensitivity,decisionGate:{status:'RESEARCH_ONLY',rule:'Do not add spike to Strategy A unless fixed-definition interaction remains positive with adequate N and bootstrap CI excludes zero across reopen sensitivities, then survives untouched holdout.'}};
 await mkdir(OUT,{recursive:true});const out=resolve(OUT,`${tf}.json`);await writeFile(out,JSON.stringify(report,null,2)+'\n');console.log(`\n${tf}: baselineResolvedTrades=${resolvedTrades.length} rawTrades=${baseline.trades.length}`);for(const m of REOPEN){const x=sensitivity[String(m)],b=x.fixedOverall.bootstrap95;console.log(`${m}m fixed2.0 spikeN=${x.fixedSpikeN} spikeAvgR=${fmt(x.fixedOverall.spike.avgR)} nonN=${x.nonSpikeN} nonAvgR=${fmt(x.fixedOverall.nonSpike.avgR)} deltaR=${fmt(x.fixedOverall.deltaR)} CI=[${b?fmt(b.lo):'n/a'},${b?fmt(b.hi):'n/a'}] p90Cut=${fmt(x.descriptiveP90Cut)}`)}console.log(`Report -> ${out}`)}
for(const tf of TF)await run(tf);
