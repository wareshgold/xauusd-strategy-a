import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');

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
    if (!trigger || trigger.index !== index) continue;
    if (trigger.direction !== (spike.direction === 'BULLISH' ? 'BUY' : 'SELL')) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const followThrough = ft.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !followThrough) continue;
    return { trigger, spike, correction, breakout, followThrough };
  }
  return null;
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const byTime = new Map(candles.map((c, i) => [c.timestamp, i]));
  const targets = (base.trades ?? []).filter((t) => t.result !== 'AMBIGUOUS' && typeof t.entryTime === 'string' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL'));
  const mismatches = [];

  for (const t of targets) {
    const index = byTime.get(t.entryTime);
    if (!Number.isInteger(index)) continue;
    const x = replayAt(candles, index);
    if (x?.trigger?.timestamp === t.entryTime && x?.trigger?.direction === t.direction) continue;

    const nearby = [];
    for (let d = -3; d <= 3; d++) {
      const i = index + d;
      if (i < 0 || i >= candles.length) continue;
      const y = replayAt(candles, i);
      if (y) nearby.push({ offset: d, index: i, candleTime: candles[i].timestamp, triggerTime: y.trigger.timestamp, direction: y.trigger.direction });
    }
    mismatches.push({ entryTime: t.entryTime, direction: t.direction, baselineEntryIndex: Number(t.entryIndex), canonicalIndex: index, canonicalCandle: candles[index], replay: x ? { triggerTime: x.trigger.timestamp, direction: x.trigger.direction } : null, nearby });
  }

  console.log(JSON.stringify({ targetCount: targets.length, mismatchCount: mismatches.length, mismatches }, null, 2));
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
