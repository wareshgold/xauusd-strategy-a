import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-pre-ny-structural-chain-forensics');
const TIMEFRAMES=['1min','5min'];

function summarize(rows){const a=rows.filter(r=>Number.isFinite(r.rMultiple));const gp=a.filter(r=>r.rMultiple>0).reduce((s,r)=>s+r.rMultiple,0);const gl=a.filter(r=>r.rMultiple<0).reduce((s,r)=>s-r.rMultiple,0);return{n:a.length,wins:a.filter(r=>r.rMultiple>0).length,losses:a.filter(r=>r.rMultiple<0).length,PF:gl?gp/gl:null,avgR:a.length?a.reduce((s,r)=>s+r.rMultiple,0)/a.length:0,totalR:a.reduce((s,r)=>s+r.rMultiple,0)};}
function dd(rows){let e=0,p=0,m=0;for(const r of rows.filter(x=>Number.isFinite(x.rMultiple))){e+=r.rMultiple;p=Math.max(p,e);m=Math.max(m,p-e);}return m;}
function dateKey(t){const d=new Date(t);return Number.isNaN(d.getTime())?'UNKNOWN':d.toISOString().slice(0,10);}
function stage(r){return{
  spike:Boolean(r.opportunitySpike),
  sweep:Number.isInteger(r.sweepIndex),
  bos:Number.isInteger(r.bosIndex),
  displacement:Number.isInteger(r.displacementIndex),
  expansion:Number.isInteger(r.expansionIndex),
  fvg:Number.isInteger(r.fvgIndex),
  fvgRetest:Boolean(r.fvgRetest),
  sequenceComplete:Boolean(r.sequenceComplete),
};}
function chainPredicates(){return[
 ['SPIKE',r=>r.s],
 ['SPIKE+SWEEP',r=>r.s&&r.sw],
 ['SPIKE+SWEEP+BOS',r=>r.s&&r.sw&&r.b],
 ['SPIKE+SWEEP+BOS+DISPLACEMENT',r=>r.s&&r.sw&&r.b&&r.d],
 ['SPIKE+SWEEP+BOS+DISPLACEMENT+FVG',r=>r.s&&r.sw&&r.b&&r.d&&r.f],
 ['SPIKE+SWEEP+BOS+DISPLACEMENT+FVG_RETEST',r=>r.s&&r.sw&&r.b&&r.d&&r.fr],
 ['SPIKE+EXPANSION+FVG_RETEST',r=>r.s&&r.e&&r.fr],
];}
function decorate(row){const x=stage(row);return{...row,...x,s:x.spike,sw:x.sweep,b:x.bos,d:x.displacement,e:x.expansion,f:x.fvg,fr:x.fvgRetest,structuralCount:[x.sweep,x.bos,x.displacement,x.expansion,x.fvg,x.fvgRetest].filter(Boolean).length};}
function rank(rows){return [...rows].sort((a,b)=>b.structuralCount-a.structuralCount||Number(b.sequenceComplete)-Number(a.sequenceComplete)||Number(b.fvgRetest)-Number(a.fvgRetest)||Number(b.expansion)-Number(a.expansion)||new Date(a.entryTime)-new Date(b.entryTime));}
function dailySelect(rows,k){const groups=new Map();for(const r of rows){const key=dateKey(r.entryTime);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r);}const selected=[];for(const rs of groups.values())selected.push(...rank(rs).slice(0,k));return selected;}

