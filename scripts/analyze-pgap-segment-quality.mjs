import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-candidate-quality');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-segment-quality');

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
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
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

function band(value) {
  if (!Number.isFinite(value)) return 'NA';
  return BANDS.find(b => value >= b.min && value < b.max)?.name ?? 'NA';
}

function grouped(rows, keyFn) {
  const map = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return Object.fromEntries([...map].map(([key, subset]) => [key, stats(subset)]));
}

function segmentGrid(rows) {
  const result = {};
  for (const direction of ['BUY', 'SELL']) {
    for (const session of ['LONDON_ONLY', 'OVERLAP', 'NEW_YORK_ONLY', 'OUTSIDE', 'LONDON', 'NEW_YORK']) {
      const subset = rows.filter(r => r.direction === direction && r.session === session);
      if (subset.length) result[`${direction}__${session}`] = {
        overall: stats(subset),
        byRatioBand: grouped(subset, r => band(r.pgap?.maxGapToSpike)),
      };
    }
  }
  return result;
}

function oosSecondHalf(rows) {
  const chronological = [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)));
  return chronological.slice(Math.floor(chronological.length / 2));
}

async function analyze(timeframe) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const rows = (report.trades ?? []).filter(r => Number.isFinite(r.rMultiple));
  const oos = oosSecondHalf(rows);
  const reportOut = {
    strategy: 'Strategy A / SP2L',
    timeframe,
    sourceReport: `data/reports/strategy-a-pgap-candidate-quality/${timeframe}.json`,
    purpose: 'Diagnostic interaction study of heuristic P-GAP candidate ratio with direction and session. No P-GAP rule is activated.',
    fullSample: {
      baseline: stats(rows),
      byDirection: grouped(rows, r => r.direction ?? 'NA'),
      bySession: grouped(rows, r => r.session ?? 'NA'),
      byDirectionAndSession: grouped(rows, r => `${r.direction ?? 'NA'}__${r.session ?? 'NA'}`),
      byDirectionSessionRatio: segmentGrid(rows),
    },
    oosSecondHalf: {
      baseline: stats(oos),
      byDirection: grouped(oos, r => r.direction ?? 'NA'),
      bySession: grouped(oos, r => r.session ?? 'NA'),
      byDirectionAndSession: grouped(oos, r => `${r.direction ?? 'NA'}__${r.session ?? 'NA'}`),
      byDirectionSessionRatio: segmentGrid(oos),
    },
    researchWarnings: [
      'P-GAP is still a heuristic candidate definition, not a validated market-structure rule.',
      'Small segment samples are unstable and must not be promoted to strategy rules.',
      'The second-half split is an exploratory OOS check, not a formal walk-forward validation.',
      'This report does not activate, optimize, or modify any trading rule.',
    ],
  };
  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(reportOut, null, 2));
  console.log(`${timeframe}: trades=${rows.length} OOS=${oos.length}`);
  for (const [segment, value] of Object.entries(reportOut.fullSample.byDirectionAndSession)) {
    console.log(`  ${segment}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} totalR=${value.totalR.toFixed(4)}`);
  }
  console.log('  Ratio bands by direction/session:');
  for (const [segment, value] of Object.entries(reportOut.fullSample.byDirectionSessionRatio)) {
    for (const [ratio, s] of Object.entries(value.byRatioBand)) {
      console.log(`    ${segment} ${ratio}: n=${s.trades} PF=${s.PF?.toFixed(4) ?? 'n/a'} avgR=${s.avgR.toFixed(4)} totalR=${s.totalR.toFixed(4)}`);
    }
  }
  console.log('  OOS direction/session:');
  for (const [segment, value] of Object.entries(reportOut.oosSecondHalf.byDirectionAndSession)) {
    console.log(`    ${segment}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} totalR=${value.totalR.toFixed(4)}`);
  }
  console.log(`Report -> ${out}`);
}

await analyze('1min');
await analyze('5min');
