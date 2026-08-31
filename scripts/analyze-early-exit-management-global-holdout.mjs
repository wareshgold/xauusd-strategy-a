import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-early-exit-management-global-holdout');
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [1, 2, 3, 5, 8, 12, 20];
const MAE_THRESHOLDS = [0.25, 0.5, 0.75, 1.0];
const MFE_THRESHOLDS = [0.25, 0.5, 0.75, 1.0];
const MIN_N = 10;

function finite(v) { return Number.isFinite(Number(v)); }
function pick(r, keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    PF: gl ? gp / gl : (gp ? null : 0),
    avgR: rs.length ? rs.reduce((a, b) => a + b, 0) / rs.length : 0,
    totalR: rs.reduce((a, b) => a + b, 0),
  };
}
function split(rows) {
  const a = [...rows].sort((x, y) => new Date(x.entryTime) - new Date(y.entryTime));
  const c = Math.floor(a.length / 3);
  return { dev: a.slice(0, c), validation: a.slice(c, 2 * c), holdout: a.slice(2 * c) };
}
function exitIndexForTrade(trade, candles) {
  const entryIndex = Number(trade.entryIndex);
  const entry = pick(trade, ['entry', 'entryPrice', 'fillPrice', 'price']);
  const stop = pick(trade, ['stopLoss', 'stop', 'sl']);
  const tp1 = pick(trade, ['tp1', 'takeProfit', 'target']);
  const tp2 = pick(trade, ['tp2']);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(stop) || !finite(tp1)) return null;
  for (let i = entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = trade.direction === 'BUY' ? c.low <= stop : c.high >= stop;
    const tp2Hit = tp2 !== null && (trade.direction === 'BUY' ? c.high >= tp2 : c.low <= tp2);
    const tp1Hit = trade.direction === 'BUY' ? c.high >= tp1 : c.low <= tp1;
    if (sl || tp2Hit || tp1Hit) return i;
  }
  return null;
}
function excursionAt(trade, candles, horizon) {
  const entryIndex = Number(trade.entryIndex);
  const entry = pick(trade, ['entry', 'entryPrice', 'fillPrice', 'price']);
  const risk = pick(trade, ['riskDistance', 'risk', 'stopDistance']);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(risk) || risk <= 0) return null;
  const end = Math.min(candles.length - 1, entryIndex + horizon);
  if (end <= entryIndex) return null;
  const buy = String(trade.direction).toUpperCase() === 'BUY';
  let mae = 0, mfe = 0;
  for (let i = entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const lo = Number(c.low), hi = Number(c.high);
    if (!Number.isFinite(lo) || !Number.isFinite(hi)) continue;
    mae = Math.max(mae, buy ? entry - lo : hi - entry);
    mfe = Math.max(mfe, buy ? hi - entry : entry - lo);
  }
  return { maeR: Math.max(0, mae) / risk, mfeR: Math.max(0, mfe) / risk, endIndex: end };
}
function candidateRows(rows, horizon, maeThreshold, mfeThreshold, candles) {
  return rows.map(r => {
    const e = r.early[horizon];
    if (!e) return null;
    const originalExit = r.exitIndex;
    if (!Number.isInteger(originalExit)) return null;
    if (originalExit <= e.endIndex) return { ...r, rMultiple: Number(r.rMultiple), managementAction: 'original-exit-before-or-at-horizon' };
    if (!(e.maeR >= maeThreshold && e.mfeR < mfeThreshold)) return { ...r, rMultiple: Number(r.rMultiple), managementAction: 'original-exit' };
    const c = candles[e.endIndex];
    const close = Number(c?.close);
    const entry = pick(r, ['entry', 'entryPrice', 'fillPrice', 'price']);
    const risk = pick(r, ['riskDistance', 'risk', 'stopDistance']);
    if (!finite(close) || !finite(entry) || !finite(risk) || risk <= 0) return null;
    const buy = String(r.direction).toUpperCase() === 'BUY';
    const rMultiple = (buy ? close - entry : entry - close) / risk;
    return { ...r, rMultiple, managementAction: 'early-exit-at-close', managedExitIndex: e.endIndex };
  }).filter(Boolean);
}
async function run(tf) {
  const [raw, candleRaw] = await Promise.all([
    readFile(resolve(ROOT, `data/reports/strategy-a-entry-geometry-forensics/${tf}.json`), 'utf8'),
    readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'),
  ]);
  const source = JSON.parse(raw);
  const candleData = JSON.parse(candleRaw);
  const candles = candleData.candles ?? candleData;
  const base = (source.tradeRows || []).filter(r => Number.isFinite(r.rMultiple));
  const rows = base.map(r => {
    const exitIndex = exitIndexForTrade(r, candles);
    const early = Object.fromEntries(HORIZONS.map(h => [h, excursionAt(r, candles, h)]));
    return { ...r, exitIndex, early };
  }).filter(r => Number.isInteger(r.exitIndex));
  const s = split(rows);
  const baseline = { dev: stats(s.dev), validation: stats(s.validation), holdout: stats(s.holdout), all: stats(rows) };
  const tests = [];
  for (const h of HORIZONS) for (const mae of MAE_THRESHOLDS) for (const mfe of MFE_THRESHOLDS) {
    const managed = candidateRows(rows, h, mae, mfe, candles);
    const m = split(managed);
    const dev = stats(m.dev), validation = stats(m.validation), holdout = stats(m.holdout);
    const triggered = managed.filter(r => r.managementAction === 'early-exit-at-close');
    tests.push({
      horizon: h, maeThresholdR: mae, mfeThresholdR: mfe,
      triggerCount: triggered.length,
      triggerRate: rows.length ? triggered.length / rows.length : 0,
      dev, validation, holdout,
      passesDev: dev.n >= MIN_N && dev.PF !== null && dev.PF >= 1 && dev.avgR > 0,
      passesValidation: validation.n >= MIN_N && validation.PF !== null && validation.PF >= 1 && validation.avgR > 0,
    });
  }
  const candidates = tests.filter(x => x.passesDev && x.passesValidation && x.holdout.n >= MIN_N)
    .sort((a, b) => b.validation.avgR - a.validation.avgR || b.validation.PF - a.validation.PF || b.validation.n - a.validation.n);
  const robust = candidates.filter(x => x.holdout.PF !== null && x.holdout.PF >= 1 && x.holdout.avgR > 0)
    .sort((a, b) => b.holdout.avgR - a.holdout.avgR || b.holdout.PF - a.holdout.PF);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_EARLY_EXIT_MANAGEMENT_GLOBAL_HOLDOUT_V1',
    timeframe: tf,
    scope: 'Prospective exit-management simulation. Entry rules are unchanged. An early exit is allowed only after entry and only when the specified early MAE/MFE condition is observed; otherwise the original backtest exit is retained.',
    methodology: {
      split: 'One shared chronological DEV/VALIDATION/HOLDOUT partition; boundaries are fixed for every candidate.',
      search: '7 horizons x 4 MAE thresholds x 4 MFE thresholds = 112 fixed hypotheses.',
      trigger: 'At the close of horizon H, exit if early MAE >= threshold and early MFE < threshold. If the original SL/TP exit occurred before or on H, the original exit is retained.',
      execution: 'Early-exit price is the close of the H-th post-entry candle. This is intentionally conservative and deterministic.',
      selectionGate: `DEV and VALIDATION each n >= ${MIN_N}, PF >= 1, avgR > 0. Candidates are ranked on VALIDATION only. HOLDOUT is untouched until final evaluation.`,
      multipleComparisons: 'The fixed grid is exploratory; any positive holdout result is evidence for a follow-up pre-specified robustness test, not a production rule.',
      noEntryLookahead: 'The condition uses only candles available after the trade entry.',
    },
    globalCounts: { all: rows.length, dev: s.dev.length, validation: s.validation.length, holdout: s.holdout.length },
    baseline,
    tests: tests.length,
    devValidationCandidates: candidates.length,
    robustHoldoutCandidates: robust.length,
    topCandidates: candidates.slice(0, 20),
    robustHoldout: robust.slice(0, 20),
  };
  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: trades=${rows.length} tests=${tests.length} devValidationCandidates=${candidates.length} robustHoldoutCandidates=${robust.length}`);
  for (const c of candidates.slice(0, 10)) console.log(`  H${c.horizon} MAE>=${c.maeThresholdR}R & MFE<${c.mfeThresholdR}R: DEV n=${c.dev.n} PF=${c.dev.PF?.toFixed(4) ?? 'n/a'} avgR=${c.dev.avgR.toFixed(4)} | VAL n=${c.validation.n} PF=${c.validation.PF?.toFixed(4) ?? 'n/a'} avgR=${c.validation.avgR.toFixed(4)} | HOLDOUT n=${c.holdout.n} PF=${c.holdout.PF?.toFixed(4) ?? 'n/a'} avgR=${c.holdout.avgR.toFixed(4)} totalR=${c.holdout.totalR.toFixed(4)} triggerRate=${(c.triggerRate * 100).toFixed(1)}%`);
  console.log(`Report -> ${out}`);
}
for (const tf of TIMEFRAMES) await run(tf);
