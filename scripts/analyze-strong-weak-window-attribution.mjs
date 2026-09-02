import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-strong-weak-window-attribution');
const TIMEFRAMES = ['1min', '5min'];
const WINDOW_COUNT = 8;
const MIN_WINDOW_N = 20;

function num(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function mean(values) {
  const xs = values.filter((x) => Number.isFinite(x));
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
}

function median(values) {
  const xs = values.filter((x) => Number.isFinite(x)).sort((a, b) => a - b);
  if (!xs.length) return null;
  const m = Math.floor(xs.length / 2);
  return xs.length % 2 ? xs[m] : (xs[m - 1] + xs[m]) / 2;
}

function sd(values) {
  const xs = values.filter((x) => Number.isFinite(x));
  if (xs.length < 2) return null;
  const m = mean(xs);
  return Math.sqrt(xs.reduce((s, x) => s + (x - m) ** 2, 0) / (xs.length - 1));
}

function summarize(rows) {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    PF: gl ? gp / gl : (gp ? null : 0),
    avgR: rs.length ? totalR / rs.length : 0,
    totalR,
  };
}

function session(entryTime) {
  const d = new Date(entryTime);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK_LATE';
  return 'OUTSIDE';
}

function candlesFromSource(source) {
  const rows = source.candles ?? source.data ?? [];
  return rows.map((c, i) => ({
    index: i,
    time: c.time ?? c.datetime ?? c.timestamp,
    open: num(c.open),
    high: num(c.high),
    low: num(c.low),
    close: num(c.close),
  })).filter((c) => c.time && [c.open, c.high, c.low, c.close].every(Number.isFinite));
}

function ema(values, period) {
  const out = Array(values.length).fill(null);
  if (!values.length) return out;
  const k = 2 / (period + 1);
  let e = values[0];
  out[0] = e;
  for (let i = 1; i < values.length; i += 1) {
    e = values[i] * k + e * (1 - k);
    out[i] = e;
  }
  return out;
}

function buildCandleFeatures(candles) {
  const tr = candles.map((c, i) => {
    if (i === 0) return c.high - c.low;
    return Math.max(c.high - c.low, Math.abs(c.high - candles[i - 1].close), Math.abs(c.low - candles[i - 1].close));
  });
  const ema20 = ema(candles.map((c) => c.close), 20);
  const ema60 = ema(candles.map((c) => c.close), 60);
  const out = new Map();

  for (let i = 0; i < candles.length; i += 1) {
    const c = candles[i];
    const lookback = tr.slice(Math.max(0, i - 13), i + 1);
    const priorRanges = tr.slice(Math.max(0, i - 20), i);
    const range = c.high - c.low;
    const body = Math.abs(c.close - c.open);
    const atr14 = mean(lookback);
    const priorRangeMedian = median(priorRanges);
    const prevClose = i > 0 ? candles[i - 1].close : null;
    const hh20 = Math.max(...candles.slice(Math.max(0, i - 20), i + 1).map((x) => x.high));
    const ll20 = Math.min(...candles.slice(Math.max(0, i - 20), i + 1).map((x) => x.low));

    out.set(i, {
      range,
      bodyFraction: range > 0 ? body / range : null,
      atr14,
      rangeToAtr: atr14 > 0 ? range / atr14 : null,
      closeLocation: range > 0 ? (c.close - c.low) / range : null,
      distanceFrom20HighAtr: atr14 > 0 ? (hh20 - c.close) / atr14 : null,
      distanceFrom20LowAtr: atr14 > 0 ? (c.close - ll20) / atr14 : null,
      trendGapAtr: atr14 > 0 && ema60[i] != null ? (c.close - ema60[i]) / atr14 : null,
      ema20GapAtr: atr14 > 0 && ema20[i] != null ? (c.close - ema20[i]) / atr14 : null,
      emaSlope20Atr: i >= 3 && atr14 > 0 && ema20[i] != null ? (ema20[i] - ema20[i - 3]) / atr14 : null,
      priorRangeMedian,
      rangeExpansion: priorRangeMedian > 0 ? range / priorRangeMedian : null,
      prevReturnAtr: prevClose != null && atr14 > 0 ? (c.close - prevClose) / atr14 : null,
    });
  }
  return out;
}

