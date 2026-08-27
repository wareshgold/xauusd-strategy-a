import type { Candle } from '../market/Candle.js';
import type { BreakoutEvent } from '../market/BreakoutDetector.js';
import type { FollowThroughEvent } from '../market/FollowThroughDetector.js';
import type { SpikeCandidate } from './SpikeCandidate.js';

export interface SpikeDetectionConfig {
  readonly maxCandles: number;
  readonly minDirectionalFraction: number;
  readonly maxOverlapFraction: number;
}

export interface SpikeDetectionResult {
  readonly candidates: SpikeCandidate[];
  readonly rejected: Array<{ startIndex: number; endIndex: number; reason: string }>;
}

function bodyDirection(candle: Candle): number {
  return candle.close > candle.open ? 1 : candle.close < candle.open ? -1 : 0;
}

function overlapFraction(candles: readonly Candle[]): number {
  if (candles.length < 2) return 0;
  let overlap = 0;
  let total = 0;
  for (let i = 1; i < candles.length; i += 1) {
    const previous = candles[i - 1]!;
    const current = candles[i]!;
    const intersection = Math.max(0, Math.min(previous.high, current.high) - Math.max(previous.low, current.low));
    const union = Math.max(previous.high, current.high) - Math.min(previous.low, current.low);
    overlap += union === 0 ? 0 : intersection / union;
    total += 1;
  }
  return overlap / total;
}

/**
 * Research-stage detector only. It identifies directional impulse candidates
 * around already-detected breakout + follow-through events. It deliberately
 * does not assign a trading signal or invent a P-GAP threshold.
 */
export function detectSpikeCandidates(
  candles: readonly Candle[],
  breakouts: readonly BreakoutEvent[],
  followThrough: readonly FollowThroughEvent[],
  config: SpikeDetectionConfig,
): SpikeDetectionResult {
  const candidates: SpikeCandidate[] = [];
  const rejected: SpikeDetectionResult['rejected'] = [];

  for (const breakout of breakouts) {
    const ft = followThrough.find((event) => event.breakoutIndex === breakout.index);
    if (!ft) continue;
    const startIndex = Math.max(0, breakout.index - config.maxCandles + 1);
    const endIndex = ft.followThroughIndex;
    const window = candles.slice(startIndex, endIndex + 1);
    if (window.length < 2) continue;

    const direction = breakout.direction === 'BULLISH' ? 1 : -1;
    const directional = window.filter((c) => bodyDirection(c) === direction).length / window.length;
    const overlap = overlapFraction(window);
    const startPrice = direction === 1 ? window[0]!.low : window[0]!.high;
    const endPrice = direction === 1 ? window.at(-1)!.high : window.at(-1)!.low;
    const size = Math.abs(endPrice - startPrice);

    if (directional < config.minDirectionalFraction) {
      rejected.push({ startIndex, endIndex, reason: 'DIRTY_STRUCTURE' });
      continue;
    }
    if (overlap > config.maxOverlapFraction) {
      rejected.push({ startIndex, endIndex, reason: 'EXCESSIVE_OVERLAP' });
      continue;
    }

    candidates.push({
      startIndex,
      endIndex,
      direction: breakout.direction,
      startPrice,
      endPrice,
      size,
      breakoutIndex: breakout.index,
      followThroughIndex: ft.followThroughIndex,
      structureScore: directional,
      overlapScore: 1 - overlap,
      hasPGAPEvidence: false,
    });
  }

  return { candidates, rejected };
}