async function run(timeframe){
 const path=resolve(ROOT,`data/reports/strategy-a-opportunity-window-structural-forensics/${timeframe}.json`);
 const src=JSON.parse(await readFile(path,'utf8'));
 const all=(src.tradeRows||[]).filter(r=>Number.isFinite(r.rMultiple)).map(decorate);
 const pre=all.filter(r=>r.opportunityWindow==='PRE_NY_BUILD');
 const oosIndex=Math.floor(pre.length*.5),oos=pre.slice(oosIndex);
 const chains=chainPredicates().map(([name,p])=>{const a=pre.filter(p),oo=oos.filter(p),comp=oos.filter(r=>!p(r));return{name,all:{...summarize(a),maxDD:dd(a)},oos:{...summarize(oo),maxDD:dd(oo)},oosComplement:{...summarize(comp),maxDD:dd(comp)}};});
 const caps=[1,2,3,4,5].map(k=>{const selected=dailySelect(pre,k),selectedOOS=dailySelect(oos,k),days=new Set(pre.map(r=>dateKey(r.entryTime))).size,oosDays=new Set(oos.map(r=>dateKey(r.entryTime))).size;return{maxTradesPerDay:k,all:{...summarize(selected),maxDD:dd(selected),days,avgSelectedPerDay:days?selected.length/days:0},oos:{...summarize(selectedOOS),maxDD:dd(selectedOOS),days:oosDays,avgSelectedPerDay:oosDays?selectedOOS.length/oosDays:0}};});
 const chainCaps=chainPredicates().map(([name,p])=>{const cand=pre.filter(p),oo=oos.filter(p);return{name,candidateN:cand.length,oosN:oo.length,caps:[1,2,3,4,5].map(k=>{const s=dailySelect(cand,k),so=dailySelect(oo,k);return{maxTradesPerDay:k,all:summarize(s),oos:summarize(so)};})};});
 const byDirection=['BUY','SELL'].map(d=>{const a=pre.filter(r=>r.direction===d),oo=oos.filter(r=>r.direction===d);return{direction:d,all:summarize(a),oos:summarize(oo)};});
 const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_PRE_NY_STRUCTURAL_CHAIN_FORENSICS',timeframe,scope:'PRE_NY_BUILD only; chronological second-half OOS; no rule selected',methodology:{windowUTC:'11:00-13:00',spike:'existing opportunity-window structural forensic spike classification',chain:'pre-entry structural flags already computed by opportunity-window structural forensic',ranking:'deterministic pre-entry rank: structuralCount, then sequenceComplete, FVG retest, expansion, then entry time',dailyCap:'select at most K ranked candidates per UTC calendar day; K=1..5',important:'daily cap is a research filter, not a requirement to manufacture a signal; days with no qualifying setup remain no-trade'},coverage:{allPreNY:pre.length,oosPreNY:oos.length,allDays:new Set(pre.map(r=>dateKey(r.entryTime))).size,oosDays:new Set(oos.map(r=>dateKey(r.entryTime))).size},overall:{all:summarize(pre),oos:summarize(oos)},chains,caps,chainCaps,byDirection,tradeRows:pre,nextResearchQuestion:'Only promote a compact chain if it remains positive OOS with meaningful sample size and survives an untouched third chronological holdout; then test day-level selection stability.'};
 await mkdir(OUT_DIR,{recursive:true});const out=resolve(OUT_DIR,`${timeframe}.json`);await writeFile(out,JSON.stringify(report,null,2));
 console.log(`${timeframe}: PRE_NY trades=${pre.length} OOS=${oos.length}`);
 for(const c of chains)console.log(`  ${c.name}: all n=${c.all.n} PF=${c.all.PF?.toFixed(4)??'n/a'} | OOS n=${c.oos.n} PF=${c.oos.PF?.toFixed(4)??'n/a'} avgR=${c.oos.avgR.toFixed(4)} | complement PF=${c.oosComplement.PF?.toFixed(4)??'n/a'}`);
 for(const c of caps)console.log(`  CAP_${c.maxTradesPerDay}/day: all n=${c.all.n} PF=${c.all.PF?.toFixed(4)??'n/a'} avgR=${c.all.avgR.toFixed(4)} | OOS n=${c.oos.n} PF=${c.oos.PF?.toFixed(4)??'n/a'} avgR=${c.oos.avgR.toFixed(4)}`);
 console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES)await run(tf);
