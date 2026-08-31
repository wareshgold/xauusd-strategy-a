import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-pre-ny-third-holdout-stability');
const TIMEFRAMES=['1min','5min'];
const PARTS=3;
const MIN_MEANINGFUL_OOS=10;

function summarize(rows){
  const a=rows.filter(r=>Number.isFinite(r.rMultiple));
  const gp=a.filter(r=>r.rMultiple>0).reduce((s,r)=>s+r.rMultiple,0);
  const gl=a.filter(r=>r.rMultiple<0).reduce((s,r)=>s-r.rMultiple,0);
  return {
    n:a.length,
    wins:a.filter(r=>r.rMultiple>0).length,
    losses:a.filter(r=>r.rMultiple<0).length,
    PF:gl?gp/gl:null,
    avgR:a.length?a.reduce((s,r)=>s+r.rMultiple,0)/a.length:0,
    totalR:a.reduce((s,r)=>s+r.rMultiple,0),
  };
}

function dd(rows){
  let equity=0,peak=0,max=0;
  for(const r of rows.filter(x=>Number.isFinite(x.rMultiple))){
    equity+=r.rMultiple;
    peak=Math.max(peak,equity);
    max=Math.max(max,peak-equity);
  }
  return max;
}

function dateKey(v){
  const d=new Date(v);
  return Number.isNaN(d.getTime())?'UNKNOWN':d.toISOString().slice(0,10);
}

function rank(rows){
  return [...rows].sort((a,b)=>
    Number(b.sequenceComplete)-Number(a.sequenceComplete)||
    Number(b.fvgRetest)-Number(a.fvgRetest)||
    Number(b.expansion)-Number(a.expansion)||
    new Date(a.entryTime)-new Date(b.entryTime)
  );
}

function dailySelect(rows,k){
  const groups=new Map();
  for(const r of rows){
    const key=dateKey(r.entryTime);
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(r);
  }
  const selected=[];
  for(const rs of groups.values())selected.push(...rank(rs).slice(0,k));
  return selected;
}

function candidatePredicates(){
  return [
    ['SPIKE',r=>r.s],
    ['SPIKE+SWEEP',r=>r.s&&r.sw],
    ['SPIKE+EXPANSION+FVG_RETEST',r=>r.s&&r.e&&r.fr],
  ];
}

function decorate(row){
  return {
    ...row,
    s:Boolean(row.spike),
    sw:Boolean(row.sweep),
    b:Boolean(row.bos),
    d:Boolean(row.displacement),
    e:Boolean(row.expansion),
    f:Boolean(row.fvg),
    fr:Boolean(row.fvgRetest),
    sequenceComplete:Boolean(row.sequenceComplete),
  };
}

function splitThree(rows){
  const n=rows.length;
  const a=Math.floor(n/PARTS);
  const b=Math.floor((2*n)/PARTS);
  return [rows.slice(0,a),rows.slice(a,b),rows.slice(b)];
}

function evaluate(rows){
  const [development,validation,holdout]=splitThree(rows);
  const sets={development,validation,holdout};
  const candidates=candidatePredicates().map(([name,p])=>{
    const byPart={};
    for(const [part,partRows] of Object.entries(sets)){
      const selected=partRows.filter(p);
      byPart[part]={...summarize(selected),maxDD:dd(selected),meaningfulN:selected.length>=MIN_MEANINGFUL_OOS};
    }
    const hold=byPart.holdout;
    const survives=hold.meaningfulN&&hold.PF!=null&&hold.PF>=1&&hold.avgR>0;
    return {name,byPart,holdoutSurvivesMeaningfulPositive:survives};
  });

  const caps=[1,2,3,4,5].map(k=>{
    const byPart={};
    for(const [part,partRows] of Object.entries(sets)){
      const selected=dailySelect(partRows,k);
      byPart[part]={...summarize(selected),maxDD:dd(selected),days:new Set(partRows.map(r=>dateKey(r.entryTime))).size};
    }
    const h=byPart.holdout;
    return {maxTradesPerDay:k,byPart,holdoutSurvivesMeaningfulPositive:h.meaningfulN&&h.PF!=null&&h.PF>=1&&h.avgR>0};
  });

  return {
    partitions:{development:development.length,validation:validation.length,holdout:holdout.length},
    candidates,
    dailyCaps:caps,
  };
}

async function run(timeframe){
  const srcPath=resolve(ROOT,`data/reports/strategy-a-pre-ny-structural-chain-forensics/${timeframe}.json`);
  const src=JSON.parse(await readFile(srcPath,'utf8'));
  const rows=(src.tradeRows||[])
    .filter(r=>Number.isFinite(r.rMultiple)&&r.opportunityWindow==='PRE_NY_BUILD')
    .map(decorate)
    .sort((a,b)=>new Date(a.entryTime)-new Date(b.entryTime));

  const report={
    strategy:'Strategy A / SP2L',
    mode:'RESEARCH_PRE_NY_THIRD_HOLDOUT_STABILITY',
    timeframe,
    scope:'PRE_NY_BUILD only; fixed pre-existing candidates; three chronological partitions; no threshold optimization',
    methodology:{
      source:'existing PRE-NY structural-chain forensic tradeRows',
      partitions:'first third = development, middle third = validation, final third = untouched holdout',
      candidates:'fixed previously observed structural predicates; no new feature or threshold is fitted here',
      dailyCap:'deterministic rank-based cap K=1..5 per UTC calendar day; no candidate is manufactured on empty days',
      meaningfulHoldoutN:MIN_MEANINGFUL_OOS,
      promotionGate:'diagnostic only: meaningful holdout sample, PF >= 1, and avgR > 0; passing this report does not authorize production',
      warning:'small samples remain hypothesis-generating even when PF is high',
    },
    coverage:{trades:rows.length,days:new Set(rows.map(r=>dateKey(r.entryTime))).size},
    evaluation:evaluate(rows),
    tradeRows:rows,
    nextResearchQuestion:'If a candidate is positive on the untouched third, freeze it and validate on a separate dataset/source and by BUY/SELL/session/day robustness before implementation.',
  };

  await mkdir(OUT_DIR,{recursive:true});
  const out=resolve(OUT_DIR,`${timeframe}.json`);
  await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: PRE_NY trades=${rows.length} dev/val/holdout=${report.evaluation.partitions.development}/${report.evaluation.partitions.validation}/${report.evaluation.partitions.holdout}`);
  for(const c of report.evaluation.candidates){
    const d=c.byPart.development,v=c.byPart.validation,h=c.byPart.holdout;
    console.log(`  ${c.name}: DEV PF=${d.PF?.toFixed(4)??'n/a'} n=${d.n} | VAL PF=${v.PF?.toFixed(4)??'n/a'} n=${v.n} | HOLDOUT PF=${h.PF?.toFixed(4)??'n/a'} n=${h.n} avgR=${h.avgR.toFixed(4)} survives=${c.holdoutSurvivesMeaningfulPositive}`);
  }
  for(const c of report.evaluation.dailyCaps){
    const h=c.byPart.holdout;
    console.log(`  CAP_${c.maxTradesPerDay}/day: HOLDOUT PF=${h.PF?.toFixed(4)??'n/a'} n=${h.n} avgR=${h.avgR.toFixed(4)} survives=${c.holdoutSurvivesMeaningfulPositive}`);
  }
  console.log(`Report -> ${out}`);
}

for(const tf of TIMEFRAMES)await run(tf);
