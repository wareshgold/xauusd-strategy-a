import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-entry-geometry-combination-forensics');
const TIMEFRAMES=['1min','5min'];
const MIN_OOS_N=10;
const TOP_N=30;

function summarize(rows){
  const a=rows.filter(r=>Number.isFinite(r.rMultiple));
  const gp=a.filter(r=>r.rMultiple>0).reduce((s,r)=>s+r.rMultiple,0);
  const gl=a.filter(r=>r.rMultiple<0).reduce((s,r)=>s-r.rMultiple,0);
  return {n:a.length,wins:a.filter(r=>r.rMultiple>0).length,losses:a.filter(r=>r.rMultiple<0).length,PF:gl?gp/gl:null,avgR:a.length?a.reduce((s,r)=>s+r.rMultiple,0)/a.length:0,totalR:a.reduce((s,r)=>s+r.rMultiple,0)};
}
function dd(rows){let e=0,p=0,m=0;for(const r of rows){if(!Number.isFinite(r.rMultiple))continue;e+=r.rMultiple;p=Math.max(p,e);m=Math.max(m,p-e);}return m;}
function bucket(x,cuts,labels){if(!Number.isFinite(x))return null;for(let i=0;i<cuts.length;i++)if(x<cuts[i])return labels[i];return labels.at(-1);}
function splitHalf(rows){const m=Math.floor(rows.length/2);return [rows.slice(0,m),rows.slice(m)];}

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

function classify(rows){
  return rows.map(r=>{const x={...r};for(const [key,cuts,labels] of defs)x[`${key}Bucket`]=bucket(r[key],cuts,labels);return x;});
}
function pairStats(rows,a,b){
  const [ka,la]=a,[kb,lb]=b;
  const out=[];
  for(const va of la)for(const vb of lb){
    const selected=rows.filter(r=>r[`${ka}Bucket`]===va&&r[`${kb}Bucket`]===vb);
    if(!selected.length)continue;
    const [dev,oos]=splitHalf(selected);
    const ds=summarize(dev),os=summarize(oos);
    out.push({featureA:ka,bucketA:va,featureB:kb,bucketB:vb,dev:{...ds,maxDD:dd(dev)},oos:{...os,maxDD:dd(oos)},eligibleForHoldout:Boolean(os.n>=MIN_OOS_N&&os.PF!=null&&os.PF>=1&&os.avgR>0)});
  }
  return out;
}
function rankCandidates(rows){
  return [...rows].filter(x=>x.oos.n>=MIN_OOS_N&&x.oos.PF!=null).sort((a,b)=>b.oos.PF-a.oos.PF||b.oos.avgR-a.oos.avgR||b.oos.n-a.oos.n);
}

async function run(timeframe){
  const srcPath=resolve(ROOT,`data/reports/strategy-a-entry-geometry-forensics/${timeframe}.json`);
  const src=JSON.parse(await readFile(srcPath,'utf8'));
  const raw=src.tradeRows||[];
  if(!raw.length)throw new Error(`${timeframe}: entry-geometry source has no tradeRows: ${srcPath}`);
  const missing=defs.map(([key])=>key).filter(key=>raw.every(r=>!Number.isFinite(r[key])));
  if(missing.length)throw new Error(`${timeframe}: stale/incompatible entry-geometry report; no finite values for ${missing.join(', ')}. Regenerate it first with: node .\\scripts\\analyze-entry-geometry-forensics.mjs`);
  const rows=classify(raw.filter(r=>Number.isFinite(r.rMultiple)).sort((a,b)=>new Date(a.entryTime)-new Date(b.entryTime)));
  const coverage=Object.fromEntries(defs.map(([key])=>[key,rows.filter(r=>Number.isFinite(r[key])).length]));
  const pairs=[];
  for(let i=0;i<defs.length;i++)for(let j=i+1;j<defs.length;j++)pairs.push(...pairStats(rows,defs[i],defs[j]));
  const eligible=rankCandidates(pairs);
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_ENTRY_GEOMETRY_COMBINATION_FORENSICS',timeframe,scope:'All baseline trades with geometry features; exhaustive pairwise bucket combinations; chronological half split; maximum two features; no production rule changes',methodology:{source:'strategy-a-entry-geometry-forensics tradeRows',search:'all unordered pairs across the eight pre-declared geometry features and their fixed research buckets',complexity:'maximum two features; no three-way combinations or continuous threshold search',split:'first half DEV, second half OOS, chronological by entryTime',candidateGate:`OOS n >= ${MIN_OOS_N}, PF >= 1, avgR > 0`,nextGate:'Any candidate passing this gate is hypothesis-only and must be frozen before third chronological holdout testing.',warning:'pairwise search creates multiple-comparison risk; high OOS PF alone is not evidence of a real edge.'},coverage:{classifiedTrades:rows.length,featureFiniteCounts:coverage,pairTests:pairs.length},overall:{...summarize(rows),maxDD:dd(rows)},topOOS:eligible.slice(0,TOP_N),eligibleCount:eligible.length,allPairResults:pairs,nextResearchQuestion:'Freeze only a small number of pre-specified top candidates, then evaluate each on untouched chronological thirds (development/validation/holdout) and by BUY/SELL/session/day robustness.'};
  await mkdir(OUT_DIR,{recursive:true});
  const out=resolve(OUT_DIR,`${timeframe}.json`);await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: trades=${rows.length} pairTests=${pairs.length} eligibleOOS=${eligible.length}`);
  for(const c of eligible.slice(0,TOP_N))console.log(`  ${c.featureA}=${c.bucketA} + ${c.featureB}=${c.bucketB}: DEV n=${c.dev.n} PF=${c.dev.PF?.toFixed(4)??'n/a'} | OOS n=${c.oos.n} PF=${c.oos.PF?.toFixed(4)??'n/a'} avgR=${c.oos.avgR.toFixed(4)} totalR=${c.oos.totalR.toFixed(4)} holdoutCandidate=${c.eligibleForHoldout}`);
  console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES)await run(tf);
