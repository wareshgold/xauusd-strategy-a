import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-continuous-path-dynamics');
const HORIZONS = [5, 10, 20];
const CHECKPOINTS = [1, 2, 3];

const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { const x = a.filter(Number.isFinite).sort((a,b)=>a-b); if (!x.length) return null; const m=Math.floor(x.length/2); return x.length%2 ? x[m] : (x[m-1]+x[m])/2; };
const quantile = (a,q) => { const x=a.filter(Number.isFinite).sort((a,b)=>a-b); if(!x.length)return null; const p=(x.length-1)*q; const i=Math.floor(p),f=p-i; return x[i+1]===undefined?x[i]:x[i]+f*(x[i+1]-x[i]); };

function auditMetric(rows, key) {
  const vals = rows.flatMap(r => Object.values(r.metrics ?? {})).map(x => Number(x?.[key])).filter(Number.isFinite);
  if (!vals.length) return null;
  const uniq = [...new Set(vals.map(x => Number(x.toFixed(9))))];
  return { n: vals.length, unique: uniq.length, min: Math.min(...vals), p25: quantile(vals,.25), median: median(vals), p75: quantile(vals,.75), max: Math.max(...vals), mean: mean(vals), shareEqual1: vals.filter(x=>Math.abs(x-1)<1e-9).length/vals.length, shareInteger: vals.filter(x=>Number.isInteger(x)).length/vals.length };
}

function auditWithinCheckpoint(report, field) {
  const rows=[];
  for (const w of report.windows ?? []) for (const [name,m] of Object.entries(w.metrics ?? {})) {
    const cp=Number(name.match(/^T(\d+)_/)?.[1]);
    const h=Number(name.match(/_H(\d+)$/)?.[1]);
    if (!CHECKPOINTS.includes(cp) || !HORIZONS.includes(h)) continue;
    const n=Number(m.n)||0;
    if(n>0) rows.push({window:w.label,cp,h,n,metrics:m});
  }
  const grouped={};
  for(const r of rows){const k=`T${r.cp}_H${r.h}`;(grouped[k]??=[]).push(r);}
  return Object.fromEntries(Object.entries(grouped).map(([k,v])=>[k,{windows:v.map(x=>({window:x.window,n:x.n,metric:x.metrics[field]})),pooled:auditMetric(v,field)}]));
}

for (const tf of ['1min','5min']) {
  const report=JSON.parse(await readFile(resolve(REPORT_DIR,`${tf}.json`),'utf8'));
  console.log(`\n=== ${tf} TIMING METRIC AUDIT ===`);
  for(const field of ['timeToMae25','timeToMae50','timeToMae75','timeToMae1','timeToMfe05','timeToMfe1','timeToMfe2']) {
    const data=auditWithinCheckpoint(report,field);
    console.log(`\n${field}`);
    for(const [k,v] of Object.entries(data)) {
      const p=v.pooled;
      console.log(`  ${k}: pooled n=${p?.n??0} unique=${p?.unique??0} median=${p?.median??'n/a'} shareEqual1=${((p?.shareEqual1??0)*100).toFixed(1)}% integer=${((p?.shareInteger??0)*100).toFixed(1)}% range=[${p?.min??'n/a'},${p?.max??'n/a'}]`);
      console.log(`    windows: ${v.windows.map(x=>`${x.window}:${x.n}/${x.metric??'n/a'}`).join(' | ')}`);
    }
  }
  const example=report.windows?.[0]?.metrics?.T1_H5;
  console.log(`\nCHECKPOINT/HORIZON SEMANTICS T1_H5 keys=${Object.keys(example??{}).join(',')}`);
}
console.log('\nDiagnostic only: no strategy parameters, production rules, or fresh-holdout results are changed.');
