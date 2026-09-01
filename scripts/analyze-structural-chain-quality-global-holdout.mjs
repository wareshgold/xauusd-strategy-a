import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-structural-chain-quality-global-holdout');
const TIMEFRAMES = ['1min', '5min'];
const SWING_RADIUS = 2;
const STRUCTURE_LOOKBACK = 80;
const DISPLACEMENT_LOOKBACK = 20;
const DISPLACEMENT_MULTIPLE = 1.5;
const DISPLACEMENT_BODY_FRACTION = 0.6;
const MIN_GAP = 0;

function sign(direction) { return direction === 'BUY' ? 1 : -1; }
function tr(c) { return Math.max(c.high - c.low, Math.abs(c.high - c.open), Math.abs(c.low - c.open)); }
function bodyFraction(c) { const r = c.high - c.low; return r > 0 ? Math.abs(c.close - c.open) / r : 0; }
function median(a) { const x = a.filter(Number.isFinite).sort((p, q) => p - q); if (!x.length) return null; const m = Math.floor(x.length / 2); return x.length % 2 ? x[m] : (x[m - 1] + x[m]) / 2; }
function summarize(rows) {
  const a = rows.filter(r => Number.isFinite(r.rMultiple));
  const gp = a.filter(r => r.rMultiple > 0).reduce((s, r) => s + r.rMultiple, 0);
  const gl = a.filter(r => r.rMultiple < 0).reduce((s, r) => s - r.rMultiple, 0);
  return { n: a.length, wins: a.filter(r => r.rMultiple > 0).length, losses: a.filter(r => r.rMultiple < 0).length, PF: gl ? gp / gl : null, avgR: a.length ? a.reduce((s, r) => s + r.rMultiple, 0) / a.length : 0, totalR: a.reduce((s, r) => s + r.rMultiple, 0) };
}
function dd(rows) { let e = 0, p = 0, m = 0; for (const r of rows.filter(x => Number.isFinite(x.rMultiple))) { e += r.rMultiple; p = Math.max(p, e); m = Math.max(m, p - e); } return m; }
function gate(x) { return x.n >= 15 && x.PF != null && x.PF >= 1 && x.avgR > 0; }

function swings(candles, start, end) {
  const highs = [], lows = [];
  for (let i = Math.max(start + SWING_RADIUS, SWING_RADIUS); i < Math.min(end - SWING_RADIUS, candles.length - SWING_RADIUS); i++) {
    let hi = true, lo = true;
    for (let j = 1; j <= SWING_RADIUS; j++) {
      if (candles[i].high <= candles[i - j].high || candles[i].high <= candles[i + j].high) hi = false;
      if (candles[i].low >= candles[i - j].low || candles[i].low >= candles[i + j].low) lo = false;
    }
    if (hi) highs.push({ i, price: candles[i].high });
    if (lo) lows.push({ i, price: candles[i].low });
  }
  return { highs, lows };
}

