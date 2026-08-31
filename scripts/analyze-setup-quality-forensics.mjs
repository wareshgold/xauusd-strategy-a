import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-trade-forensics');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-setup-quality-forensics');

function percentile(values, p) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const i = (a.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (i - lo);
}

function stats(rows) {
  const closed = rows.filter(t => Number.isFinite(t.rMultiple));
  const wins = closed.filter(t => t.rMultiple > 0);
  const losses = closed.filter(t => t.rMultiple < 0);
  const grossWin = wins.reduce((s, t) => s + t.rMultiple, 0);
  const grossLoss = Math.abs(losses.reduce((s, t) => s + t.rMultiple, 0));
  const rs = closed.map(t => t.rMultiple);
  const p99 = percentile(rs, 0.99);
  const robust = p99 == null ? [] : closed.filter(t => t.rMultiple <= p99);
  const robustWins = robust.filter(t => t.rMultiple > 0).reduce((s, t) => s + t.rMultiple, 0);
  const robustLosses = Math.abs(robust.filter(t => t.rMultiple < 0).reduce((s, t) => s + t.rMultiple, 0));
  return {
    trades: closed.length,
    wins: wins.length,
    losses: losses.length,
    winRate: closed.length ? wins.length / closed.length : 0,
    avgR: closed.length ? rs.reduce((s, r) => s + r, 0) / closed.length : 0,
    totalR: rs.reduce((s, r) => s + r, 0),
    PF: grossLoss ? grossWin / grossLoss : null,
    medianR: percentile(rs, 0.5),
    robustPF: robustLosses ? robustWins / robustLosses : null,
    robustAvgR: robust.length ? robust.reduce((s, t) => s + t.rMultiple, 0) / robust.length : null,
    excludedTop1Pct: closed.length - robust.length
  };
}

function bucketNumber(value, edges) {
  if (!Number.isFinite(value)) return 'NA';
  for (let i = 0; i < edges.length; i++) if (value < edges[i]) return `<${edges[i]}`;
  return `>=${edges.at(-1)}`;
}

function group(rows, keyFn) {
  const m = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!m.has(key)) m.set(key, []);
    m.get(key).push(row);
  }
  return Object.fromEntries([...m].map(([k, v]) => [k, stats(v)]));
}

function ratio(t) {
  return Number.isFinite(t.correctionSize) && Number.isFinite(t.spikeSize) && t.spikeSize > 0
    ? t.correctionSize / t.spikeSize
    : null;
}

