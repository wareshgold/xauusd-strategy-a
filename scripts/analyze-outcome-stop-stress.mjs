import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-outcome-stop-stress');
const TOTAL = 15000;
const PRE = 10000;
const DEV = 6000;
const HORIZON = 20;
const THRESHOLDS = [0.25, 0.5, 1];
const STOP_MULTIPLIERS = [0.5, 0.75, 1, 1.25, 1.5, 2];

function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return { n: rs.length, wins: wins.length, losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    avgR: rs.length ? rs.reduce((a, b) => a + b, 0) / rs.length : 0,
    totalR: rs.reduce((a, b) => a + b, 0), PF: gl ? gp / gl : null };
}

function quantiles(values) {
  const v = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!v.length) return { n: 0, p25: null, median: null, p75: null, mean: null };
  const at = p => { const i = (v.length - 1) * p; const b = Math.floor(i), f = i - b; return v[b] + (v[b + 1] ?? v[b]) * f; };
  return { n: v.length, p25: at(.25), median: at(.5), p75: at(.75), mean: v.reduce((a,b) => a+b, 0) / v.length };
}

function signedMove(direction, price, entry) {
  return direction === 'BUY' ? price - entry : entry - price;
}

function path(candles, trade) {
  const entryIndex = Number(trade.entryIndex), entry = Number(trade.entry);
  const stop = Number(trade.stopLoss), risk = Math.abs(entry - stop);
  if (!Number.isInteger(entryIndex) || !(risk > 0)) return null;
  const end = Math.min(candles.length - 1, entryIndex + HORIZON);
  const out = { first: {}, timeToFav: {}, timeToAdv: {}, mfe: 0, mae: 0 };
  for (let i = entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const fav = signedMove(trade.direction, trade.direction === 'BUY' ? c.high : c.low, entry) / risk;
    const adv = signedMove(trade.direction, trade.direction === 'BUY' ? c.low : c.high, entry) / risk;
    out.mfe = Math.max(out.mfe, fav); out.mae = Math.max(out.mae, adv);
    for (const t of THRESHOLDS) {
      const k = String(t);
      if (out.timeToFav[k] == null && fav >= t) out.timeToFav[k] = i - entryIndex;
      if (out.timeToAdv[k] == null && adv >= t) out.timeToAdv[k] = i - entryIndex;
    }
  }
  for (const t of THRESHOLDS) {
    const k = String(t), f = out.timeToFav[k], a = out.timeToAdv[k];
    out.first[k] = f != null && a != null ? (f < a ? 'FAVORABLE_FIRST' : a < f ? 'ADVERSE_FIRST' : 'SAME_BAR') : f != null ? 'FAVORABLE_ONLY' : a != null ? 'ADVERSE_ONLY' : 'NEITHER';
  }
  return out;
}

function thresholdSummary(rows) {
  const out = {};
  for (const t of THRESHOLDS) {
    const k = String(t);
    const groups = Object.fromEntries(['FAVORABLE_FIRST','ADVERSE_FIRST','SAME_BAR','FAVORABLE_ONLY','ADVERSE_ONLY','NEITHER'].map(x => [x, rows.filter(r => r.path?.first[k] === x)]));
    out[k] = { thresholdR: t, total: rows.length,
      groups: Object.fromEntries(Object.entries(groups).map(([name, rs]) => [name, { rate: rows.length ? rs.length / rows.length : 0, metrics: metrics(rs.map(r => r.outcome)) }])),
      timeToFavorable: quantiles(rows.map(r => r.path?.timeToFav[k])),
      timeToAdverse: quantiles(rows.map(r => r.path?.timeToAdv[k])),
    };
  }
  return out;
}

function stressTrade(candles, trade, multiplier) {
  const entryIndex = Number(trade.entryIndex), entry = Number(trade.entry);
  const baseRisk = Math.abs(entry - Number(trade.stopLoss));
  const target = Number(trade.takeProfit1 ?? trade.tp1 ?? trade.TP1);
  if (!Number.isInteger(entryIndex) || !(baseRisk > 0) || !Number.isFinite(target)) return null;
  const stopDistance = baseRisk * multiplier;
  const stop = trade.direction === 'BUY' ? entry - stopDistance : entry + stopDistance;
  const targetR = Math.abs(target - entry) / stopDistance;
  const end = candles.length - 1;
  let result = 'OPEN', exitIndex = null, r = null;
  for (let i = entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const hitTarget = trade.direction === 'BUY' ? c.high >= target : c.low <= target;
    const hitStop = trade.direction === 'BUY' ? c.low <= stop : c.high >= stop;
    if (hitTarget && hitStop) { result = 'AMBIGUOUS'; exitIndex = i; break; }
    if (hitStop) { result = 'STOP'; exitIndex = i; r = -multiplier; break; }
    if (hitTarget) { result = 'TP1'; exitIndex = i; r = targetR; break; }
  }
  return { result, exitIndex, r, targetR };
}