function chronologicalWindows(rows) {
  const sorted = [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const base = Math.floor(sorted.length / WINDOW_COUNT);
  return Array.from({ length: WINDOW_COUNT }, (_, i) => sorted.slice(
    i * base,
    i === WINDOW_COUNT - 1 ? sorted.length : (i + 1) * base,
  ));
}

function numericFeature(rows, key) {
  return rows.map((r) => num(r.features?.[key])).filter(Number.isFinite);
}

function effect(rowsA, rowsB, key) {
  const a = numericFeature(rowsA, key);
  const b = numericFeature(rowsB, key);
  const ma = mean(a);
  const mb = mean(b);
  const pooled = [sd(a), sd(b)].every(Number.isFinite) && a.length > 1 && b.length > 1
    ? Math.sqrt(((a.length - 1) * sd(a) ** 2 + (b.length - 1) * sd(b) ** 2) / (a.length + b.length - 2))
    : null;
  return {
    strongN: a.length,
    weakN: b.length,
    strongMean: ma,
    weakMean: mb,
    strongMedian: median(a),
    weakMedian: median(b),
    meanDeltaStrongMinusWeak: ma != null && mb != null ? ma - mb : null,
    standardizedDelta: pooled && ma != null && mb != null ? (ma - mb) / pooled : null,
  };
}

function categorical(rows, key) {
  const counts = {};
  for (const r of rows) {
    const value = r[key];
    if (value == null) continue;
    counts[value] = (counts[value] ?? 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).map(([value, count]) => [
    value,
    { n: count, rate: rows.length ? count / rows.length : 0 },
  ]));
}

function categoricalComparison(strong, weak, key) {
  const s = categorical(strong, key);
  const w = categorical(weak, key);
  const values = new Set([...Object.keys(s), ...Object.keys(w)]);
  return Object.fromEntries([...values].sort().map((value) => [value, {
    strongRate: s[value]?.rate ?? 0,
    weakRate: w[value]?.rate ?? 0,
    rateDelta: (s[value]?.rate ?? 0) - (w[value]?.rate ?? 0),
    strongN: s[value]?.n ?? 0,
    weakN: w[value]?.n ?? 0,
  }]));
}

async function run(timeframe) {
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`), 'utf8'));
  const candleSource = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
  const candles = candlesFromSource(candleSource);
  const candleFeatures = buildCandleFeatures(candles);

  const rows = (baseline.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .map((t) => {
      const entryIndex = Number(t.entryIndex);
      const candle = candleFeatures.get(entryIndex);
      return {
        ...t,
        rMultiple: Number(t.rMultiple),
        sessionDerived: session(t.entryTime),
        features: candle ?? {},
      };
    })
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const windows = chronologicalWindows(rows).map((windowRows, index) => ({
    window: index + 1,
    from: windowRows[0]?.entryTime ?? null,
    to: windowRows.at(-1)?.entryTime ?? null,
    ...summarize(windowRows),
    rows: windowRows,
  }));

  const eligible = windows.filter((w) => w.n >= MIN_WINDOW_N);
  const strong = eligible.filter((w) => w.PF != null && w.PF >= 1 && w.avgR > 0);
  const weak = eligible.filter((w) => !(w.PF != null && w.PF >= 1 && w.avgR > 0));
  const strongRows = strong.flatMap((w) => w.rows);
  const weakRows = weak.flatMap((w) => w.rows);

  const numericKeys = [
    'range', 'bodyFraction', 'atr14', 'rangeToAtr', 'closeLocation',
    'distanceFrom20HighAtr', 'distanceFrom20LowAtr', 'trendGapAtr',
    'ema20GapAtr', 'emaSlope20Atr', 'rangeExpansion', 'prevReturnAtr',
  ];
  const categoricalKeys = ['direction', 'sessionDerived', 'qualityGrade', 'emaAligned', 'nearRoundLevel', 'hasPGAPEvidence'];

  const windowFeatureSummary = windows.map((w) => ({
    window: w.window,
    from: w.from,
    to: w.to,
    n: w.n,
    PF: w.PF,
    avgR: w.avgR,
    features: Object.fromEntries(numericKeys.map((key) => [key, {
      n: numericFeature(w.rows, key).length,
      mean: mean(numericFeature(w.rows, key)),
      median: median(numericFeature(w.rows, key)),
    }])),
  }));

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_STRONG_WEAK_WINDOW_ATTRIBUTION_V1',
    timeframe,
    scope: 'Hypothesis-generation attribution only. Baseline resolved trades are grouped by the already-observed chronological performance of each window; only variables observable at or before entry are compared. No thresholds, windows, or features are promoted to production.',
    methodology: {
      windows: WINDOW_COUNT,
      ordering: 'chronological entryTime',
      minimumWindowN: MIN_WINDOW_N,
      strongDefinition: 'eligible window with PF >= 1 and avgR > 0',
      weakDefinition: 'eligible window not satisfying the strong definition',
      candleFeatureSource: `data/historical/xauusd-${timeframe}.json at trade entryIndex`,
      leakageControl: 'Outcome is used only to label historical windows for attribution. Candidate descriptors are calculated from entry-time or earlier market data; no future candle is used.',
      interpretation: 'This report is descriptive and post-hoc. A difference between strong and weak windows is not evidence of a tradable edge. Do not fit thresholds to these results or use the strong windows themselves as a production regime filter.',
      promotionGate: 'Only one pre-registered market-state hypothesis may proceed, and only after it is frozen before evaluation on a fresh untouched holdout.',
    },
    overall: summarize(rows),
    windowPerformance: windows.map(({ rows: _rows, ...rest }) => ({ ...rest, label: strong.includes(windows[rest.window - 1]) ? 'STRONG' : 'WEAK' })),
    groupCounts: {
      eligibleWindows: eligible.length,
      strongWindows: strong.length,
      weakWindows: weak.length,
      strongTrades: strongRows.length,
      weakTrades: weakRows.length,
    },
    strongVsWeakNumeric: Object.fromEntries(numericKeys.map((key) => [key, effect(strongRows, weakRows, key)])),
    strongVsWeakCategorical: Object.fromEntries(categoricalKeys.map((key) => [key, categoricalComparison(strongRows, weakRows, key)])),
    byWindowFeatureSummary: windowFeatureSummary,
    cautions: [
      'The strong/weak labels are derived from realized window outcomes and therefore cannot be used as a predictive label in live trading.',
      'A feature with a large descriptive difference may be a consequence of sampling, confounding, or the baseline setup composition.',
      'No p-value, threshold search, or automatic feature selection is performed in this stage.',
      'Do not optimize against W1 or any other individual best-performing window.',
    ],
    nextStep: 'Review whether one pre-entry market-state descriptor shows a coherent cross-window pattern rather than a single-window spike. If yes, write exactly one pre-registered hypothesis with a fixed rule before touching the fresh holdout. If no, revisit baseline setup definition instead of adding filters.',
  };

  delete report.windowPerformance[0]?.rows;
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`${timeframe}: baseline=${rows.length} eligibleWindows=${eligible.length} strong=${strong.length} weak=${weak.length} strongTrades=${strongRows.length} weakTrades=${weakRows.length}`);
  for (const w of windows) {
    const label = strong.includes(w) ? 'STRONG' : 'WEAK';
    console.log(`  W${w.window} ${label}: n=${w.n} PF=${w.PF?.toFixed(4) ?? 'n/a'} avgR=${w.avgR.toFixed(4)} ${w.from ?? 'n/a'} -> ${w.to ?? 'n/a'}`);
  }
  console.log('  Numeric attribution (standardized strong-minus-weak):');
  for (const key of numericKeys) {
    const x = report.strongVsWeakNumeric[key];
    console.log(`    ${key}: delta=${x.meanDeltaStrongMinusWeak?.toFixed(4) ?? 'n/a'} d=${x.standardizedDelta?.toFixed(4) ?? 'n/a'} n=${x.strongN}/${x.weakN}`);
  }
  console.log(`Report -> ${out}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
