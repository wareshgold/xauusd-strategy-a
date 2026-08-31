import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-trade-forensics');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-pgap-candidate-quality');
const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 7 * 60, endMinutes: 16 * 60 },
    { name: 'NEW_YORK', startMinutes: 13 * 60, endMinutes: 22 * 60 },
  ],
  avoidWindows: [],
};

async function loadModule(file) {
  return import(pathToFileURL(resolve(ROOT, file)).href);
}

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
  return {
    trades: closed.length,
    wins: wins.length,
    losses: losses.length,
    winRate: closed.length ? wins.length / closed.length : 0,
    avgR: closed.length ? rs.reduce((s, r) => s + r, 0) / closed.length : 0,
    totalR: rs.reduce((s, r) => s + r, 0),
    PF: grossLoss ? grossWin / grossLoss : null,
    medianR: percentile(rs, 0.5),
    medianMFE: percentile(closed.map(t => t.mfeR), 0.5),
    medianMAE: percentile(closed.map(t => t.maeR), 0.5),
  };
}

function band(value, edges) {
  if (!Number.isFinite(value)) return 'NA';
  for (const edge of edges) if (value < edge) return `<${edge}`;
  return `>=${edges.at(-1)}`;
}

function group(rows, keyFn) {
  const map = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return Object.fromEntries([...map].map(([k, v]) => [k, stats(v)]));
}

async function loadDataset(timeframe) {
  return JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
}

function candidateMetrics(observations, entry, spikeSize) {
  const candidates = observations.filter(x => x.classification === 'CANDIDATE');
  const sizes = candidates.map(x => x.size).filter(Number.isFinite);
  const entryPrice = entry.entry;
  const distance = candidates.map(x => Math.abs(entryPrice - ((x.upper + x.lower) / 2))).filter(Number.isFinite);
  return {
    candidateCount: candidates.length,
    hasCandidate: candidates.length > 0,
    totalGapSize: sizes.reduce((s, x) => s + x, 0),
    maxGapSize: sizes.length ? Math.max(...sizes) : 0,
    medianGapSize: percentile(sizes, 0.5),
    maxGapToSpike: spikeSize > 0 && sizes.length ? Math.max(...sizes) / spikeSize : null,
    maxGapToEntryDistance: sizes.length && distance.length ? Math.min(...distance) / Math.max(sizes) : null,
  };
}

