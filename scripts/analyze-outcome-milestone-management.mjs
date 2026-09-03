import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-outcome-milestone-management');
const TOTAL = 15000;
const PRE = 10000;
const DEV = 6000;
const MILESTONES = [0.5, 0.75, 1];
const TARGET_R = 2;
const HORIZON = 10000;

function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a,b) => a+b, 0), gl = -losses.reduce((a,b) => a+b, 0);
  return { n: rs.length, wins: wins.length, losses: losses.length, winRate: rs.length ? wins.length/rs.length : 0, avgR: rs.length ? rs.reduce((a,b)=>a+b,0)/rs.length : 0, PF: gl ? gp/gl : null, totalR: rs.reduce((a,b)=>a+b,0) };
}

function replay(candles, trade, milestone) {
  const entryIndex = Number(trade.entryIndex), entry = Number(trade.entry);
  const baseRisk = Math.abs(entry - Number(trade.stopLoss));
  if (!Number.isInteger(entryIndex) || !(baseRisk > 0)) return null;
  const target = trade.direction === 'BUY' ? entry + TARGET_R * baseRisk : entry - TARGET_R * baseRisk;
  const initialStop = trade.direction === 'BUY' ? entry - baseRisk : entry + baseRisk;
  let armed = false, stop = initialStop, armIndex = null;
  for (let i = entryIndex + 1; i < Math.min(candles.length, entryIndex + HORIZON + 1); i++) {
    const c = candles[i];
    const fav = trade.direction === 'BUY' ? (c.high-entry)/baseRisk : (entry-c.low)/baseRisk;
    const hitMilestone = fav >= milestone;
    if (!armed && hitMilestone) { armed = true; armIndex = i; stop = entry; }
    const hitTarget = trade.direction === 'BUY' ? c.high >= target : c.low <= target;
    const hitStop = trade.direction === 'BUY' ? c.low <= stop : c.high >= stop;
    if (hitTarget && hitStop) return { result:'AMBIGUOUS', r:null, armIndex, exitIndex:i };
    if (hitStop) return { result: armed ? 'BREAKEVEN' : 'STOP', r: armed ? 0 : -1, armIndex, exitIndex:i };
    if (hitTarget) return { result:'TP2', r:TARGET_R, armIndex, exitIndex:i };
  }
  return { result:'OPEN', r:null, armIndex, exitIndex:null };
}

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles;
  const baseline = JSON.parse(await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  const trades = (baseline.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff);
  const rows = trades.map(trade => ({ trade })).filter(x => Number.isInteger(Number(x.trade.entryIndex)));
  const dev = rows.filter(x => Number(x.trade.entryIndex) < DEV);
  const val = rows.filter(x => Number(x.trade.entryIndex) >= DEV && Number(x.trade.entryIndex) < PRE);
  const report = { strategy:'Strategy A', mode:'OUTCOME_MILESTONE_BE_MANAGEMENT_DIAGNOSTIC_PREHOLDOUT', timeframe, scope:{ totalCandles:TOTAL, preHoldoutCandles:PRE, devCandles:DEV, valCandles:PRE-DEV, freshHoldoutCandles:TOTAL-PRE, freshHoldoutExcluded:true }, methodology:{ purpose:'Diagnostic only: test whether moving stop to breakeven after a favorable milestone changes canonical 2R outcome.', milestones:MILESTONES, targetR:TARGET_R, initialStopR:1, sameCandle:'If target and active stop are both touched on the same candle, classify AMBIGUOUS; no intrabar order is inferred.', noOptimization:true, noProductionChange:true } };
  report.scenarios = {};
  for (const m of MILESTONES) {
    const summarize = set => {
      const outcomes = set.map(x => replay(candles, x.trade, m)).filter(Boolean);
      const resolved = outcomes.filter(x => Number.isFinite(x.r));
      return { total:outcomes.length, resolved:resolved.length, ambiguous:outcomes.filter(x=>x.result==='AMBIGUOUS').length, open:outcomes.filter(x=>x.result==='OPEN').length, armed:outcomes.filter(x=>x.armIndex != null).length, outcomes:{TP2:outcomes.filter(x=>x.result==='TP2').length,BREAKEVEN:outcomes.filter(x=>x.result==='BREAKEVEN').length,STOP:outcomes.filter(x=>x.result==='STOP').length}, metrics:metrics(resolved) };
    };
    report.scenarios[String(m)] = { DEV:summarize(dev), VAL:summarize(val) };
  }
  await mkdir(OUT_DIR,{recursive:true});
  const out=resolve(OUT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: joined=${rows.length} DEV=${dev.length} VAL=${val.length}`);
  for (const m of MILESTONES) { const d=report.scenarios[String(m)].DEV,v=report.scenarios[String(m)].VAL; console.log(` milestone=+${m}R: DEV TP2=${d.outcomes.TP2} BE=${d.outcomes.BREAKEVEN} STOP=${d.outcomes.STOP} amb=${d.ambiguous} avgR=${d.metrics.avgR.toFixed(4)} PF=${d.metrics.PF?.toFixed(3)??'n/a'} | VAL TP2=${v.outcomes.TP2} BE=${v.outcomes.BREAKEVEN} STOP=${v.outcomes.STOP} amb=${v.ambiguous} avgR=${v.metrics.avgR.toFixed(4)} PF=${v.metrics.PF?.toFixed(3)??'n/a'}`); }
  console.log(`Report -> ${out}`);
}

await Promise.all(['1min','5min'].map(run));
