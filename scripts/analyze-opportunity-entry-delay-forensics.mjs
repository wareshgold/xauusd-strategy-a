import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-opportunity-entry-delay-forensics');
const TIMEFRAMES = ['1min', '5min'];
const BANDS = [
  ['D0_2', 0, 2], ['D3_5', 3, 5], ['D6_8', 6, 8], ['D9_12', 9, 12], ['D13_20', 13, 20], ['D21_PLUS', 21, Infinity]
];

function sum(rows){const a=rows.filter(r=>Number.isFinite(r.rMultiple));const gp=a.filter(r=>r.rMultiple>0).reduce((s,r)=>s+r.rMultiple,0);const gl=a.filter(r=>r.rMultiple<0).reduce((s,r)=>s-r.rMultiple,0);return {n:a.length,wins:a.filter(r=>r.rMultiple>0).length,losses:a.filter(r=>r.rMultiple<0).length,PF:gl?gp/gl:null,avgR:a.length?a.reduce((s,r)=>s+r.rMultiple,0)/a.length:0,totalR:a.reduce((s,r)=>s+r.rMultiple,0)};}
function dd(rows){let e=0,p=0,m=0;for(const r of rows.filter(x=>Number.isFinite(x.rMultiple))){e+=r.rMultiple;p=Math.max(p,e);m=Math.max(m,p-e);}return m;}
function pct(rows){const a=rows.filter(r=>Number.isFinite(r.rMultiple));return a.length?a.filter(r=>r.rMultiple>0).length/a.length:null;}
function num(r,...keys){for(const k of keys){if(Number.isFinite(r[k]))return r[k];}return null;}
function latestEvent(r){const keys=['spikeIndex','sweepIndex','bosIndex','displacementIndex','expansionIndex','fvgIndex'];const vals=keys.map(k=>r[k]).filter(Number.isInteger);return vals.length?Math.max(...vals):null;}
function delay(r){const entry=num(r,'entryIndex');const event=latestEvent(r);return Number.isInteger(entry)&&Number.isInteger(event)?entry-event:null;}
function group(rows,p){const a=rows.filter(p);return {...sum(a),winRate:pct(a),maxDD:dd(a)};}
function reportFor(rows, timeframe){
 const enriched=rows.map(r=>({...r,entryDelay:delay(r)}));
 const valid=enriched.filter(r=>Number.isFinite(r.entryDelay));
 const opportunity=enriched.filter(r=>r.opportunityWindow&&r.opportunityWindow!=='OTHER');
 const oos=opportunity.slice(Math.floor(opportunity.length/2));
 const bands=BANDS.map(([name,lo,hi])=>({name,lo,hi,all:group(opportunity,r=>r.entryDelay>=lo&&r.entryDelay<=hi),oos:group(oos,r=>r.entryDelay>=lo&&r.entryDelay<=hi)}));
 const byWindow=[...new Set(opportunity.map(r=>r.opportunityWindow))].map(w=>{const a=opportunity.filter(r=>r.opportunityWindow===w);return {window:w,...sum(a),maxDD:dd(a),delayP50:median(a.map(r=>r.entryDelay)),bands:BANDS.map(([name,lo,hi])=>({name,...sum(a.filter(r=>r.entryDelay>=lo&&r.entryDelay<=hi))}))};});
 const confirmations=[
  ['FVG_RETEST',r=>Boolean(r.fvgRetest)],
  ['EXPANSION',r=>Boolean(r.expansionIndex)],
  ['BOS+DISPLACEMENT',r=>Boolean(r.bosIndex)&&Boolean(r.displacementIndex)],
  ['SWEEP+BOS+DISPLACEMENT',r=>Boolean(r.sweepIndex)&&Boolean(r.bosIndex)&&Boolean(r.displacementIndex)]
 ];
 const confirmationDelay=BANDS.map(([name,lo,hi])=>({name,...Object.fromEntries(confirmations.map(([c,p])=>[c,group(oos,r=>r.entryDelay>=lo&&r.entryDelay<=hi&&p(r))]))}));
 return {strategy:'Strategy A / SP2L',mode:'RESEARCH_OPPORTUNITY_ENTRY_DELAY_FORENSICS',timeframe,methodology:{delay:'entryIndex minus latest pre-entry structural event index',scope:'Opportunity Window trades only',bands:BANDS.map(x=>x[0]),oos:'second chronological half of Opportunity Window trades',confirmations:'descriptive only; no optimization or signal rule change',important:'delay is a correlation diagnostic until validated on untouched data'},coverage:{opportunity:opportunity.length,delayKnown:opportunity.filter(r=>Number.isFinite(r.entryDelay)).length},overall:{...sum(opportunity),maxDD:dd(opportunity)},bands,confirmationDelay,byWindow,oos:{...sum(oos),maxDD:dd(oos)}};
}
function median(a){const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const m=Math.floor(x.length/2);return x.length%2?x[m]:(x[m-1]+x[m])/2;}
async function main(tf){const path=resolve(ROOT,`data/reports/strategy-a-opportunity-window-structural-forensics/${tf}.json`);const src=JSON.parse(await readFile(path,'utf8'));const rep=reportFor(src.tradeRows||[],tf);await mkdir(REPORT_DIR,{recursive:true});const out=resolve(REPORT_DIR,`${tf}.json`);await writeFile(out,JSON.stringify(rep,null,2));console.log(`${tf}: opportunity=${rep.coverage.opportunity} delayKnown=${rep.coverage.delayKnown}`);for(const b of rep.bands)console.log(`  ${b.name}: n=${b.all.n} PF=${b.all.PF?.toFixed(4)??'n/a'} avgR=${b.all.avgR.toFixed(4)} | OOS n=${b.oos.n} PF=${b.oos.PF?.toFixed(4)??'n/a'} avgR=${b.oos.avgR.toFixed(4)}`);console.log(`Report -> ${out}`);}
for(const tf of TIMEFRAMES)await main(tf);
