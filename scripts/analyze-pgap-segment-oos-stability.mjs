import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-candidate-quality');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-segment-oos-stability');

const BANDS = [
  { name: 'LT_0.02', min: -Infinity, max: 0.02 },
  { name: '0.02_0.05', min: 0.02, max: 0.05 },
  { name: '0.05_0.10', min: 0.05, max: 0.10 },
  { name: '0.10_0.20', min: 0.10, max: 0.20 },
  { name: '0.20_0.40', min: 0.20, max: 0.40 },
  { name: 'GE_0.40', min: 0.40, max: Infinity },
];

function band(value) {
  if (!Number.isFinite(value)) return 'NA';
  return BANDS.find(b => value >= b.min && value < b.max)?.name ?? 'NA';
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
  };
}

function sortChronological(rows) {
  return [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)));
}

function halves(rows) {
  const sorted = sortChronological(rows);
  const cut = Math.floor(sorted.length / 2);
  return { first: sorted.slice(0, cut), second: sorted.slice(cut) };
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

function candidateRows(rows) {
  return rows.filter(r => Number.isFinite(r.pgap?.maxGapToSpike));
}

function segmentRows(rows) {
  const result = {};
  for (const direction of ['BUY', 'SELL']) {
    for (const session of ['LONDON_ONLY', 'OVERLAP', 'NEW_YORK_ONLY', 'OUTSIDE']) {
      for (const ratioBand of BANDS.map(b => b.name)) {
        const subset = rows.filter(r =>
          r.direction === direction &&
          r.session === session &&
          band(Number(r.pgap?.maxGapToSpike)) === ratioBand,
        );
        if (subset.length) result[`${direction}__${session}__${ratioBand}`] = subset;
      }
    }
  }
  return result;
}

function stability(first, second) {
  const a = stats(first);
  const b = stats(second);
  const sameSign = (a.avgR === 0 || b.avgR === 0) ? a.avgR === b.avgR : Math.sign(a.avgR) === Math.sign(b.avgR);
  const positiveBoth = a.avgR > 0 && b.avgR > 0;
  const pfPositiveBoth = (a.PF ?? 0) > 1 && (b.PF ?? 0) > 1;
  return {
    firstHalf: a,
    secondHalf: b,
    sameAvgRSign: sameSign,
    positiveAvgRBothHalves: positiveBoth,
    PFAbove1BothHalves: pfPositiveBoth,
    qualifiesForFollowUp: first.length >= 20 && second.length >= 20 && positiveBoth,
  };
}

async function analyze(timeframe) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const rows = (report.trades ?? []).filter(r => Number.isFinite(r.rMultiple));
  const candidate = candidateRows(rows);
  const segments = segmentRows(candidate);
  const results = {};

  for (const [name, subset] of Object.entries(segments)) {
    const { first, second } = halves(subset);
    results[name] = stability(first, second);
  }

  const allHalves = halves(candidate);
  const reportOut = {
    strategy: 'Strategy A / SP2L',
    timeframe,
    sourceReport: `data/reports/strategy-a-pgap-candidate-quality/${timeframe}.json`,
    purpose: 'OOS stability screen for P-GAP ratio × direction × session interactions. Diagnostic only; no rule activation.',
    sample: {
      matchedTrades: rows.length,
      candidateTrades: candidate.length,
      firstHalfTrades: allHalves.first.length,
      secondHalfTrades: allHalves.second.length,
      candidateRatioDistribution: grouped(candidate, r => band(Number(r.pgap?.maxGapToSpike))),
    },
    candidateBaseline: stability(allHalves.first, allHalves.second),
    segments: results,
    followUpCandidates: Object.entries(results)
      .filter(([, s]) => s.qualifiesForFollowUp)
      .map(([segment, s]) => ({
        segment,
        firstHalf: s.firstHalf,
        secondHalf: s.secondHalf,
        reason: '>=20 trades in each half and positive average R in both halves',
      }))
      .sort((a, b) => b.secondHalf.avgR - a.secondHalf.avgR),
    researchWarnings: [
      'This is a stability screen, not a formal statistical validation.',
      'No segment is promoted solely from this report.',
      'PF and average R are both reported because PF can be dominated by a small number of outliers.',
      'The >=20 trades per half threshold is a research minimum, not a claim of statistical sufficiency.',
      'P-GAP remains a heuristic candidate feature until its market-structure definition is independently validated.',
    ],
  };

  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(reportOut, null, 2));

  console.log(`${timeframe}: matched=${rows.length} candidate=${candidate.length}`);
  console.log(`  firstHalf=${allHalves.first.length} secondHalf=${allHalves.second.length}`);
  console.log('  stable follow-up candidates:');
  if (!reportOut.followUpCandidates.length) {
    console.log('    NONE');
  } else {
    for (const c of reportOut.followUpCandidates) {
      console.log(`    ${c.segment}: S1 n=${c.firstHalf.trades} avgR=${c.firstHalf.avgR.toFixed(4)} PF=${c.firstHalf.PF?.toFixed(4) ?? 'n/a'} | S2 n=${c.secondHalf.trades} avgR=${c.secondHalf.avgR.toFixed(4)} PF=${c.secondHalf.PF?.toFixed(4) ?? 'n/a'}`);
    }
  }
  console.log(`Report -> ${out}`);
}

await analyze('1min');
await analyze('5min');
