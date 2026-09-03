import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PRE = 10000;
const FRESH = 5000;
const CHECKPOINTS = [1, 2, 3, 5, 10];
const THRESHOLDS = [0.25, 0.5, 0.75, 1];
const PATH_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-early-adverse-excursion-fresh-holdout');

const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pct = (n, d) => d ? n / d : null;
const pf = rs => { const gp = rs.filter(x => x > 0).reduce((a, b) => a + b, 0); const gl = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0); return gl ? gp / gl : null; };
const key = c => `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;

function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  return { n: rs.length, avgR: mean(rs), PF: pf(rs), winRate: pct(rs.filter(r => r > 0).length, rs.length), totalR: rs.reduce((a, b) => a + b, 0) };
}

function early(candles, trade) {
  const i = Number(trade.entryIndex);
  const e = Number(trade.entry);
  const s = Number(trade.stopLoss);
  const d = String(trade.direction).toUpperCase();
  const risk = Math.abs(e - s);
  if (!Number.isInteger(i) || !Number.isFinite(e) || !Number.isFinite(s) || !risk || !['BUY', 'SELL'].includes(d)) return null;
  const path = [];
  for (let j = i + 1; j <= Math.min(candles.length - 1, i + Math.max(...CHECKPOINTS)); j++) {
    const c = candles[j];
    const adverse = (d === 'BUY' ? e - c.low : c.high - e) / risk;
    const favorable = (d === 'BUY' ? c.high - e : e - c.low) / risk;
    path.push({ bar: j - i, adverse, favorable });
  }
  const checkpoints = {};
  for (const h of CHECKPOINTS) {
    const q = path.filter(x => x.bar <= h);
    checkpoints[h] = { mae: Math.max(0, ...q.map(x => x.adverse)), mfe: Math.max(0, ...q.map(x => x.favorable)) };
  }
  return { entryIndex: i, entryTime: trade.entryTime, direction: d, entry: e, stopLoss: s, risk, rMultiple: Number(trade.rMultiple), checkpoints };
}

function compare(rows, h, t) {
  const within = rows.filter(r => r.checkpoints[h].mae <= t);
  const beyond = rows.filter(r => r.checkpoints[h].mae > t);
  return { checkpoint: h, thresholdR: t, within: { ...stats(within), share: pct(within.length, rows.length) }, beyond: { ...stats(beyond), share: pct(beyond.length, rows.length) }, deltaAvgR: within.length && beyond.length ? mean(within.map(r => r.rMultiple)) - mean(beyond.map(r => r.rMultiple)) : null };
}

async function run(tf) {
  const candles = (JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles ?? []);
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);
  const path = JSON.parse(await readFile(resolve(PATH_DIR, `${tf}.json`), 'utf8'));
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  const freshCut = new Date(candles[PRE].timestamp);
  const baseFresh = (base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) >= freshCut);
  const baseMap = new Map(baseFresh.map(t => [key(t), t]));
  const selected = (path.baselineSelected ?? []).filter(c => c.index >= PRE && c.triggerDelay === 1);
  const joined = [];
  for (const c of selected) {
    const t = baseMap.get(key(c));
    if (t) joined.push({ ...t, entryIndex: c.index });
  }
  const rows = joined.map(t => early(candles, t)).filter(Boolean);
  const report = {
    strategy: 'Strategy A', mode: 'DELAY1_EARLY_ADVERSE_EXCURSION_FRESH_HOLDOUT', timeframe: tf,
    scope: { totalCandles: candles.length, preHoldoutCandles: PRE, freshHoldoutCandles: FRESH, delayExactly: 1 },
    methodology: { outcomeSource: 'canonical baseline fresh-holdout trades', featureSource: 'post-entry OHLC excursion from actual fresh-holdout entry', checkpoints: CHECKPOINTS, thresholdsR: THRESHOLDS, sameBarOHLC: 'No intrabar ordering inference.', frozenBeforeHoldout: true, noOptimization: true, productionUntouched: true, diagnosticOnly: true },
    parity: { canonicalFreshTrades: baseFresh.length, delay1FreshJoined: joined.length, unmatchedDelay1: selected.length - joined.length },
    baselineDelay1: stats(rows),
    byCheckpoint: Object.fromEntries(CHECKPOINTS.map(h => [`MAE@${h}`, Object.fromEntries(THRESHOLDS.map(t => [`<=${t}R`, compare(rows, h, t)]))])),
    rows,
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`\n=== ${tf} DELAY1 EARLY ADVERSE EXCURSION — FRESH HOLDOUT ===`);
  console.log(`canonicalFresh=${baseFresh.length} delay1Joined=${rows.length} unmatched=${report.parity.unmatchedDelay1}`);
  console.log(`BASELINE DELAY1: n=${report.baselineDelay1.n} AvgR=${report.baselineDelay1.avgR?.toFixed(3)} PF=${report.baselineDelay1.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * report.baselineDelay1.winRate).toFixed(1)} TotalR=${report.baselineDelay1.totalR.toFixed(3)}`);
  for (const h of CHECKPOINTS) {
    for (const t of THRESHOLDS) {
      const s = compare(rows, h, t);
      console.log(`  MAE@${h} <=${t}R: n=${s.within.n} share=${(100 * (s.within.share ?? 0)).toFixed(1)} AvgR=${s.within.avgR?.toFixed(3)} PF=${s.within.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * s.within.winRate).toFixed(1)} | >${t}R: n=${s.beyond.n} AvgR=${s.beyond.avgR?.toFixed(3)} PF=${s.beyond.PF?.toFixed(3) ?? 'n/a'} WR=${(100 * s.beyond.winRate).toFixed(1)} Δ=${s.deltaAvgR?.toFixed(3)}`);
    }
  }
  console.log(`Report -> ${out}`);
}
for (const tf of ['1min', '5min']) await run(tf);