function analyze(report) {
  const trades = (report.trades ?? []).filter(t => Number.isFinite(t.rMultiple));
  const numericFields = ['spikeSize', 'spikeStructureScore', 'spikeOverlapScore', 'correctionSize', 'leg1Size', 'targetR', 'qualityScore', 'mfeR', 'maeR', 'barsToExit'];
  const fieldCoverage = Object.fromEntries(numericFields.map(k => [k, {
    present: trades.filter(t => Number.isFinite(t[k])).length,
    missing: trades.filter(t => !Number.isFinite(t[k])).length
  }]));

  const qualityValues = trades.map(t => t.qualityScore).filter(Number.isFinite);
  const structureValues = trades.map(t => t.spikeStructureScore).filter(Number.isFinite);
  const overlapValues = trades.map(t => t.spikeOverlapScore).filter(Number.isFinite);

  return {
    timeframe: report.timeframe,
    trades: trades.length,
    baseline: stats(trades),
    fieldCoverage,
    distributions: {
      qualityScore: { min: Math.min(...qualityValues), p25: percentile(qualityValues, .25), p50: percentile(qualityValues, .5), p75: percentile(qualityValues, .75), max: Math.max(...qualityValues), unique: [...new Set(qualityValues)].sort((a,b)=>a-b) },
      spikeStructureScore: { min: Math.min(...structureValues), p25: percentile(structureValues, .25), p50: percentile(structureValues, .5), p75: percentile(structureValues, .75), max: Math.max(...structureValues), unique: [...new Set(structureValues)].sort((a,b)=>a-b) },
      spikeOverlapScore: { min: Math.min(...overlapValues), p25: percentile(overlapValues, .25), p50: percentile(overlapValues, .5), p75: percentile(overlapValues, .75), max: Math.max(...overlapValues) },
      spikeSize: { p25: percentile(trades.map(t=>t.spikeSize), .25), p50: percentile(trades.map(t=>t.spikeSize), .5), p75: percentile(trades.map(t=>t.spikeSize), .75), p90: percentile(trades.map(t=>t.spikeSize), .9) },
      correctionToSpike: { p25: percentile(trades.map(ratio).filter(Number.isFinite), .25), p50: percentile(trades.map(ratio).filter(Number.isFinite), .5), p75: percentile(trades.map(ratio).filter(Number.isFinite), .75), p90: percentile(trades.map(ratio).filter(Number.isFinite), .9) },
      targetR: { p25: percentile(trades.map(t=>t.targetR), .25), p50: percentile(trades.map(t=>t.targetR), .5), p75: percentile(trades.map(t=>t.targetR), .75), p90: percentile(trades.map(t=>t.targetR), .9) }
    },
    byQualityScore: group(trades, t => Number.isFinite(t.qualityScore) ? String(t.qualityScore) : 'NA'),
    byStructureScore: group(trades, t => Number.isFinite(t.spikeStructureScore) ? String(t.spikeStructureScore) : 'NA'),
    byPGAP: group(trades, t => t.spikeHasPGAPEvidence ? 'PGAP_YES' : 'PGAP_NO'),
    byDirection: group(trades, t => t.direction),
    byOverlapBand: group(trades, t => bucketNumber(t.spikeOverlapScore, [0.25, 0.5, 0.75, 1.0])),
    byTargetRBand: group(trades, t => bucketNumber(t.targetR, [1, 2, 3, 5, 10])),
    byCorrectionToSpikeBand: group(trades, t => bucketNumber(ratio(t), [0.5, 0.75, 1, 1.25, 1.5, 2])),
    byMFEAtOutcome: group(trades, t => bucketNumber(t.mfeR, [0.25, 0.5, 1, 2, 5, 10])),
    researchWarnings: [
      qualityValues.length && new Set(qualityValues).size === 1 ? 'qualityScore has only one observed value; current quality scoring is not discriminating setups.' : null,
      structureValues.length && new Set(structureValues).size === 1 ? 'spikeStructureScore has only one observed value; structure scoring is not discriminating setups.' : null,
      trades.every(t => t.spikeHasPGAPEvidence === false) ? 'No trade has PGAP evidence; the baseline is not exercising the P-GAP gate.' : null,
      trades.filter(t => Number.isFinite(t.leg2ToLeg1Ratio)).length === 0 ? 'leg2ToLeg1Ratio is absent for all trades; 2L completion is not available for post-entry quality analysis.' : null
    ].filter(Boolean),
    researchNote: 'Diagnostic only. No thresholds, parameters, filters, entries, exits, or trading rules were changed. Buckets are descriptive and must not be promoted to rules without out-of-sample validation.'
  };
}

await mkdir(OUTPUT, { recursive: true });
for (const timeframe of ['1min', '5min']) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const result = analyze(report);
  await writeFile(resolve(OUTPUT, `${timeframe}.json`), JSON.stringify(result, null, 2));
  console.log(`${timeframe}: trades=${result.trades} PF=${result.baseline.PF?.toFixed(4) ?? 'n/a'} robustPF=${result.baseline.robustPF?.toFixed(4) ?? 'n/a'}`);
  console.log(`  quality unique=${result.distributions.qualityScore.unique.join(',')} structure unique=${result.distributions.spikeStructureScore.unique.join(',')}`);
  for (const [key, value] of Object.entries(result.byPGAP)) console.log(`  ${key}: n=${value.trades} PF=${value.PF?.toFixed(4) ?? 'n/a'} avgR=${value.avgR.toFixed(4)} robustPF=${value.robustPF?.toFixed(4) ?? 'n/a'}`);
  for (const warning of result.researchWarnings) console.log(`  WARNING: ${warning}`);
  console.log(`Report -> ${resolve(OUTPUT, `${timeframe}.json`)}`);
}
