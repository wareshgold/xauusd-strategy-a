import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-entry-trigger-mechanics-preholdout');
const TIMEFRAME = '5min';
const TOTAL_CANDLES = 15000;
const FRESH_HOLDOUT_CANDLES = 5000;
const PRE_HOLDOUT_CANDLES = TOTAL_CANDLES - FRESH_HOLDOUT_CANDLES;
const CFG = { breakoutLookback: 5, ftMaxBars: 2, spikeMaxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 };

const [Breakout, FT, Spike, Correction, Trigger] = await Promise.all([
  import('../src/domain/market/BreakoutDetector.ts'),
  import('../src/domain/market/FollowThroughDetector.ts'),
  import('../src/domain/strategy-a/SpikeDetector.ts'),
  import('../src/domain/strategy-a/CorrectionDetector.ts'),
  import('../src/domain/strategy-a/EntryTrigger.ts'),
]);

function finite(x) { return Number.isFinite(Number(x)); }
function mean(a) { return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null; }
function quantile(a, p) {
  const x = [...a].sort((m, n) => m - n);
  return x.length ? x[Math.floor((x.length - 1) * p)] : null;
}
function summarize(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0);
  const losses = rs.filter(r => r < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);
  return { n: rs.length, wins: wins.length, losses: losses.length, winRate: rs.length ? wins.length / rs.length : 0, PF: gl ? gp / gl : (gp ? null : 0), avgR: mean(rs), totalR };
}
function metricSummary(rows, key) {
  const vals = rows.map(r => Number(r[key])).filter(Number.isFinite);
  return { n: vals.length, mean: mean(vals), p25: quantile(vals, .25), median: quantile(vals, .5), p75: quantile(vals, .75), min: vals.length ? Math.min(...vals) : null, max: vals.length ? Math.max(...vals) : null };
}
function bucket(rows, ranges) {
  return Object.fromEntries(ranges.map(([label, test]) => [label, summarize(rows.filter(test))]));
}

async function reconstruct() {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${TIMEFRAME}.json`), 'utf8'));
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${TIMEFRAME}.json`), 'utf8'));
  const candles = raw.candles ?? [];
  if (candles.length < TOTAL_CANDLES) throw new Error(`expected ${TOTAL_CANDLES} candles, found ${candles.length}`);
  const cutoff = candles[PRE_HOLDOUT_CANDLES]?.timestamp;
  if (!cutoff) throw new Error('missing pre-holdout cutoff');

  const rows = [];
  for (const trade of baseline.trades ?? []) {
    if (!finite(trade.entryIndex) || !finite(trade.rMultiple) || trade.result === 'AMBIGUOUS') continue;
    const entryIndex = Number(trade.entryIndex);
    if (entryIndex >= PRE_HOLDOUT_CANDLES) continue;
    const visible = candles.slice(0, entryIndex + 1);
    const breakouts = Breakout.detectBreakout(visible, CFG.breakoutLookback).filter(b => b.index < entryIndex);
    const matches = [];

    for (const b of breakouts) {
      const ft = FT.detectFollowThrough(visible, [b], { maxBarsAfterBreakout: CFG.ftMaxBars, requireCloseBeyondBrokenLevel: true })[0];
      if (!ft) continue;
      const spike = Spike.detectSpikeCandidates(visible, [b], [ft], CFG).candidates.find(s => s.endIndex < entryIndex);
      if (!spike) continue;
      const correction = Correction.detectFirstCorrection(visible, spike);
      if (!correction || correction.correctionExtremeIndex >= entryIndex) continue;
      const trigger = Trigger.detectEntryTrigger(visible, correction);
      if (!trigger || trigger.index !== entryIndex) continue;
      if (trade.direction && trigger.direction !== trade.direction) continue;
      matches.push({ b, ft, spike, correction, trigger });
    }

    // A baseline trade must map to one deterministic reconstruction. Prefer the
    // latest matching structural chain, which is the most recent valid setup
    // visible at the actual entry bar. This avoids duplicating a trade when
    // older breakout chains also happen to reconstruct the same trigger.
    const matched = matches.at(-1);
    if (!matched) continue;

    const { spike, correction, trigger } = matched;
    const delayBars = entryIndex - correction.correctionExtremeIndex;
    const correctionDepthBars = correction.correctionExtremeIndex - correction.correctionStartIndex;
    const triggerDistance = trigger.direction === 'BUY'
      ? trigger.entryPrice - correction.extremePrice
      : correction.extremePrice - trigger.entryPrice;
    const triggerExtensionPctSpike = spike.size > 0 ? triggerDistance / spike.size : null;
    const correctionDepthPrice = trigger.direction === 'BUY'
      ? spike.startPrice - correction.extremePrice
      : correction.extremePrice - spike.startPrice;
    const correctionDepthPctSpike = spike.size > 0 ? correctionDepthPrice / spike.size : null;

    rows.push({
      entryIndex,
      entryTime: trade.entryTime,
      direction: trigger.direction,
      session: trade.session,
      result: trade.result,
      rMultiple: Number(trade.rMultiple),
      delayBars,
      correctionDepthBars,
      triggerDistance,
      triggerExtensionPctSpike,
      correctionDepthPctSpike,
      spikeSize: spike.size,
      structureScore: spike.structureScore,
      overlapScore: spike.overlapScore,
    });
  }
  return { rows, cutoff };
}

