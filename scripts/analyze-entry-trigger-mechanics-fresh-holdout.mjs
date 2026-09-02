import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PATH_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-trigger-mechanics-fresh-holdout');
const TOTAL_CANDLES = 15000;
const FRESH_HOLDOUT_CANDLES = 5000;
const PRE_HOLDOUT_CANDLES = 10000;
const MIN_N = 10;
const QUALIFIED_TIMEFRAME = '5min';

function stats(rows) {
  const rs = rows.map(r => Number(r.r)).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0), losses = rs.filter(r => r < 0);
  const gp = wins.reduce((a, b) => a + b, 0), gl = -losses.reduce((a, b) => a + b, 0);
  let eq = 0, peak = 0, dd = 0, streak = 0, maxCL = 0;
  for (const r of rs) { eq += r; peak = Math.max(peak, eq); dd = Math.max(dd, peak - eq); streak = r < 0 ? streak + 1 : 0; maxCL = Math.max(maxCL, streak); }
  return { n: rs.length, wins: wins.length, losses: losses.length, winRate: rs.length ? wins.length / rs.length : 0, avgR: rs.length ? rs.reduce((a,b) => a+b, 0) / rs.length : 0, totalR: rs.reduce((a,b) => a+b, 0), PF: gl ? gp / gl : null, maxDD: dd, maxCL };
}
function key(c) { return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`; }
function candidate(name, predicate, rows, baseline) {
  const selected = rows.filter(predicate);
  const s = stats(selected);
  return { name, ...s, deltaAvgR: s.avgR - baseline.avgR, eligible: s.n >= MIN_N, pass: s.n >= MIN_N && s.avgR > 0 && s.PF !== null && s.PF >= 1 };
}

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles ?? [];
  if (candles.length < TOTAL_CANDLES) throw new Error(`${timeframe}: expected ${TOTAL_CANDLES} candles, found ${candles.length}`);
  if (timeframe !== QUALIFIED_TIMEFRAME) {
    console.log(`${timeframe}: NOT_ELIGIBLE (qualified timeframe=${QUALIFIED_TIMEFRAME})`);
    return;
  }
  const path = JSON.parse(await readFile(resolve(PATH_DIR, `${timeframe}.json`), 'utf8'));
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8'));
  const freshCut = candles[PRE_HOLDOUT_CANDLES]?.timestamp;
  if (!freshCut) throw new Error(`${timeframe}: missing fresh holdout cutoff`);
  const baseTrades = (base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) >= new Date(freshCut));
  const baseMap = new Map(baseTrades.map(t => [`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`, t]));
  const selected = (path.baselineSelected ?? []).filter(c => c.index >= PRE_HOLDOUT_CANDLES);
  const joined = [];
  for (const c of selected) { const t = baseMap.get(key(c)); if (t) joined.push({ ...c, r: Number(t.rMultiple), result: t.result, entryTime: t.entryTime }); }
  const baseline = stats(joined);
  const hypotheses = [
    candidate('triggerDelay <= 1', r => r.triggerDelay <= 1, joined, baseline),
    candidate('stopToImpulse 25-50%', r => r.stopToImpulse >= 0.25 && r.stopToImpulse < 0.50, joined, baseline),
    candidate('COMBINED: triggerDelay <= 1 AND stopToImpulse 25-50%', r => r.triggerDelay <= 1 && r.stopToImpulse >= 0.25 && r.stopToImpulse < 0.50, joined, baseline),
  ];
  const report = { strategy: 'Strategy A', mode: 'ENTRY_TRIGGER_MECHANICS_FRESH_HOLDOUT', timeframe, scope: { totalCandles: candles.length, preHoldoutCandles: PRE_HOLDOUT_CANDLES, freshHoldoutCandles: FRESH_HOLDOUT_CANDLES }, methodology: { outcomeSource: 'canonical baseline backtest; no outcome recomputation', featureSource: 'direct baseline-path forensic', selection: 'two hypotheses frozen after DEV/VAL PASS; no threshold optimization on holdout', minN: MIN_N, productionUntouched: true }, parity: { baselineFreshHoldout: baseTrades.length, joinedForensics: joined.length, baselineMissing: baseTrades.filter(t => !joined.some(r => key(r) === `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`)).length }, baseline, hypotheses, decision: 'Fresh holdout confirmation only. No hypothesis is promoted automatically; any confirmed hypothesis requires separate robustness/stability validation before production consideration.' };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: baseline n=${baseline.n} avgR=${baseline.avgR.toFixed(4)} PF=${baseline.PF?.toFixed(4) ?? 'n/a'} joined=${joined.length}`);
  for (const h of hypotheses) console.log(`  ${h.name}: n=${h.n} avgR=${h.avgR.toFixed(4)} PF=${h.PF?.toFixed(3) ?? 'n/a'} winRate=${(h.winRate * 100).toFixed(2)}% totalR=${h.totalR.toFixed(4)} maxDD=${h.maxDD.toFixed(4)}R maxCL=${h.maxCL} deltaAvgR=${h.deltaAvgR.toFixed(4)} pass=${h.pass}`);
  console.log(`Report -> ${out}`);
}
for (const tf of ['1min', '5min']) await run(tf);
