import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-outcome-survival-matrix');
const TOTAL = 15000;
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [1, 2, 3, 5, 10, 20];
const THRESHOLDS = [0.25, 0.5, 0.75, 1, 1.5, 2, 3];

function metrics(rs) {
  const values = rs.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = values.filter(x => x > 0), losses = values.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return { n: values.length, winRate: values.length ? wins.length / values.length : 0, avgR: values.length ? values.reduce((a,b) => a+b, 0) / values.length : 0, PF: gl ? gp / gl : null };
}

function quantile(values, p) {
  const v = values.filter(Number.isFinite).sort((a,b) => a-b);
  if (!v.length) return null;
  const i = (v.length - 1) * p, b = Math.floor(i), f = i - b;
  return v[b] + (v[b + 1] ?? v[b]) * f;
}

function path(candles, trade) {
  const entryIndex = Number(trade.entryIndex), entry = Number(trade.entry);
  const risk = Math.abs(entry - Number(trade.stopLoss));
  if (!Number.isInteger(entryIndex) || !(risk > 0)) return null;
  const out = {};
  for (const h of HORIZONS) {
    const end = Math.min(candles.length - 1, entryIndex + h);
    const reached = { fav: {}, adv: {} };
    for (let i = entryIndex + 1; i <= end; i++) {
      const c = candles[i];
      const fav = (trade.direction === 'BUY' ? c.high - entry : entry - c.low) / risk;
      const adv = (trade.direction === 'BUY' ? entry - c.low : c.high - entry) / risk;
      for (const t of THRESHOLDS) {
        const k = String(t);
        if (reached.fav[k] == null && fav >= t) reached.fav[k] = i - entryIndex;
        if (reached.adv[k] == null && adv >= t) reached.adv[k] = i - entryIndex;
      }
    }
    out[h] = { fav: reached.fav, adv: reached.adv };
  }
  return out;
}

function survival(rows, horizon) {
  const out = {};
  for (const t of THRESHOLDS) {
    const k = String(t);
    const reachedFav = rows.filter(r => r.path[horizon].fav[k] != null);
    const reachedAdv = rows.filter(r => r.path[horizon].adv[k] != null);
    const favFirst = rows.filter(r => {
      const f = r.path[horizon].fav[k], a = r.path[horizon].adv[k];
      return f != null && (a == null || f < a);
    });
    const advFirst = rows.filter(r => {
      const f = r.path[horizon].fav[k], a = r.path[horizon].adv[k];
      return a != null && (f == null || a < f);
    });
    const same = rows.filter(r => {
      const f = r.path[horizon].fav[k], a = r.path[horizon].adv[k];
      return f != null && a != null && f === a;
    });
    out[k] = {
      thresholdR: t,
      favorableReachRate: rows.length ? reachedFav.length / rows.length : 0,
      adverseReachRate: rows.length ? reachedAdv.length / rows.length : 0,
      favorableFirstRate: rows.length ? favFirst.length / rows.length : 0,
      adverseFirstRate: rows.length ? advFirst.length / rows.length : 0,
      sameBarRate: rows.length ? same.length / rows.length : 0,
      timeToFavorable: { median: quantile(reachedFav.map(r => r.path[horizon].fav[k]), .5), p75: quantile(reachedFav.map(r => r.path[horizon].fav[k]), .75) },
      timeToAdverse: { median: quantile(reachedAdv.map(r => r.path[horizon].adv[k]), .5), p75: quantile(reachedAdv.map(r => r.path[horizon].adv[k]), .75) },
      outcomeIfFavorableFirst: metrics(favFirst.map(r => r.outcome)),
      outcomeIfAdverseFirst: metrics(advFirst.map(r => r.outcome)),
    };
  }
  return out;
}

function transition(rows, horizon) {
  const out = {};
  for (let i = 0; i < THRESHOLDS.length - 1; i++) {
    const from = THRESHOLDS[i], to = THRESHOLDS[i + 1];
    const fk = String(from), tk = String(to);
    const survivors = rows.filter(r => r.path[horizon].fav[fk] != null);
    const next = survivors.filter(r => r.path[horizon].fav[tk] != null && r.path[horizon].fav[tk] >= r.path[horizon].fav[fk]);
    out[`${from}->${to}`] = {
      baseN: survivors.length,
      transitionN: next.length,
      transitionRate: survivors.length ? next.length / survivors.length : 0,
      outcomeAfterFrom: metrics(survivors.map(r => r.outcome)),
      outcomeAfterTo: metrics(next.map(r => r.outcome)),
    };
  }
  return out;
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
  const report = {
    strategy: 'Strategy A', mode: 'OUTCOME_SURVIVAL_MATRIX_PREHOLDOUT', timeframe,
    scope: { totalCandles: TOTAL, preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE-DEV, freshHoldoutCandles: TOTAL-PRE, freshHoldoutExcluded: true },
    methodology: { purpose: 'Measure favorable/adverse threshold reach, ordering, time-to-threshold, and transitions between favorable thresholds using canonical entries.', horizons: HORIZONS, thresholds: THRESHOLDS.map(t => `+/-${t}R`), adverseDefinition: 'BUY entry-low; SELL high-entry.', sameBar: 'Same candle means threshold first-hit times are equal; intrabar order is not inferred.', canonicalOutcome: true, noOptimization: true, noProductionChange: true },
    counts: { joined: rows.length, DEV: dev.length, VAL: val.length },
    baseline: { DEV: metrics(dev.map(x => x.outcome)), VAL: metrics(val.map(x => x.outcome)) },
    survival: {},
    transitions: {},
  };
  for (const h of HORIZONS) {
    report.survival[h] = { DEV: survival(dev, h), VAL: survival(val, h) };
    report.transitions[h] = { DEV: transition(dev, h), VAL: transition(val, h) };
  }
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: joined=${rows.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${report.baseline.DEV.avgR.toFixed(4)} baselineVAL=${report.baseline.VAL.avgR.toFixed(4)}`);
  for (const h of HORIZONS) {
    const d = report.survival[h].DEV, v = report.survival[h].VAL;
    const f1d = d['1'].favorableReachRate, f1v = v['1'].favorableReachRate;
    const f2d = d['2'].favorableReachRate, f2v = v['2'].favorableReachRate;
    const a1d = d['1'].adverseReachRate, a1v = v['1'].adverseReachRate;
    console.log(` h${h}: +1R reach DEV=${(f1d*100).toFixed(1)}% VAL=${(f1v*100).toFixed(1)}% | +2R DEV=${(f2d*100).toFixed(1)}% VAL=${(f2v*100).toFixed(1)}% | -1R DEV=${(a1d*100).toFixed(1)}% VAL=${(a1v*100).toFixed(1)}%`);
  }
  const h = 20;
  for (const t of THRESHOLDS) {
    const d = report.survival[h].DEV[String(t)], v = report.survival[h].VAL[String(t)];
    console.log(` h20 +/-${t}R: DEV reach F=${(d.favorableReachRate*100).toFixed(1)}% A=${(d.adverseReachRate*100).toFixed(1)}% Ffirst=${(d.favorableFirstRate*100).toFixed(1)}% Afirst=${(d.adverseFirstRate*100).toFixed(1)}% | VAL reach F=${(v.favorableReachRate*100).toFixed(1)}% A=${(v.adverseReachRate*100).toFixed(1)}% Ffirst=${(v.favorableFirstRate*100).toFixed(1)}% Afirst=${(v.adverseFirstRate*100).toFixed(1)}%`);
  }
  console.log(`Report -> ${out}`);
}

await Promise.all(['1min','5min'].map(run));