async function analyze(timeframe, modules) {
  const dataset = await loadDataset(timeframe);
  const candles = dataset.candles;
  const tradeReport = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const trades = (tradeReport.trades ?? []).filter(t => Number.isFinite(t.rMultiple));
  const tradeByKey = new Map(trades.map(t => [`${t.entryIndex}:${t.direction}`, t]));
  const unique = new Map();

  for (let eventIndex = 0; eventIndex < candles.length; eventIndex += 1) {
    if (eventIndex < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) continue;
    const visible = candles.slice(0, eventIndex + 1);
    const breakouts = modules.detectBreakout(visible, BREAKOUT_LOOKBACK);
    const followThrough = modules.detectFollowThrough(visible, breakouts, {
      maxBarsAfterBreakout: FT_MAX_BARS,
      requireCloseBeyondBrokenLevel: true,
    });
    const spikes = modules.detectSpikeCandidates(visible, breakouts, followThrough, {
      maxCandles: SPIKE_MAX_CANDLES,
      minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
      maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
    });

    for (const spike of spikes.candidates) {
      if (spike.endIndex >= eventIndex) continue;
      const correction = modules.detectFirstCorrection(visible, spike);
      if (!correction || correction.correctionExtremeIndex >= eventIndex) continue;
      const trigger = modules.detectEntryTrigger(visible, correction);
      if (!trigger || trigger.index !== eventIndex) continue;
      const projection = modules.projectLeg2(visible, correction);
      if (!projection) continue;
      const ema = modules.buildEMAContext(visible.map(c => c.close), CONTEXT);
      if (!ema) continue;
      const location = modules.buildLocationContext(trigger.entryPrice, CONTEXT);
      const session = modules.buildSessionContext(trigger.timestamp, CONTEXT);
      const quality = modules.scoreSetup(spike, { ema, location, session });
      if (!quality.tradeAllowed) continue;
      const key = `${trigger.index}:${trigger.direction}`;
      if (unique.has(key)) continue;

      const observations = modules.collectPGAPObservations(visible, spike);
      const trade = tradeByKey.get(key);
      if (!trade) continue;
      unique.set(key, {
        ...trade,
        pgap: candidateMetrics(observations, trade, spike.size),
        spikeSize: spike.size,
        spikeStartIndex: spike.startIndex,
        spikeEndIndex: spike.endIndex,
      });
    }
  }

  const rows = [...unique.values()];
  const candidateRows = rows.filter(r => r.pgap.hasCandidate);
  const noCandidateRows = rows.filter(r => !r.pgap.hasCandidate);
  const report = {
    strategy: 'Strategy A / SP2L',
    timeframe,
    symbol: dataset.symbol,
    source: dataset.source,
    baseline: stats(rows),
    coverage: {
      matchedTrades: rows.length,
      withPGAPCandidate: candidateRows.length,
      withoutPGAPCandidate: noCandidateRows.length,
      candidateRate: rows.length ? candidateRows.length / rows.length : 0,
    },
    byCandidatePresence: {
      PGAP_CANDIDATE_YES: stats(candidateRows),
      PGAP_CANDIDATE_NO: stats(noCandidateRows),
    },
    byCandidateCount: group(rows, r => band(r.pgap.candidateCount, [1, 2, 3, 5])),
    byMaxGapToSpike: group(rows, r => band(r.pgap.maxGapToSpike, [0.05, 0.1, 0.25, 0.5, 1])),
    byMaxGapSize: group(rows, r => band(r.pgap.maxGapSize, [0.25, 0.5, 1, 2, 5])),
    byDirectionAndCandidate: group(rows, r => `${r.direction}__${r.pgap.hasCandidate ? 'YES' : 'NO'}`),
    bySessionAndCandidate: group(rows, r => `${r.session}__${r.pgap.hasCandidate ? 'YES' : 'NO'}`),
    distributions: {
      candidateCount: {
        p25: percentile(rows.map(r => r.pgap.candidateCount), .25),
        p50: percentile(rows.map(r => r.pgap.candidateCount), .5),
        p75: percentile(rows.map(r => r.pgap.candidateCount), .75),
        p90: percentile(rows.map(r => r.pgap.candidateCount), .9),
      },
      maxGapToSpike: {
        p25: percentile(rows.map(r => r.pgap.maxGapToSpike), .25),
        p50: percentile(rows.map(r => r.pgap.maxGapToSpike), .5),
        p75: percentile(rows.map(r => r.pgap.maxGapToSpike), .75),
        p90: percentile(rows.map(r => r.pgap.maxGapToSpike), .9),
      },
      maxGapSize: {
        p25: percentile(rows.map(r => r.pgap.maxGapSize), .25),
        p50: percentile(rows.map(r => r.pgap.maxGapSize), .5),
        p75: percentile(rows.map(r => r.pgap.maxGapSize), .75),
        p90: percentile(rows.map(r => r.pgap.maxGapSize), .9),
      },
    },
    researchWarnings: [
      'These are heuristic three-candle imbalance candidates, not validated P-GAPs.',
      'No candidate threshold is promoted to a trading rule by this report.',
      'Candidate presence is evaluated only from information visible at entry; post-entry outcome fields are used only for diagnostics.',
      rows.length !== trades.length ? `Only ${rows.length} of ${trades.length} forensic trades matched the deterministic structural replay; unmatched trades are excluded from candidate/outcome comparisons.` : null,
    ].filter(Boolean),
    researchNote: 'Diagnostic only. The purpose is to test whether pre-entry P-GAP candidate evidence separates outcomes before any P-GAP definition or gate is activated.',
  };

  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: matched=${rows.length} candidateYes=${candidateRows.length} candidateNo=${noCandidateRows.length}`);
  console.log(`  YES PF=${stats(candidateRows).PF?.toFixed(4) ?? 'n/a'} avgR=${stats(candidateRows).avgR.toFixed(4)} | NO PF=${stats(noCandidateRows).PF?.toFixed(4) ?? 'n/a'} avgR=${stats(noCandidateRows).avgR.toFixed(4)}`);
  console.log(`  maxGap/spike P50=${report.distributions.maxGapToSpike.p50 ?? 'n/a'} P90=${report.distributions.maxGapToSpike.p90 ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

const modules = {
  detectBreakout: (await loadModule('src/domain/market/BreakoutDetector.ts')).detectBreakout,
  detectFollowThrough: (await loadModule('src/domain/market/FollowThroughDetector.ts')).detectFollowThrough,
  detectSpikeCandidates: (await loadModule('src/domain/strategy-a/SpikeDetector.ts')).detectSpikeCandidates,
  detectFirstCorrection: (await loadModule('src/domain/strategy-a/CorrectionDetector.ts')).detectFirstCorrection,
  detectEntryTrigger: (await loadModule('src/domain/strategy-a/EntryTrigger.ts')).detectEntryTrigger,
  projectLeg2: (await loadModule('src/domain/strategy-a/LegProjection.ts')).projectLeg2,
  collectPGAPObservations: (await loadModule('src/domain/strategy-a/PGAPResearch.ts')).collectPGAPObservations,
  buildEMAContext: (await loadModule('src/domain/strategy-a/Context.ts')).buildEMAContext,
  buildLocationContext: (await loadModule('src/domain/strategy-a/Context.ts')).buildLocationContext,
  buildSessionContext: (await loadModule('src/domain/strategy-a/Context.ts')).buildSessionContext,
  scoreSetup: (await loadModule('src/domain/strategy-a/QualityScore.ts')).scoreSetup,
};

await analyze('1min', modules);
await analyze('5min', modules);
