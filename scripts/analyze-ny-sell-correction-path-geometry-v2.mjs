import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-correction-path-geometry-v2');
const DEV = 6000;
const PRE = 10000;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(5)) : null;
const utcMinutes = (ts) => { const d = new Date(ts); return d.getUTCHours() * 60 + d.getUTCMinutes(); };
const isNySell = (ts) => { const m = utcMinutes(ts); return m >= 960 && m < 1320; };

function replayAt(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !isNySell(trigger.timestamp)) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const followThrough = ft.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !followThrough) continue;
    return { visible, spike, breakout, followThrough, correction, trigger };
  }
  return null;
}

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => { const pos = (a.length - 1) * f; const lo = Math.floor(pos); const hi = Math.ceil(pos); return p(a[lo] + (a[hi] - a[lo]) * (pos - lo)); };
  return { n: a.length, p25: q(.25), median: q(.5), p75: q(.75), min: p(a[0]), max: p(a.at(-1)) };
}

function bucketRows(rows, feature) {
  const sorted = rows.slice().sort((a, b) => a[feature] - b[feature]);
  const groups = ['Q1', 'Q2', 'Q3', 'Q4'];
  return Object.fromEntries(groups.map((g, i) => {
    const start = Math.floor(i * sorted.length / 4);
    const end = Math.floor((i + 1) * sorted.length / 4);
    const xs = sorted.slice(start, end);
    const wins = xs.filter((x) => x.r > 0);
    const grossWin = wins.reduce((s, x) => s + x.r, 0);
    const grossLoss = xs.filter((x) => x.r <= 0).reduce((s, x) => s + Math.abs(x.r), 0);
    return [g, { n: xs.length, WR: xs.length ? wins.length / xs.length : null, avgR: xs.length ? xs.reduce((s, x) => s + x.r, 0) / xs.length : null, PF: grossLoss ? grossWin / grossLoss : null, totalR: xs.reduce((s, x) => s + x.r, 0), featureMedian: quantiles(xs.map((x) => x[feature])).median }];
  }));
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const targets = (base.trades ?? []).map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex < PRE && t.direction === 'SELL' && isNySell(t.entryTime) && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r));
  const rows = targets.map((t) => {
    const x = replayAt(candles, t.entryIndex);
    if (!x || x.trigger.timestamp !== t.entryTime) throw new Error(`Lineage mismatch at ${t.entryIndex}`);
    const { visible, spike, correction, trigger } = x;
    const corr = visible.slice(correction.correctionStartIndex, correction.correctionExtremeIndex + 1);
    const triggerCandle = visible[t.entryIndex];
    const maxHigh = Math.max(...corr.map((c) => c.high));
    const minLow = Math.min(...corr.map((c) => c.low));
    const correctionSize = Math.max(0, correction.extremePrice - spike.endPrice);
    const spikeSize = Math.abs(spike.size);
    const adverseBeforeTrigger = Math.max(0, maxHigh - spike.endPrice);
    const reclaimFromExtreme = Math.max(0, correction.extremePrice - trigger.entryPrice);
    const triggerBody = Math.abs(triggerCandle.close - triggerCandle.open);
    const triggerRange = triggerCandle.high - triggerCandle.low;
    const triggerCloseLocation = triggerRange > 0 ? (triggerCandle.close - triggerCandle.low) / triggerRange : null;
    return {
      split: t.entryIndex < DEV ? 'DEV' : 'VAL', time: t.entryTime, r: t.r,
      correctionBars: correction.correctionExtremeIndex - correction.correctionStartIndex + 1,
      correctionSize, correctionToSpike: spikeSize > 0 ? correctionSize / spikeSize : null,
      adverseBeforeTrigger, adverseToSpike: spikeSize > 0 ? adverseBeforeTrigger / spikeSize : null,
      reclaimFromExtreme, reclaimToCorrection: correctionSize > 0 ? reclaimFromExtreme / correctionSize : null,
      triggerBody, triggerRange, triggerBodyToRange: triggerRange > 0 ? triggerBody / triggerRange : null,
      triggerCloseLocation,
      correctionNetDirection: correction.extremePrice - spike.endPrice,
      triggerIndex: t.entryIndex,
      spikeSize,
    };
  });

  const FEATURES = ['correctionBars', 'correctionToSpike', 'adverseToSpike', 'reclaimToCorrection', 'triggerBodyToRange', 'triggerCloseLocation'];
  const summary = { total: rows.length, dev: rows.filter((x) => x.split === 'DEV').length, val: rows.filter((x) => x.split === 'VAL').length };
  const result = { strategy: 'Strategy A / SP2L', mode: 'RESEARCH_NY_SELL_CORRECTION_PATH_GEOMETRY_V2', timeframe: '5m', scope: { ...summary, freshHoldoutExcluded: true, productionUntouched: true }, methodology: { purpose: 'Descriptive analysis of correction path, reclaim geometry and trigger-candle impulse for canonical NY SELL.', noOptimization: true, noNewTradingRules: true, noThresholdSearch: true, holdoutLocked: true }, featureDistributions: Object.fromEntries(FEATURES.map((f) => [f, { ALL: quantiles(rows.map((x) => x[f])), DEV: quantiles(rows.filter((x) => x.split === 'DEV').map((x) => x[f])), VAL: quantiles(rows.filter((x) => x.split === 'VAL').map((x) => x[f])) }])), buckets: Object.fromEntries(FEATURES.map((f) => [f, { ALL: bucketRows(rows, f), DEV: bucketRows(rows.filter((x) => x.split === 'DEV'), f), VAL: bucketRows(rows.filter((x) => x.split === 'VAL'), f) }])), cases: rows };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));
  console.log('');
  console.log('════════════════════════════════════════════════════════════');
  console.log('NY SELL — CORRECTION PATH / RECLAIM / TRIGGER GEOMETRY V2');
  console.log('════════════════════════════════════════════════════════════');
  console.log(`Universe: ${summary.total} canonical NY SELL | DEV=${summary.dev} | VAL=${summary.val} | Fresh=LOCKED`);
  console.log('Feature medians:');
  console.table(Object.fromEntries(FEATURES.map((f) => [f, { ALL: result.featureDistributions[f].ALL.median, DEV: result.featureDistributions[f].DEV.median, VAL: result.featureDistributions[f].VAL.median }])));
  for (const f of FEATURES) { console.log(`\n${f} — ALL Q1-Q4`); console.table(result.buckets[f].ALL); console.log(`${f} — DEV Q1-Q4`); console.table(result.buckets[f].DEV); console.log(`${f} — VAL Q1-Q4`); console.table(result.buckets[f].VAL); }
  console.log('\nCase rows:');
  console.table(rows.map((x) => ({ split: x.split, time: x.time, R: p(x.r), corrBars: x.correctionBars, corrToSpike: p(x.correctionToSpike), adverseToSpike: p(x.adverseToSpike), reclaimToCorr: p(x.reclaimToCorrection), bodyToRange: p(x.triggerBodyToRange), closeLoc: p(x.triggerCloseLocation) })));
  console.log(`\nFull report -> ${resolve(OUT, '5m.json')}`);
  console.log('No optimization, no new rules, no Fresh Holdout access.');
}

await main();
