import type { Candle } from './Candle.js';
import type { BreakoutEvent } from './BreakoutDetector.js';

export interface FollowThroughConfig {
  readonly maxBarsAfterBreakout: number;
  readonly requireCloseBeyondBrokenLevel: boolean;
}

export interface FollowThroughEvent {
  readonly breakoutIndex: number;
  readonly followThroughIndex: number;
  readonly direction: BreakoutEvent['direction'];
  readonly timestamp: string;
}

export function detectFollowThrough(candles: readonly Candle[], breakouts: readonly BreakoutEvent[], config: FollowThroughConfig): FollowThroughEvent[] {
  const results: FollowThroughEvent[] = [];
  for (const breakout of breakouts) {
    const end = Math.min(candles.length - 1, breakout.index + config.maxBarsAfterBreakout);
    for (let i = breakout.index + 1; i <= end; i += 1) {
      const candle = candles[i]!;
      const directional = breakout.direction === 'BULLISH' ? candle.close > breakout.close : candle.close < breakout.close;
      const beyondLevel = breakout.direction === 'BULLISH' ? candle.close > breakout.brokenLevel : candle.close < breakout.brokenLevel;
      if (directional && (!config.requireCloseBeyondBrokenLevel || beyondLevel)) {
        results.push({ breakoutIndex: breakout.index, followThroughIndex: i, direction: breakout.direction, timestamp: candle.timestamp });
        break;
      }
    }
  }
  return results;
}