function stressSummary(candles, trades, multiplier) {
  const rows = trades.map(t => stressTrade(candles, t, multiplier)).filter(Boolean);
  const resolved = rows.filter(x => x.result === 'TP1' || x.result === 'STOP');
  const same = rows.filter(x => x.result === 'AMBIGUOUS');
  const rs = resolved.filter(x => Number.isFinite(x.r)).map(x => ({ r: x.r }));
  return { multiplier, total: rows.length, resolved: resolved.length, ambiguous: same.length,
    ambiguousRate: rows.length ? same.length / rows.length : 0,
    open: rows.filter(x => x.result === 'OPEN').length,
    outcomes: { TP1: rows.filter(x => x.result === 'TP1').length, STOP: rows.filter(x => x.result === 'STOP').length },
    metricsResolved: metrics(rs) };
}

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles;
  if (candles.length < TOTAL) throw new Error(`${timeframe}: expected ${TOTAL}+ candles, got ${candles.length}`);
  const baseline = JSON.parse(await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  const trades = (baseline.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff);
  const rows = trades.map(t => ({ trade: t, path: path(candles, t), outcome: { r: Number(t.rMultiple) } })).filter(x => x.path);
  const dev = rows.filter(x => Number(x.trade.entryIndex) < DEV);
  const val = rows.filter(x => Number(x.trade.entryIndex) >= DEV && Number(x.trade.entryIndex) < PRE);
  const stress = set => Object.fromEntries(STOP_MULTIPLIERS.map(m => [String(m), stressSummary(candles, set.map(x => x.trade), m)]));
  const report = {
    strategy: 'Strategy A', mode: 'OUTCOME_THRESHOLD_AND_DIAGNOSTIC_STOP_STRESS_PREHOLDOUT', timeframe,
    scope: { totalCandles: TOTAL, preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE-DEV, freshHoldoutCandles: TOTAL-PRE, freshHoldoutExcluded: true },
    methodology: { purpose: 'Separate path ordering from stop-distance sensitivity using canonical entries.', horizon: HORIZON, thresholds: THRESHOLDS.map(t => `+/-${t}R`), stopMultipliers: STOP_MULTIPLIERS, stressTarget: 'Canonical TP1 is retained; hypothetical stop distance is multiplier x canonical entry-to-stop distance.', sameCandle: 'If hypothetical stop and TP1 are both touched in one candle, classify AMBIGUOUS; no intrabar order is inferred.', noOptimization: true, noProductionChange: true },
    counts: { joined: rows.length, DEV: dev.length, VAL: val.length },
    baseline: { DEV: metrics(dev.map(x => x.outcome)), VAL: metrics(val.map(x => x.outcome)) },
    thresholdOrdering: { DEV: thresholdSummary(dev), VAL: thresholdSummary(val) },
    stopStress: { DEV: stress(dev), VAL: stress(val) },
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`); await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: joined=${rows.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${report.baseline.DEV.avgR.toFixed(4)} baselineVAL=${report.baseline.VAL.avgR.toFixed(4)}`);
  for (const t of THRESHOLDS) {
    const k = String(t), d = report.thresholdOrdering.DEV[k], v = report.thresholdOrdering.VAL[k];
    console.log(` +/-${t}R: DEV F=${(d.groups.FAVORABLE_FIRST.rate*100).toFixed(1)}% A=${(d.groups.ADVERSE_FIRST.rate*100).toFixed(1)}% S=${(d.groups.SAME_BAR.rate*100).toFixed(1)}% | VAL F=${(v.groups.FAVORABLE_FIRST.rate*100).toFixed(1)}% A=${(v.groups.ADVERSE_FIRST.rate*100).toFixed(1)}% S=${(v.groups.SAME_BAR.rate*100).toFixed(1)}%`);
  }
  for (const m of STOP_MULTIPLIERS) {
    const d = report.stopStress.DEV[String(m)], v = report.stopStress.VAL[String(m)];
    console.log(` stop=${m}x: DEV resolved=${d.resolved}/${d.total} amb=${(d.ambiguousRate*100).toFixed(1)}% avgR=${d.metricsResolved.avgR.toFixed(4)} PF=${d.metricsResolved.PF?.toFixed(3) ?? 'n/a'} | VAL resolved=${v.resolved}/${v.total} amb=${(v.ambiguousRate*100).toFixed(1)}% avgR=${v.metricsResolved.avgR.toFixed(4)} PF=${v.metricsResolved.PF?.toFixed(3) ?? 'n/a'}`);
  }
  console.log(`Report -> ${out}`);
}

await Promise.all(['1min','5min'].map(run));
