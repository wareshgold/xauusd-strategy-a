import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-spike-structure-attribution');
const REOPEN_EXCLUSION_MINUTES = [0, 15, 30, 45, 60];
const LOOKBACK = 60;
const TF = [
  { name: '1min', minutes: 1 },
  { name: '5min', minutes: 5 },
];

const mean = a => { const v=a.filter(Number.isFinite); return v.length ? v.reduce((s,x)=>s+x,0)/v.length : null; };
const median = a => { const v=a.filter(Number.isFinite).sort((a,b)=>a-b); if(!v.length)return null; const m=Math.floor(v.length/2); return v.length%2?v[m]:(v[m-1]+v[m])/2; };
const quantile = (a,p) => { const v=a.filter(Number.isFinite).sort((a,b)=>a-b); if(!v.length)return null; const x=(v.length-1)*p,l=Math.floor(x),h=Math.ceil(x); return l===h?v[l]:v[l]+(v[h]-v[l])*(x-l); };
const parse = s => { const d=new Date(s.includes('T') ? s : s.replace(' ','T')+'Z'); return Number.isNaN(d.getTime())?null:d; };
const tr = (c,p) => Math.max(c.high-c.low,Math.abs(c.high-p),Math.abs(c.low-p));
const isReopen = d => d?.getUTCDay()===0 && d?.getUTCHours()===22 && d?.getUTCMinutes()===0;
const key = (v) => v == null ? 'NA' : String(v);

function metrics(rows){
 const rs=rows.map(x=>x.r).filter(Number.isFinite);
 const wins=rs.filter(x=>x>0).length, losses=rs.filter(x=>x<0).length;
 const grossWin=rs.filter(x=>x>0).reduce((s,x)=>s+x,0), grossLoss=-rs.filter(x=>x<0).reduce((s,x)=>s+x,0);
 return {n:rs.length,wins,losses,winRate:rs.length?wins/rs.length:null,avgR:mean(rs),expectancyR:mean(rs),profitFactor:grossLoss?grossWin/grossLoss:null,totalR:rs.reduce((s,x)=>s+x,0)};
}
function classify(v){ if(v==null)return 'NA'; if(v<=0)return '0'; if(v===1)return '1'; if(v===2)return '2'; return '3+'; }

async function run(tf){
 const candlesData=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf.name}.json`),'utf8'));
 const baseline=JSON.parse(await readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf.name}.json`),'utf8'));
 const candles=candlesData.candles;
 const indexByTs=new Map(candles.map((c,i)=>[c.timestamp,i]));
 const trv=candles.map((c,i)=>i?tr(c,candles[i-1].close):null);
 const rollingP90=candles.map((_,i)=>i>=LOOKBACK?quantile(trv.slice(i-LOOKBACK,i),.9):null);
 const reopenStarts=[];
 for(let i=0;i<candles.length;i++){const d=parse(candles[i].timestamp);if(isReopen(d))reopenStarts.push(parse(candles[i].timestamp).getTime());}
 function excluded(ts,mins){const t=parse(ts)?.getTime();return Number.isFinite(t)&&reopenStarts.some(x=>t>=x&&t<x+mins*60000);}
 const trades=baseline.trades.map(t=>{
   const i=t.entryIndex ?? indexByTs.get(t.entryTime);
   if(i==null || i<LOOKBACK || !Number.isFinite(trv[i-1])) return null;
   const prior=i-1;
   const score=rollingP90[prior] ? trv[prior]/rollingP90[prior] : null;
   return {...t,index:i,priorIndex:prior,priorSpikeScore:score,priorSpike:score!=null&&score>=1};
 }).filter(Boolean);
 const exclusions={};
 for(const mins of REOPEN_EXCLUSION_MINUTES){
   const eligible=trades.filter(t=>!excluded(t.entryTime,mins));
   const spike=eligible.filter(t=>t.priorSpike), non=eligible.filter(t=>!t.priorSpike);
   const base=metrics(eligible.map(t=>({r:t.rMultiple})));
   const groups={
     overall:{spike:metrics(spike.map(t=>({r:t.rMultiple}))),nonSpike:metrics(non.map(t=>({r:t.rMultiple})))},
     structureScore:{}, qualityGrade:{}, session:{}, direction:{}, pgap:{}, emaAligned:{}, overlapBucket:{}
   };
   const add=(container,k)=>{const rows=eligible.filter(t=>String(t[k.field])===String(k.value));};
   for(const v of ['0','1','2','3+']){const g=eligible.filter(t=>classify(t.structureScore)===v);groups.structureScore[v]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   for(const v of ['A','B','C','D']){const g=eligible.filter(t=>key(t.qualityGrade)===v);groups.qualityGrade[v]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   for(const v of ['LONDON','NEW_YORK','ASIA','OVERLAP','NA']){const g=eligible.filter(t=>key(t.session)===v);groups.session[v]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   for(const v of ['BUY','SELL','NA']){const g=eligible.filter(t=>key(t.direction)===v);groups.direction[v]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   for(const v of ['true','false','NA']){const g=eligible.filter(t=>key(t.hasPGAPEvidence)===v);groups.pgap[v]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   for(const v of ['true','false','NA']){const g=eligible.filter(t=>key(t.emaAligned)===v);groups.emaAligned[v]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   for(const [lo,hi,name] of [[-Infinity,.25,'<.25'],[.25,.5,'.25-.5'],[.5,.75,'.5-.75'],[.75,Infinity,'>=.75']]){const g=eligible.filter(t=>Number.isFinite(t.overlapScore)&&t.overlapScore>=lo&&t.overlapScore<hi);groups.overlapBucket[name]={spike:metrics(g.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),nonSpike:metrics(g.filter(t=>!t.priorSpike).map(t=>({r:t.rMultiple})))}};
   exclusions[String(mins)]={reopenExcluded:trades.length-eligible.length,eligibleTrades:eligible.length,baseline:base,spike:metrics(spike.map(t=>({r:t.rMultiple}))),nonSpike:metrics(non.map(t=>({r:t.rMultiple}))),deltaR:(mean(spike.map(t=>t.rMultiple))??0)-(mean(non.map(t=>t.rMultiple))??0),groups};
 }
 const report={generatedAt:new Date().toISOString(),timeframe:tf.name,definition:'Leakage-safe structural attribution. A prior spike is the immediately preceding candle whose TR is at least the 90th percentile of the preceding 60 candle TR values. Sunday 22:00 UTC reopen impact is tested as sensitivity only. No global/future threshold is used and no production rule is selected.',data:{candles:candles.length,from:candles[0]?.timestamp,to:candles.at(-1)?.timestamp,baselineTrades:baseline.trades.length},sensitivity:exclusions,diagnostics:{tradePriorSpikeCoverage:metrics(trades.filter(t=>t.priorSpike).map(t=>({r:t.rMultiple}))),warning:'This is attribution/diagnostic research. Positive conditional differences do not establish causal independence or OOS validity.'}};
 await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,`${tf.name}.json`),JSON.stringify(report,null,2)+'\n');
 console.log(`\n${tf.name}: baselineTrades=${baseline.trades.length}`);
 for(const mins of REOPEN_EXCLUSION_MINUTES){const x=exclusions[String(mins)];console.log(`${mins}m eligible=${x.eligibleTrades} spikeN=${x.spike.n} spikeAvgR=${x.spike.avgR?.toFixed(4)} nonN=${x.nonSpike.n} nonAvgR=${x.nonSpike.avgR?.toFixed(4)} deltaR=${x.deltaR.toFixed(4)}`)}
}
for(const tf of TF) await run(tf);
console.log(`Report -> ${OUT}`);
