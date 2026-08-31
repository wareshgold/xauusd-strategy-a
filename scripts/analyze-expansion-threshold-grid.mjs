import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');
const DATA = resolve(ROOT, 'data/historical');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-expansion-threshold-grid');
const LOOKBACK = 20;
const BANDS = [
  { name: 'LT_1.00', min: -Infinity, max: 1.00 },
  { name: '1.00_1.25', min: 1.00, max: 1.25 },
  { name: '1.25_1.50', min: 1.25, max: 1.50 },
  { name: '1.50_2.00', min: 1.50, max: 2.00 },
  { name: '2.00_2.50', min: 2.00, max: 2.50 },
  { name: 'GE_2.50', min: 2.50, max: Infinity },
];

function percentile(values, p) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const i = (a.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (i - lo);
}

function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0), losses = rs.filter(r => r < 0);
  const grossWin = wins.reduce((s, r) => s + r, 0);
  const grossLoss = Math.abs(losses.reduce((s, r) => s + r, 0));
  return {
    trades: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    avgR: rs.length ? rs.reduce((s, r) => s + r, 0) / rs.length : 0,
    totalR: rs.reduce((s, r) => s + r, 0),
    PF: grossLoss ? grossWin / grossLoss : null,
    medianR: percentile(rs, 0.5),
  };
}

function maxDrawdown(rows) {
  let equity = 0, peak = 0, dd = 0;
  for (const row of [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)))) {
    equity += Number.isFinite(row.rMultiple) ? row.rMultiple : 0;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
  }
  return dd;
}

function swingPoints(candles) {
  const out = [];
  const pivot = 2;
  for (let i = pivot; i < candles.length - pivot; i++) {
    const c = candles[i];
    let high = true, low = true;
    for (let j = i - pivot; j <= i + pivot; j++) {
      if (j === i) continue;
      if (candles[j].high >= c.high) high = false;
      if (candles[j].low <= c.low) low = false;
    }
    if (high) out.push({ index: i, side: 'HIGH', price: c.high });
    if (low) out.push({ index: i, side: 'LOW', price: c.low });
  }
  return out.sort((a, b) => a.index - b.index || a.side.localeCompare(b.side));
}

function expansionAt(candles, index) {
  if (!Number.isInteger(index) || index < LOOKBACK || index >= candles.length) return null;
  const c = candles[index];
  const range = Number(c.high) - Number(c.low);
  if (!(range > 0)) return null;
  const priorRanges = candles
    .slice(Math.max(0, index - LOOKBACK), index)
    .map(x => Number(x.high) - Number(x.low))
    .filter(x => x > 0 && Number.isFinite(x));
  if (!priorRanges.length) return null;
  const medianRange = percentile(priorRanges, 0.5);
  return medianRange > 0 ? range / medianRange : null;
}

function bandFor(v) {
  if (!Number.isFinite(v)) return 'NA';
  return BANDS.find(b => v >= b.min && v < b.max)?.name ?? 'NA';
}

function enrich(rows, candles) {
  return rows.map(r => {
    const expansion = expansionAt(candles, Number(r.entryIndex));
    return { ...r, expansion, expansionBand: bandFor(expansion) };
  });
}

function grid(rows) {
  return Object.fromEntries(BANDS.map(b => {
    const subset = rows.filter(r => r.expansionBand === b.name);
    return [b.name, { ...stats(subset), DD: maxDrawdown(subset) }];
  }));
}

function cumulativeThresholds(rows) {
  const thresholds = [1.00, 1.25, 1.50, 2.00, 2.50];
  return Object.fromEntries(thresholds.map(threshold => {
    const kept = rows.filter(r => Number.isFinite(r.expansion) && r.expansion >= threshold);
    return [`GE_${threshold.toFixed(2)}`, {
      threshold,
      kept: kept.length,
      coverage: rows.length ? kept.length / rows.length : 0,
      ...stats(kept),
      DD: maxDrawdown(kept),
    }];
  }));
}

function splitHalf(rows) {
  const sorted = [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)));
  const m = Math.floor(sorted.length / 2);
  return [sorted.slice(0, m), sorted.slice(m)];
}

async function analyze(timeframe) {
  const baseline = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const dataset = JSON.parse(await readFile(resolve(DATA, `xauusd-${timeframe}.json`), 'utf8'));
  const rows = enrich((baseline.trades ?? []).filter(t => Number.isFinite(t.rMultiple)), dataset.candles);
  const [first, second] = splitHalf(rows);
  const validRatios = rows.map(r => r.expansion).filter(Number.isFinite);
  const outObj = {
    strategy: 'Strategy A / SP2L',
    timeframe,
    sourceReport: `data/reports/strategy-a-baseline/${timeframe}.json`,
    purpose: 'Diagnostic threshold-distribution study for candle-range expansion versus the preceding 20-candle median range at baseline entry. No threshold is promoted to a trading rule.',
    definition: 'expansion = entry-candle high-low range / median high-low range of the preceding 20 candles.',
    probeParameters: { lookback: LOOKBACK, pivot: 2 },
    fullSample: {
      trades: rows.length,
      baseline: stats(rows),
      baselineDD: maxDrawdown(rows),
      expansionDistribution: {
        p25: percentile(validRatios, 0.25),
        p50: percentile(validRatios, 0.50),
        p75: percentile(validRatios, 0.75),
        p90: percentile(validRatios, 0.90),
      },
      byExpansionBand: grid(rows),
      cumulativeLowerThresholds: cumulativeThresholds(rows),
    },
    oosSecondHalf: {
      trades: second.length,
      baseline: stats(second),
      baselineDD: maxDrawdown(second),
      byExpansionBand: grid(second),
      cumulativeLowerThresholds: cumulativeThresholds(second),
    },
    firstHalf: {
      trades: first.length,
      baseline: stats(first),
      byExpansionBand: grid(first),
      cumulativeLowerThresholds: cumulativeThresholds(first),
    },
    researchWarnings: [
      'Expansion is a diagnostic reconstruction, not a validated production feature definition.',
      'Pivot=2 and lookback=20 are fixed diagnostic probes and are not optimized here.',
      'Small bins can show unstable PF/AvgR and must not be treated as robust evidence.',
      'The second-half split is an exploratory OOS check, not formal walk-forward validation.',
      'No threshold or filter is activated by this report.',
    ],
  };
  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(outObj, null, 2));
  console.log(`${timeframe}: trades=${rows.length} expansionP50=${outObj.fullSample.expansionDistribution.p50 ?? 'n/a'} expansionP90=${outObj.fullSample.expansionDistribution.p90 ?? 'n/a'}`);
  for (const [name, value] of Object.entries(outObj.fullSample.byExpansionBand)) {
    console.log(`  ${name}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} totalR=${value.totalR.toFixed(4)} DD=${value.DD.toFixed(4)}`);
  }
  console.log(`  OOS second-half: trades=${second.length} PF=${outObj.oosSecondHalf.baseline.PF?.toFixed(4) ?? 'n/a'} avgR=${outObj.oosSecondHalf.baseline.avgR.toFixed(4)} totalR=${outObj.oosSecondHalf.baseline.totalR.toFixed(4)}`);
  for (const [name, value] of Object.entries(outObj.oosSecondHalf.byExpansionBand)) {
    console.log(`  OOS ${name}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} totalR=${value.totalR.toFixed(4)}`);
  }
  console.log(`Report -> ${out}`);
}

await analyze('1min');
await analyze('5min');