function findChain(candles, t) {
  const ei = t.entryIndex;
  if (!Number.isInteger(ei) || ei < STRUCTURE_LOOKBACK || !candles[ei]) return null;
  const s = sign(t.direction);
  const start = Math.max(0, ei - STRUCTURE_LOOKBACK);
  const end = ei;
  const { highs, lows } = swings(candles, start, end);
  if (!highs.length || !lows.length) return null;

  // A liquidity sweep must occur before the structural break. The sweep is strict:
  // wick through a prior confirmed swing and close back through that same level.
  const sweepCandidates = s > 0
    ? lows.filter(x => x.i >= start + SWING_RADIUS && x.i < ei - 2)
    : highs.filter(x => x.i >= start + SWING_RADIUS && x.i < ei - 2);
  let sweep = null;
  for (const sw of sweepCandidates) {
    const nextEnd = Math.min(ei - 1, sw.i + 20);
    for (let i = sw.i + 1; i <= nextEnd; i++) {
      const c = candles[i];
      const swept = s > 0 ? c.low < sw.price && c.close > sw.price : c.high > sw.price && c.close < sw.price;
      if (swept) { sweep = { i, swingIndex: sw.i, price: sw.price }; break; }
    }
    if (sweep) break;
  }

  const breakStart = sweep ? sweep.i + 1 : start + SWING_RADIUS;
  const opposing = s > 0 ? highs.filter(x => x.i < ei && x.i >= start) : lows.filter(x => x.i < ei && x.i >= start);
  let bos = null;
  for (const sw of opposing) {
    if (sw.i < breakStart) {
      for (let i = breakStart; i < ei; i++) {
        const c = candles[i];
        const broken = s > 0 ? c.close > sw.price : c.close < sw.price;
        if (broken) { bos = { i, swingIndex: sw.i, price: sw.price }; break; }
      }
      if (bos) break;
    }
  }

  const dispStart = bos ? bos.i : (sweep ? sweep.i + 1 : start);
  const medianTR = median(candles.slice(Math.max(start, dispStart - DISPLACEMENT_LOOKBACK), dispStart).map(tr));
  let displacement = null;
  for (let i = dispStart; i < ei; i++) {
    const c = candles[i];
    const aligned = s > 0 ? c.close > c.open : c.close < c.open;
    if (aligned && medianTR && tr(c) >= medianTR * DISPLACEMENT_MULTIPLE && bodyFraction(c) >= DISPLACEMENT_BODY_FRACTION) {
      displacement = { i, score: tr(c) / medianTR };
      break;
    }
  }

  // Three-candle fair-value gap, detected without using the entry candle or later data.
  let fvg = null;
  const fvgStart = displacement ? displacement.i + 1 : (bos ? bos.i + 1 : breakStart);
  for (let i = fvgStart + 2; i < ei; i++) {
    const a = candles[i - 2], c = candles[i];
    const bullishGap = c.low - a.high;
    const bearishGap = a.low - c.high;
    if (s > 0 ? bullishGap > MIN_GAP : bearishGap > MIN_GAP) {
      fvg = { i, low: s > 0 ? a.high : c.high, high: s > 0 ? c.low : a.low };
      break;
    }
  }

  // Retest requires price to enter the FVG after it is formed and before entry.
  let retest = null;
  if (fvg) {
    for (let i = fvg.i + 1; i < ei; i++) {
      const c = candles[i];
      const touches = c.low <= fvg.high && c.high >= fvg.low;
      if (touches) { retest = { i }; break; }
    }
  }

  const full = Boolean(sweep && bos && displacement && fvg && retest && sweep.i < bos.i && bos.i <= displacement.i && displacement.i < fvg.i && fvg.i < retest.i && retest.i < ei);
  const sweepBosDisp = Boolean(sweep && bos && displacement && sweep.i < bos.i && bos.i <= displacement.i && displacement.i < ei);
  const sweepBos = Boolean(sweep && bos && sweep.i < bos.i);
  const bosDisp = Boolean(bos && displacement && bos.i <= displacement.i && displacement.i < ei);
  const fvgRetest = Boolean(fvg && retest && fvg.i < retest.i && retest.i < ei);

  return {
    ...t,
    sweep: Boolean(sweep), bos: Boolean(bos), displacement: Boolean(displacement), fvg: Boolean(fvg), retest: Boolean(retest),
    sweepBosDisp, sweepBos, bosDisp, fvgRetest, fullChain: full,
    sweepIndex: sweep?.i ?? null, bosIndex: bos?.i ?? null, displacementIndex: displacement?.i ?? null, fvgIndex: fvg?.i ?? null, retestIndex: retest?.i ?? null
  };
}

