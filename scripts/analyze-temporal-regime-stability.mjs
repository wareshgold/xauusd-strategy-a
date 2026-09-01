import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-temporal-regime-stability');
const TIMEFRAMES = ['1min', '5min'];
const WINDOW_COUNT = 8;
const MIN_WINDOW_N = 20;

function summarize(rows) {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return { n: rs.length, winRate: rs.length ? wins.length / rs.length : 0, PF: gl ? gp / gl : (gp ? null : 0), avgR: rs.length ? rs.reduce((a,b)=>a+b,0)/rs.length : 0, totalR: rs.reduce((a,b)=>a+b,0) };
}

function splitChronological(rows) {
  const sorted = [...rows].sort((a,b)=>new Date(a.entryTime)-new Date(b.entryTime));
  const base = Math.floor(sorted.length / WINDOW_COUNT);
  return Array.from({length: WINDOW_COUNT}, (_,i)=>sorted.slice(i*base, i===WINDOW_COUNT-1 ? sorted.length : (i+1)*base));
}

function windowStats(rows) {
  return splitChronological(rows).map((w,i)=>({ window:i+1, from:w[0]?.entryTime??null, to:w.at(-1)?.entryTime??null, ...summarize(w) }));
}

function stability(windows) {
  const eligible = windows.filter(w=>w.n>=MIN_WINDOW_N);
  const positive = eligible.filter(w=>w.PF != null && w.PF>=1 && w.avgR>0);
  const avgWindowR = eligible.length ? eligible.reduce((s,w)=>s+w.avgR,0)/eligible.length : 0;
  const minAvgR = eligible.length ? Math.min(...eligible.map(w=>w.avgR)) : null;
  return { eligibleWindows:eligible.length, positiveWindows:positive.length, positiveWindowRate:eligible.length ? positive.length/eligible.length : 0, avgWindowR, minAvgR, finalWindowPositive:Boolean(eligible.length && eligible.at(-1).PF != null && eligible.at(-1).PF>=1 && eligible.at(-1).avgR>0), allEligibleWindowsPositive:Boolean(eligible.length && positive.length===eligible.length) };
}

function byYearMonth(rows) {
  const groups = new Map();
  for (const r of rows) {
    const d = new Date(r.entryTime);
    const key = `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(r);
  }
  return Object.fromEntries([...groups.entries()].map(([k,v])=>[k,summarize(v)]));
}

async function run(timeframe) {
  const source = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`),'utf8'));
  const rows=(source.trades??[]).filter(t=>Number.isFinite(Number(t.rMultiple)) && t.result!=='AMBIGUOUS').map(t=>({...t,rMultiple:Number(t.rMultiple)})).sort((a,b)=>new Date(a.entryTime)-new Date(b.entryTime));
  const windows=windowStats(rows);
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_TEMPORAL_REGIME_STABILITY_V1',timeframe,scope:'Baseline resolved trades only; chronological stability and calendar-regime diagnostics; no production rule changes.',methodology:{windows:WINDOW_COUNT,ordering:'chronological entryTime',minimumWindowN:MIN_WINDOW_N,windowGate:'diagnostic only: PF >= 1 and avgR > 0',selection:'No window, date range, or regime is optimized or promoted from this report.',warning:'Calendar buckets are descriptive diagnostics, not candidate production filters. A regime is not considered validated without a separately defined untouched holdout.',overall:summarize(rows),rolling:windows,stability:stability(windows),byYearMonth:byYearMonth(rows),nextStep:'If temporal instability is confirmed, define one pre-registered regime hypothesis from market-state variables available before entry, then test it on a fresh untouched holdout. If no stable regime emerges, revisit the baseline setup definition rather than adding filters.'};
  await mkdir(OUT_DIR,{recursive:true});
  const out=resolve(OUT_DIR,`${timeframe}.json`);
  await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: baseline=${rows.length} positiveWindows=${report.stability.positiveWindows}/${report.stability.eligibleWindows} finalPositive=${report.stability.finalWindowPositive} avgWindowR=${report.stability.avgWindowR.toFixed(4)} minWindowR=${report.stability.minAvgR?.toFixed(4)??'n/a'}`);
  for(const w of windows) console.log(`  W${w.window}: ${w.from??'n/a'} -> ${w.to??'n/a'} n=${w.n} PF=${w.PF?.toFixed(4)??'n/a'} avgR=${w.avgR.toFixed(4)} totalR=${w.totalR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}

for(const timeframe of TIMEFRAMES) await run(timeframe);