const { rows, cutoff } = await reconstruct();
const winners = rows.filter(r => r.rMultiple > 0);
const losers = rows.filter(r => r.rMultiple < 0);

const report = {
  strategy: 'Strategy A / SP2L',
  mode: 'RESEARCH_ENTRY_TRIGGER_MECHANICS_PREHOLDOUT_V2',
  timeframe: TIMEFRAME,
  scope: 'Diagnostic winner/loser analysis of actual baseline entries reconstructed from candles visible at each entry. Pre-holdout only; no holdout inspection, no rule changes, no threshold optimization.',
  methodology: {
    totalCandles: TOTAL_CANDLES,
    preHoldoutCandles: PRE_HOLDOUT_CANDLES,
    freshHoldoutCandles: FRESH_HOLDOUT_CANDLES,
    cutoff,
    triggerDefinition: 'First post-correction candle whose close reclaims the correction extreme.',
    delayDefinition: 'entryIndex - correctionExtremeIndex.',
    correctionDepthDefinition: 'correctionExtremeIndex - correctionStartIndex, measured in candles.',
    triggerExtensionDefinition: 'Directional distance from correction extreme to entry close, normalized by spike size.',
    correctionDepthPctSpikeDefinition: 'Directional price depth from spike start to correction extreme, normalized by spike size.',
    matchingRule: 'For each baseline entry, reconstruct all matching chains visible through the entry bar and use the latest matching structural chain; each baseline trade contributes at most one row.',
    fixedBuckets: 'Delay 0/1/2/3-5/6+; correction depth 1/2/3/4+; trigger extension <10%/10-25%/25-50%/>50% of spike size.',
  },
  coverage: { matchedBaselineTrades: rows.length, baselinePreHoldoutTrades: (await (async()=>JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${TIMEFRAME}.json`),'utf8')))()).trades.filter(t => finite(t.entryIndex) && finite(t.rMultiple) && t.result !== 'AMBIGUOUS' && Number(t.entryIndex) < PRE_HOLDOUT_CANDLES).length },
  overall: summarize(rows),
  winners: { count: winners.length, metrics: { delayBars: metricSummary(winners, 'delayBars'), correctionDepthBars: metricSummary(winners, 'correctionDepthBars'), triggerExtensionPctSpike: metricSummary(winners, 'triggerExtensionPctSpike'), correctionDepthPctSpike: metricSummary(winners, 'correctionDepthPctSpike'), spikeSize: metricSummary(winners, 'spikeSize') } },
  losers: { count: losers.length, metrics: { delayBars: metricSummary(losers, 'delayBars'), correctionDepthBars: metricSummary(losers, 'correctionDepthBars'), triggerExtensionPctSpike: metricSummary(losers, 'triggerExtensionPctSpike'), correctionDepthPctSpike: metricSummary(losers, 'correctionDepthPctSpike'), spikeSize: metricSummary(losers, 'spikeSize') } },
  byDelay: bucket(rows, [['0', r => r.delayBars === 0], ['1', r => r.delayBars === 1], ['2', r => r.delayBars === 2], ['3-5', r => r.delayBars >= 3 && r.delayBars <= 5], ['6+', r => r.delayBars >= 6]]),
  byCorrectionDepthBars: bucket(rows, [['0', r => r.correctionDepthBars === 0], ['1', r => r.correctionDepthBars === 1], ['2', r => r.correctionDepthBars === 2], ['3', r => r.correctionDepthBars === 3], ['4+', r => r.correctionDepthBars >= 4]]),
  byTriggerExtensionPctSpike: bucket(rows, [['<10%', r => r.triggerExtensionPctSpike < .10], ['10-25%', r => r.triggerExtensionPctSpike >= .10 && r.triggerExtensionPctSpike < .25], ['25-50%', r => r.triggerExtensionPctSpike >= .25 && r.triggerExtensionPctSpike < .50], ['>50%', r => r.triggerExtensionPctSpike >= .50]]),
  byDirection: { BUY: summarize(rows.filter(r => r.direction === 'BUY')), SELL: summarize(rows.filter(r => r.direction === 'SELL')) },
  rows,
  conclusion: 'Diagnostic only. Any apparent winner/loser separation must be tested as a frozen hypothesis on DEV/VAL before any production rule is considered. The fresh holdout remains untouched by this report.',
};

await mkdir(OUT, { recursive: true });
const out = resolve(OUT, `${TIMEFRAME}.json`);
await writeFile(out, JSON.stringify(report, null, 2));
console.log(`${TIMEFRAME}: matched=${rows.length} winners=${winners.length} losers=${losers.length} avgR=${report.overall.avgR?.toFixed(4) ?? 'n/a'} PF=${report.overall.PF?.toFixed(4) ?? 'n/a'}`);
console.log(`  coverage=${report.coverage.matchedBaselineTrades}/${report.coverage.baselinePreHoldoutTrades}`);
console.log(`  delay median winner=${report.winners.metrics.delayBars.median ?? 'n/a'} loser=${report.losers.metrics.delayBars.median ?? 'n/a'}`);
console.log(`  correctionDepth median winner=${report.winners.metrics.correctionDepthBars.median ?? 'n/a'} loser=${report.losers.metrics.correctionDepthBars.median ?? 'n/a'}`);
console.log(`  triggerExtension median winner=${report.winners.metrics.triggerExtensionPctSpike.median ?? 'n/a'} loser=${report.losers.metrics.triggerExtensionPctSpike.median ?? 'n/a'}`);
console.log(`Report -> ${out}`);
