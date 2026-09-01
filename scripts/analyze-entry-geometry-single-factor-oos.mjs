import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-entry-geometry-single-factor-oos');
const TIMEFRAMES = ['1min', '5min'];
const LOOKBACK = 60;
const IMPULSE_LOOKBACK = 20;

function finite(x) { return Number.isFinite(Number(x)); }
function median(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
function tr(c) { return Math.max(c.high - c.low, Math.abs(c.high - c.open), Math.abs(c.low - c.open)); }
function sign(direction) { return direction === 'BUY' ? 1 : -1; }
function stats(rows) {
  const a = rows.filter(r => finite(r.rMultiple));
  const gp = a.filter(r => r.rMultiple > 0).reduce((s, r) => s + r.rMultiple, 0);
  const gl = a.filter(r => r.rMultiple < 0).reduce((s, r) => s - r.rMultiple, 0);
  return {
    n: a.length,
    wins: a.filter(r => r.rMultiple > 0).length,
    losses: a.filter(r => r.rMultiple < 0).length,
    PF: gl ? gp / gl : null,
    avgR: a.length ? a.reduce((s, r) => s + r.rMultiple, 0) / a.length : null,
    totalR: a.reduce((s, r) => s + r.rMultiple, 0),
  };
}
function bucket(x, cuts, labels) {
  if (!finite(x)) return null;
  for (let i = 0; i < cuts.length; i++) if (x < cuts[i]) return labels[i];
  return labels.at(-1);
}
function thirds(rows) {
  const n = rows.length;
  const a = Math.floor(n / 3);
  const b = Math.floor((2 * n) / 3);
  return { dev: rows.slice(0, a), validation: rows.slice(a, b), holdout: rows.slice(b) };
}
function summarizeBucket(rows, key, cuts, labels) {
  const parts = thirds(rows);
  return labels.map(label => {
    const select = part => part.filter(r => bucket(r[key], cuts, labels) === label);
    const dev = stats(select(parts.dev));
    const validation = stats(select(parts.validation));
    const holdout = stats(select(parts.holdout));
    const gate = Boolean(dev.n >= 15 && validation.n >= 15 && dev.PF >= 1 && dev.avgR > 0 && validation.PF >= 1 && validation.avgR > 0);
    return { bucket: label, dev, validation, holdout, gate };
  });
}
function feature(candles, trade) {
  const ei = Number(trade.entryIndex);
  if (!Number.isInteger(ei) || ei < LOOKBACK || !candles[ei]) return null;
  const s = sign(trade.direction);
  const start = Math.max(LOOKBACK, ei - IMPULSE_LOOKBACK);
  const medianTR = median(candles.slice(ei - LOOKBACK, ei).map(tr));
  if (!medianTR || medianTR <= 0) return null;

  let impulseIndex = null;
  let best = -Infinity;
  for (let i = start; i < ei; i++) {
    const c = candles[i];
    const directionalBody = s > 0 ? c.close - c.open : c.open - c.close;
    const score = tr(c) / medianTR;
    if (directionalBody > 0 && score > best) {
      best = score;
      impulseIndex = i;
    }
  }
  if (impulseIndex == null) return null;

  const imp = candles[impulseIndex];
  const range = tr(imp);
  const between = candles.slice(impulseIndex + 1, ei);
  const extreme = between.length
    ? (s > 0 ? Math.min(...between.map(c => c.low)) : Math.max(...between.map(c => c.high)))
    : (s > 0 ? candles[ei].low : candles[ei].high);

  const retracement = s > 0 ? (imp.high - extreme) / range : (extreme - imp.low) / range;
  const entryLocation = s > 0 ? (trade.entry - imp.low) / range : (imp.high - trade.entry) / range;
  const distanceFromExtreme = s > 0 ? (imp.high - trade.entry) / range : (trade.entry - imp.low) / range;
  const bodyFraction = range > 0 ? Math.abs(imp.close - imp.open) / range : null;
  const delayFromImpulse = ei - impulseIndex;
  const recent = between.slice(-5).map(tr);
  const older = between.slice(-15, -5).map(tr);
  const compressionRatio = recent.length && older.length ? median(recent) / median(older) : null;

  return {
    ...trade,
    impulseScore: best,
    impulseRange: range,
    impulseBodyFraction: bodyFraction,
    retracement,
    entryLocation,
    distanceFromExtreme,
    delayFromImpulse,
    compressionRatio,
    stopToImpulse: finite(trade.riskDistance) ? Number(trade.riskDistance) / range : null,
  };
}

const DEFINITIONS = [
  ['impulseScore', [1, 1.25, 1.5, 2, 2.5, Infinity], ['LT_1.00', '1.00_1.25', '1.25_1.50', '1.50_2.00', '2.00_2.50', 'GE_2.50']],
  ['retracement', [0.25, 0.5, 0.75, 1, Infinity], ['LT_25%', '25_50%', '50_75%', '75_100%', 'GE_100%']],
  ['entryLocation', [0.25, 0.5, 0.75, Infinity], ['0_25%', '25_50%', '50_75%', '75_100%']],
  ['distanceFromExtreme', [0.25, 0.5, 0.75, Infinity], ['0_25%', '25_50%', '50_75%', '75_100%']],
  ['delayFromImpulse', [3, 6, 9, 13, Infinity], ['D0_2', 'D3_5', 'D6_8', 'D9_12', 'D13_PLUS']],
  ['impulseBodyFraction', [0.4, 0.6, 0.8, Infinity], ['LT_40%', '40_60%', '60_80%', 'GE_80%']],
  ['compressionRatio', [0.75, 1, 1.25, Infinity], ['LT_75%', '75_100%', '100_125%', 'GE_125%']],
  ['stopToImpulse', [0.25, 0.5, 0.75, 1, Infinity], ['LT_25%', '25_50%', '50_75%', '75_100%', 'GE_100%']],
];

async function run(tf) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles;
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${tf}.json`), 'utf8'));
  const rows = baseline.trades.filter(t => finite(t.rMultiple)).map(t => feature(candles, t)).filter(Boolean).sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_ENTRY_GEOMETRY_SINGLE_FACTOR_THIRDS_OOS_V1',
    timeframe: tf,
    methodology: {
      scope: 'Baseline trades only; pre-entry geometry; no production rule changes',
      split: 'Chronological thirds: DEV / VALIDATION / untouched HOLDOUT',
      selectionGate: 'A bucket is research-eligible only when DEV and VALIDATION each have n>=15, PF>=1 and avgR>0. HOLDOUT is never used for selection.',
      features: 'Fixed geometry definitions reused from existing forensics; no threshold search or optimization performed here.',
      lookahead: 'All geometry features use candles strictly before entry.',
    },
    coverage: { baselineTrades: baseline.trades.length, classifiedTrades: rows.length },
    overall: stats(rows),
    features: {},
  };

  for (const [key, cuts, labels] of DEFINITIONS) {
    report.features[key] = summarizeBucket(rows, key, cuts, labels);
  }

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: baseline=${baseline.trades.length} classified=${rows.length}`);
  for (const [key] of DEFINITIONS) {
    const eligible = report.features[key].filter(x => x.gate);
    console.log(`  ${key}: eligible=${eligible.map(x => x.bucket).join(',') || 'none'}`);
    for (const x of report.features[key]) {
      console.log(`    ${x.bucket}: DEV ${x.dev.n}/${x.dev.PF?.toFixed(3) ?? 'n/a'}/${x.dev.avgR?.toFixed(3) ?? 'n/a'} | VAL ${x.validation.n}/${x.validation.PF?.toFixed(3) ?? 'n/a'}/${x.validation.avgR?.toFixed(3) ?? 'n/a'} | HOLD ${x.holdout.n}/${x.holdout.PF?.toFixed(3) ?? 'n/a'}/${x.holdout.avgR?.toFixed(3) ?? 'n/a'} gate=${x.gate}`);
    }
  }
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
