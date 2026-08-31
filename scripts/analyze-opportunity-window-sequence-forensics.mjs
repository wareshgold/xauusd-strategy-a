import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-opportunity-window-sequence-forensics');
const TIMEFRAMES = ['1min', '5min'];

function median(values) { const a = values.filter(Number.isFinite).sort((x,y)=>x-y); if (!a.length) return null; const m=Math.floor(a.length/2); return a.length%2?a[m]:(a[m-1]+a[m])/2; }
function summarize(rows) {
  const u=rows.filter(x=>Number.isFinite(x.rMultiple));
  const win=u.filter(x=>x.rMultiple>0).reduce((s,x)=>s+x.rMultiple,0);
  const loss=u.filter(x=>x.rMultiple<0).reduce((s,x)=>s+Math.abs(x.rMultiple),0);
  return {n:u.length,wins:u.filter(x=>x.rMultiple>0).length,losses:u.filter(x=>x.rMultiple<0).length,PF:loss?win/loss:null,avgR:u.length?u.reduce((s,x)=>s+x.rMultiple,0)/u.length:0,totalR:u.reduce((s,x)=>s+x.rMultiple,0)};
}
function dd(rows) { let eq=0,peak=0,max=0; for(const x of rows.filter(r=>Number.isFinite(r.rMultiple))){eq+=x.rMultiple;peak=Math.max(peak,eq);max=Math.max(max,peak-eq);} return max; }
function bool(row,key){return Boolean(row[key]);}
function combo(rows,name,predicate){const yes=rows.filter(predicate),no=rows.filter(x=>!predicate(x));return{name,YES:{...summarize(yes),maxDD:dd(yes)},NO:{...summarize(no),maxDD:dd(no)}};}
function lag(row){const indices=['spikeIndex','sweepIndex','bosIndex','displacementIndex','expansionIndex','fvgIndex'].map(k=>row[k]).filter(Number.isInteger);return indices.length?row.entryIndex-Math.max(...indices):null;}

async function load(path){return JSON.parse(await readFile(path,'utf8'));}
async function run(timeframe){
  const source=await load(resolve(ROOT,`data/reports/strategy-a-opportunity-window-structural-forensics/${timeframe}.json`));
  const trades=source.tradeRows.filter(t=>Number.isFinite(t.rMultiple));
  const opportunity=trades.filter(t=>t.opportunityWindow!=='OTHER');
  const oos=trades.slice(Math.floor(trades.length*.5));
  const oosOpportunity=oos.filter(t=>t.opportunityWindow!=='OTHER');
  const rows=opportunity.map(t=>({...t,eventLag:lag(t)}));
  const predicates=[
    ['SPIKE+SWEEP',r=>r.opportunitySpike&&bool(r,'sweepIndex')],
    ['SWEEP+BOS',r=>bool(r,'sweepIndex')&&bool(r,'bosIndex')],
    ['BOS+DISPLACEMENT',r=>bool(r,'bosIndex')&&bool(r,'displacementIndex')],
    ['DISPLACEMENT+FVG',r=>bool(r,'displacementIndex')&&bool(r,'fvgIndex')],
    ['FVG+RETEST',r=>bool(r,'fvgRetest')],
    ['SWEEP+BOS+DISPLACEMENT',r=>bool(r,'sweepIndex')&&bool(r,'bosIndex')&&bool(r,'displacementIndex')],
    ['BOS+DISPLACEMENT+FVG',r=>bool(r,'bosIndex')&&bool(r,'displacementIndex')&&bool(r,'fvgIndex')],
    ['SWEEP+BOS+DISPLACEMENT+FVG_RETEST',r=>bool(r,'sweepIndex')&&bool(r,'bosIndex')&&bool(r,'displacementIndex')&&bool(r,'fvgIndex')&&bool(r,'fvgRetest')],
    ['EXPANSION+FVG_RETEST',r=>bool(r,'expansionIndex')&&bool(r,'fvgRetest')],
  ];
  const lagBands=[['LAG_0',r=>r.eventLag===0],['LAG_1_2',r=>r.eventLag>=1&&r.eventLag<=2],['LAG_3_5',r=>r.eventLag>=3&&r.eventLag<=5],['LAG_GE6',r=>r.eventLag>=6]];
  const byWindow=[...new Set(rows.map(r=>r.opportunityWindow))].map(window=>{
    const w=rows.filter(r=>r.opportunityWindow===window);
    return {window,...summarize(w),maxDD:dd(w),sequenceCombos:predicates.map(([name,p])=>({name,...summarize(w.filter(p))})),eventLag:{n:w.filter(r=>Number.isFinite(r.eventLag)).length,p50:median(w.map(r=>r.eventLag)),p90:median(w.map(r=>r.eventLag).filter(Number.isFinite).sort((a,b)=>a-b).slice(Math.floor(w.length*.9)))} };
  });
  const byCombo=predicates.map(([name,p])=>combo(rows,name,p));
  const byLag=lagBands.map(([name,p])=>({name,...summarize(rows.filter(p)),maxDD:dd(rows.filter(p))}));
  const byLagOOS=lagBands.map(([name,p])=>({name,...summarize(oosOpportunity.map(t=>({...t,eventLag:lag(t)})).filter(p))}));
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_OPPORTUNITY_WINDOW_SEQUENCE_FORENSICS',timeframe,sourceReport:`strategy-a-opportunity-window-structural-forensics/${timeframe}.json`,methodology:{scope:'only pre-entry classified trades inside defined opportunity windows',combos:'descriptive feature-presence intersections; no new thresholds optimized',eventLag:'entryIndex minus latest available pre-entry structural event index',oos:'second half of chronological matched trades',decisionRule:'no signal quota and no parameter selected from tiny samples'},overall:{...summarize(rows),maxDD:dd(rows)},byCombo,byLag,byLagOOS,byWindow,oos:{...summarize(oosOpportunity),maxDD:dd(oosOpportunity)},nextResearchQuestion:'Test only compact sequence candidates that show positive OOS with adequate sample size, then validate chronologically on a third holdout; do not optimize to daily trade count.'};
  await mkdir(REPORT_DIR,{recursive:true}); const out=resolve(REPORT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: opportunity=${rows.length} OOS=${oosOpportunity.length}`);
  console.log(`  overall PF=${summarize(rows).PF?.toFixed(4)??'n/a'} avgR=${summarize(rows).avgR.toFixed(4)}`);
  for(const x of byCombo) console.log(`  ${x.name}: YES n=${x.YES.n} PF=${x.YES.PF?.toFixed(4)??'n/a'} avgR=${x.YES.avgR.toFixed(4)} | NO n=${x.NO.n} PF=${x.NO.PF?.toFixed(4)??'n/a'} avgR=${x.NO.avgR.toFixed(4)}`);
  console.log('  OOS lag bands:'); for(const x of byLagOOS) console.log(`    ${x.name}: n=${x.n} PF=${x.PF?.toFixed(4)??'n/a'} avgR=${x.avgR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES) await run(tf);
