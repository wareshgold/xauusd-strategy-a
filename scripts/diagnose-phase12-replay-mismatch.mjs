import { execFileSync } from 'node:child_process';
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
const OLD_REF = '0017947aac1be7a6f315717d38fec6e2fc58ecb7';

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

function loadOldDataset() {
  const raw = execFileSync('git', ['show', `${OLD_REF}:data/historical/xauusd-5min.json`], {
    cwd: ROOT,
    maxBuffer: 256 * 1024 * 1024,
  });
  return JSON.parse(raw.toString('utf8')).candles ?? [];
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const current = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const old = loadOldDataset();
  const currentByTime = new Map(current.map((c, i) => [c.timestamp, i]));
  const oldByTime = new Map(old.map((c, i) => [c.timestamp, i]));
  const targets = (base.trades ?? []).filter((t) =>
    t.result !== 'AMBIGUOUS' &&
    typeof t.entryTime === 'string' &&
    Number.isFinite(Number(t.rMultiple)) &&
    (t.direction === 'BUY' || t.direction === 'SELL'),
  );

  const rows = targets.map((t) => {
    const oldIndex = oldByTime.get(t.entryTime);
    const currentIndex = currentByTime.get(t.entryTime);
    const oldReplay = Number.isInteger(oldIndex) ? replayAt(old, oldIndex) : null;
    const currentReplay = Number.isInteger(currentIndex) ? replayAt(current, currentIndex) : null;
    const oldCandle = Number.isInteger(oldIndex) ? old[oldIndex] : null;
    const currentCandle = Number.isInteger(currentIndex) ? current[currentIndex] : null;
    return {
      entryTime: t.entryTime,
      baselineDirection: t.direction,
      baselineEntryIndex: Number(t.entryIndex),
      oldIndex,
      currentIndex,
      oldDirection: oldReplay?.trigger?.direction ?? null,
      currentDirection: currentReplay?.trigger?.direction ?? null,
      oldCandle,
      currentCandle,
    };
  });

  const mismatches = rows.filter((r) =>
    r.oldDirection !== r.baselineDirection || r.currentDirection !== r.baselineDirection,
  );
  const candleChanges = rows.filter((r) => JSON.stringify(r.oldCandle) !== JSON.stringify(r.currentCandle));
  const target = rows.find((r) => r.entryTime === '2026-08-26 12:35:00');

  console.log(JSON.stringify({
    oldDatasetRef: OLD_REF,
    oldCount: old.length,
    currentCount: current.length,
    targetCount: rows.length,
    baselineReplayMatchesOnOld: rows.filter((r) => r.oldDirection === r.baselineDirection).length,
    baselineReplayMatchesOnCurrent: rows.filter((r) => r.currentDirection === r.baselineDirection).length,
    oldVsCurrentCandleChangesAtBaselineTimestamps: candleChanges.length,
    mismatchCount: mismatches.length,
    target,
    mismatches,
  }, null, 2));
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
