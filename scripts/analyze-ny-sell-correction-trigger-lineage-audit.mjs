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
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-correction-trigger-lineage-audit');
const DEV = 6000;
const PRE = 10000;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(4)) : null;

function utcMinutes(ts) { const d = new Date(ts); return d.getUTCHours() * 60 + d.getUTCMinutes(); }
function isNySell(ts) { const m = utcMinutes(ts); return m >= 16 * 60 && m < 22 * 60; }

function replayAt(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const followThrough = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, followThrough, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });

  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const ft = followThrough.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !ft || ft.followThroughIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !isNySell(trigger.timestamp)) continue;
    return { spike, breakout, followThrough: ft, correction, trigger, visible };
  }
  return null;
}

function pathStats(visible, start, end) {
  if (start > end) return { n: 0, first: null, last: null, maxHigh: null, minLow: null };
  const xs = visible.slice(start, end + 1);
  return { n: xs.length, first: xs[0]?.timestamp ?? null, last: xs.at(-1)?.timestamp ?? null, maxHigh: xs.length ? Math.max(...xs.map((c) => c.high)) : null, minLow: xs.length ? Math.min(...xs.map((c) => c.low)) : null };
}

function flags(row) {
  const out = [];
  if (row.correctionBars > 100) out.push('LONG_CORRECTION_LINEAGE');
  if (row.entryDelay > 20) out.push('LONG_TRIGGER_DELAY');
  if (row.correctionCrossesSpikeStart) out.push('CORRECTION_REACHES_SPIKE_START');
  return out;
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const targets = (base.trades ?? []).map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex >= 0 && t.entryIndex < PRE && t.direction === 'SELL' && isNySell(t.entryTime) && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r))
    .sort((a, b) => a.entryIndex - b.entryIndex);

  const rows = targets.map((target) => {
    const replay = replayAt(candles, target.entryIndex);
    if (!replay) throw new Error(`Could not rebuild canonical NY SELL at ${target.entryIndex}`);
    if (replay.trigger.timestamp !== target.entryTime) throw new Error(`Lineage mismatch at ${target.entryIndex}: baseline=${target.entryTime} rebuilt=${replay.trigger.timestamp}`);
    const { spike, breakout, followThrough, correction, trigger, visible } = replay;
    const correctionBars = correction.correctionExtremeIndex - correction.correctionStartIndex + 1;
    const entryDelay = target.entryIndex - correction.correctionExtremeIndex;
    const path = pathStats(visible, correction.correctionStartIndex, correction.correctionExtremeIndex);
    const correctionCrossesSpikeStart = spike.direction === 'BEARISH' ? path.maxHigh > spike.startPrice : path.minLow < spike.startPrice;
    const row = {
      split: target.entryIndex < DEV ? 'DEV' : 'VAL', entryIndex: target.entryIndex, entryTime: target.entryTime, r: target.r,
      breakoutTime: breakout.timestamp, spikeStartTime: visible[spike.startIndex]?.timestamp ?? null, spikeEndTime: visible[spike.endIndex]?.timestamp ?? null,
      followThroughTime: visible[followThrough.followThroughIndex]?.timestamp ?? null,
      correctionStartTime: visible[correction.correctionStartIndex]?.timestamp ?? null,
      correctionExtremeTime: visible[correction.correctionExtremeIndex]?.timestamp ?? null,
      correctionBars, correctionCrossesSpikeStart, triggerTime: trigger.timestamp, entryDelay,
      correctionPathMaxHigh: path.maxHigh, correctionPathMinLow: path.minLow,
    };
    row.diagnosticFlags = flags(row);
    return row;
  });

  const correctionBars = rows.map((x) => x.correctionBars).sort((a, b) => a - b);
  const delays = rows.map((x) => x.entryDelay).sort((a, b) => a - b);
  const median = (xs) => xs[Math.floor(xs.length / 2)] ?? null;
  const summary = {
    total: rows.length, dev: rows.filter((x) => x.split === 'DEV').length, val: rows.filter((x) => x.split === 'VAL').length,
    correctionBarsMedian: median(correctionBars), correctionBarsMax: Math.max(...correctionBars), correctionBarsGt100: rows.filter((x) => x.correctionBars > 100).length,
    entryDelayMedian: median(delays), entryDelayMax: Math.max(...delays), entryDelayGt20: rows.filter((x) => x.entryDelay > 20).length,
    correctionCrossesSpikeStart: rows.filter((x) => x.correctionCrossesSpikeStart).length, flagged: rows.filter((x) => x.diagnosticFlags.length).length,
  };

  const output = { strategy: 'Strategy A / SP2L', mode: 'RESEARCH_NY_SELL_CORRECTION_TRIGGER_LINEAGE_AUDIT', timeframe: '5m', scope: { source: 'canonical baseline NY SELL trades before fresh holdout', ...summary, freshHoldoutExcluded: true, productionUntouched: true }, methodology: { purpose: 'Audit whether correction/trigger lineage keeps an old setup alive unusually long.', noOptimization: true, noNewTradingRules: true, noDetectorChanges: true, diagnosticThresholdsOnly: { correctionBarsGt100: true, entryDelayGt20: true }, lineageCheck: 'rebuilt trigger timestamp must equal canonical baseline entry timestamp' }, summary, cases: rows };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(output, null, 2));

  console.log('');
  console.log('════════════════════════════════════════════════════════════');
  console.log('NY SELL — CORRECTION / TRIGGER LINEAGE AUDIT');
  console.log('════════════════════════════════════════════════════════════');
  console.log(`Universe: ${summary.total} canonical NY SELL | DEV=${summary.dev} | VAL=${summary.val} | Fresh=LOCKED`);
  console.log('');
  console.log('LINEAGE SUMMARY');
  console.table({ correctionBarsMedian: summary.correctionBarsMedian, correctionBarsMax: summary.correctionBarsMax, correctionBarsGt100: summary.correctionBarsGt100, entryDelayMedian: summary.entryDelayMedian, entryDelayMax: summary.entryDelayMax, entryDelayGt20: summary.entryDelayGt20, correctionCrossesSpikeStart: summary.correctionCrossesSpikeStart, flaggedCases: summary.flagged });
  console.log('');
  console.log('FLAGGED CASES — DIAGNOSTIC ONLY');
  console.table(rows.filter((x) => x.diagnosticFlags.length).map((x) => ({ split: x.split, time: x.entryTime, R: p(x.r), corrBars: x.correctionBars, delay: x.entryDelay, spikeStart: x.spikeStartTime, correctionStart: x.correctionStartTime, correctionExtreme: x.correctionExtremeTime, trigger: x.triggerTime, flags: x.diagnosticFlags.join(',') })));
  console.log('');
  console.log('ALL CASES — COMPACT LINEAGE');
  console.table(rows.map((x) => ({ split: x.split, time: x.entryTime, R: p(x.r), spikeEnd: x.spikeEndTime, ft: x.followThroughTime, corrStart: x.correctionStartTime, corrExtreme: x.correctionExtremeTime, corrBars: x.correctionBars, trigger: x.triggerTime, delay: x.entryDelay })));
  console.log('');
  console.log(`Full machine-readable report -> ${resolve(OUT, '5m.json')}`);
  console.log('No optimization, no new rules, no Fresh Holdout access.');
}

await main();
