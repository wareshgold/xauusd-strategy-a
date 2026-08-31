import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-candidate-quality');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-threshold-grid');

const BANDS = [
  { name: 'LT_0.02', min: -Infinity, max: 0.02 },
  { name: '0.02_0.05', min: 0.02, max: 0.05 },
  { name: '0.05_0.10', min: 0.05, max: 0.10 },
  { name: '0.10_0.20', min: 0.10, max: 0.20 },
  { name: '0.20_0.40', min: 0.20, max: 0.40 },
  { name: 'GE_0.40', min: 0.40, max: Infinity },
];

function percentile(values, p) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const i = (a.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (i - lo);
}

function stats(rows) {
  const rs = rows.map(r => r.rMultiple).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0);
  const losses = rs.filter(r => r < 0);
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
  let equity = 0;
  let peak = 0;
  let dd = 0;
  for (const row of [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)))) {
    equity += Number.isFinite(row.rMultiple) ? row.rMultiple : 0;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
  }
  return dd;
}

function bandFor(value) {
  if (!Number.isFinite(value)) return 'NA';
  return BANDS.find(b => value >= b.min && value < b.max)?.name ?? 'NA';
}

function enrich(rows) {
  return rows.map(r => ({
    ...r,
    ratio: r.pgap?.maxGapToSpike,
    ratioBand: bandFor(r.pgap?.maxGapToSpike),
  }));
}

function grid(rows) {
  return Object.fromEntries(BANDS.map(b => {
    const subset = rows.filter(r => r.ratioBand === b.name);
    return [b.name, { ...stats(subset), DD: maxDrawdown(subset) }];
  }));
}

function filtered(rows, threshold) {
  return rows.filter(r => Number.isFinite(r.ratio) && r.ratio <= threshold);
}

function thresholdStudy(rows) {
  const thresholds = [0.02, 0.05, 0.10, 0.20, 0.40];
  return Object.fromEntries(thresholds.map(threshold => {
    const kept = filtered(rows, threshold);
    return [`LE_${threshold.toFixed(2)}`, {
      threshold,
      kept: kept.length,
      coverage: rows.length ? kept.length / rows.length : 0,
      ...stats(kept),
      DD: maxDrawdown(kept),
    }];
  }));
}

async function analyze(timeframe) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const rows = enrich(report.trades ?? []);
  const secondHalfIndex = Math.floor(rows.length / 2);
  const chronological = [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)));
  const oos = chronological.slice(secondHalfIndex);
  const reportOut = {
    strategy: 'Strategy A / SP2L',
    timeframe,
    sourceReport: `data/reports/strategy-a-pgap-candidate-quality/${timeframe}.json`,
    purpose: 'Diagnostic threshold-distribution study for pre-entry P-GAP candidate size relative to spike size. No threshold is promoted to a trading rule.',
    fullSample: {
      trades: rows.length,
      baseline: stats(rows),
      baselineDD: maxDrawdown(rows),
      ratioDistribution: {
        p25: percentile(rows.map(r => r.ratio), 0.25),
        p50: percentile(rows.map(r => r.ratio), 0.50),
        p75: percentile(rows.map(r => r.ratio), 0.75),
        p90: percentile(rows.map(r => r.ratio), 0.90),
      },
      byRatioBand: grid(rows),
      cumulativeUpperThresholds: thresholdStudy(rows),
    },
    oosSecondHalf: {
      trades: oos.length,
      baseline: stats(oos),
      baselineDD: maxDrawdown(oos),
      byRatioBand: grid(oos),
      cumulativeUpperThresholds: thresholdStudy(oos),
    },
    byDirection: Object.fromEntries(['BUY', 'SELL'].map(direction => [direction, {
      trades: rows.filter(r => r.direction === direction).length,
      byRatioBand: grid(rows.filter(r => r.direction === direction)),
      cumulativeUpperThresholds: thresholdStudy(rows.filter(r => r.direction === direction)),
    }])),
    bySession: Object.fromEntries([...new Set(rows.map(r => r.session).filter(Boolean))].map(session => [session, {
      trades: rows.filter(r => r.session === session).length,
      byRatioBand: grid(rows.filter(r => r.session === session)),
    }])),
    researchWarnings: [
      'P-GAP candidate evidence is heuristic and is not yet a validated P-GAP definition.',
      'Small bins can show unstable PF/AvgR and must not be treated as evidence of a robust edge.',
      'The second-half split is an exploratory OOS check, not a formal walk-forward validation.',
      'No threshold or filter is activated by this report.',
    ],
  };

  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(reportOut, null, 2));
  console.log(`${timeframe}: trades=${rows.length} ratioP50=${reportOut.fullSample.ratioDistribution.p50 ?? 'n/a'} ratioP90=${reportOut.fullSample.ratioDistribution.p90 ?? 'n/a'}`);
  for (const [name, value] of Object.entries(reportOut.fullSample.byRatioBand)) {
    console.log(`  ${name}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} totalR=${value.totalR.toFixed(4)} DD=${value.DD.toFixed(4)}`);
  }
  console.log(`  OOS second-half: trades=${oos.length} PF=${reportOut.oosSecondHalf.baseline.PF?.toFixed(4) ?? 'n/a'} avgR=${reportOut.oosSecondHalf.baseline.avgR.toFixed(4)}`);
  for (const [name, value] of Object.entries(reportOut.oosSecondHalf.byRatioBand)) {
    console.log(`  OOS ${name}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} totalR=${value.totalR.toFixed(4)}`);
  }
  await writeFile(out, JSON.stringify(reportOut, null, 2));
  console.log(`Report -> ${out}`);
}

await analyze('1min');
await analyze('5min');