function split(rows) {
  const n = rows.length, d = Math.floor(n * 0.4), v = Math.floor(n * 0.7);
  return { dev: rows.slice(0, d), validation: rows.slice(d, v), holdout: rows.slice(v) };
}
function evalBucket(rows, key) { const a = rows.filter(r => r[key] === true); return { ...summarize(a), maxDD: dd(a) }; }

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles;
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`), 'utf8'));
  const rows = baseline.trades.filter(t => Number.isFinite(t.rMultiple)).map(t => findChain(candles, t)).filter(Boolean).sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const parts = split(rows);
  const defs = [
    ['sweep', 'Liquidity sweep'], ['bos', 'BOS/MSS proxy'], ['displacement', 'Displacement'], ['fvg', 'FVG'], ['retest', 'FVG retest'],
    ['sweepBos', 'Sweep → BOS'], ['bosDisp', 'BOS → displacement'], ['sweepBosDisp', 'Sweep → BOS → displacement'], ['fvgRetest', 'FVG → retest'], ['fullChain', 'Sweep → BOS → displacement → FVG → retest']
  ];
  const features = {};
  for (const [key, label] of defs) {
    const dev = evalBucket(parts.dev, key), val = evalBucket(parts.validation, key), hold = evalBucket(parts.holdout, key);
    features[key] = { label, dev, validation: val, holdout: hold, devGate: gate(dev), validationGate: gate(val), holdoutGate: gate(hold) };
  }
  const report = {
    strategy: 'Strategy A / SP2L', mode: 'RESEARCH_STRUCTURAL_CHAIN_QUALITY_GLOBAL_HOLDOUT', timeframe,
    scope: 'Baseline trades only; structural components inferred deterministically from pre-entry candles; no production rule changes; no threshold optimization',
    methodology: {
      swing: `confirmed ${SWING_RADIUS}-bar pivot highs/lows`,
      liquiditySweep: 'wick through a prior confirmed swing followed by close back through that level',
      bosMss: 'close beyond the most recent opposing confirmed swing after the sweep when available',
      displacement: `directional candle with TR >= ${DISPLACEMENT_MULTIPLE}x preceding median TR and body/range >= ${DISPLACEMENT_BODY_FRACTION}`,
      fvg: 'three-candle directional gap formed before entry',
      retest: 'subsequent candle overlaps the FVG before entry',
      fullChain: 'strict chronological Sweep → BOS/MSS → Displacement → FVG → Retest',
      split: 'chronological 40% DEV / 30% VALIDATION / 30% untouched HOLDOUT',
      promotionGate: 'diagnostic survivor requires n >= 15, PF >= 1, avgR > 0 in DEV and VALIDATION; HOLDOUT never used for selection'
    },
    coverage: { baselineTrades: baseline.trades.length, classifiedTrades: rows.length },
    overall: { ...summarize(rows), maxDD: dd(rows) },
    features,
    selection: { eligibleForHoldoutReview: defs.filter(([key]) => features[key].devGate && features[key].validationGate).map(([key]) => key), note: 'Holdout is evaluation-only; no feature is promoted automatically.' },
    tradeRows: rows
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: baseline=${baseline.trades.length} classified=${rows.length}`);
  for (const [key, label] of defs) {
    const x = features[key];
    console.log(`  ${label}: DEV n=${x.dev.n} PF=${x.dev.PF?.toFixed(4) ?? 'n/a'} avgR=${x.dev.avgR.toFixed(4)} | VAL n=${x.validation.n} PF=${x.validation.PF?.toFixed(4) ?? 'n/a'} avgR=${x.validation.avgR.toFixed(4)} | HOLD n=${x.holdout.n} PF=${x.holdout.PF?.toFixed(4) ?? 'n/a'} avgR=${x.holdout.avgR.toFixed(4)} | survivor=${x.devGate && x.validationGate}`);
  }
  console.log(`eligibleForHoldoutReview=${report.selection.eligibleForHoldoutReview.join(',') || 'none'}`);
  console.log(`Report -> ${out}`);
}
for (const tf of TIMEFRAMES) await run(tf);
