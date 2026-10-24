import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule, isInvalidated } from '../src/domain/strategy-a/Invalidation.js';
import { calculateStructureStopLoss } from '../src/domain/strategy-a/StructureStopLoss.js';

const c = (i:number,o:number,h:number,l:number,cl:number): Candle => ({ timestamp:`2026-01-01T00:${String(i).padStart(2,'0')}:00Z`, open:o, high:h, low:l, close:cl });

const correction = { spikeStartIndex:0, spikeEndIndex:2, correctionStartIndex:3, correctionExtremeIndex:3, direction:'BULLISH' as const, extremePrice:99 };

describe('Strategy A entry, invalidation and structure SL', () => {
  it('requires a post-correction close reclaim for BUY', () => {
    const trigger = detectEntryTrigger([c(0,100,101,99,100),c(1,100,104,100,103),c(2,103,106,102,105),c(3,105,102,99,100),c(4,100,103,99.5,101)], correction);
    expect(trigger?.direction).toBe('BUY');
    expect(trigger?.triggerLevel).toBe(99);
  });

  it('uses the correction extreme as invalidation', () => {
    const rule = getInvalidationRule(correction);
    expect(rule.invalidationLevel).toBe(99);
    expect(isInvalidated(c(5,99,99.5,98,98.5), rule)).toBe(true);
  });

  it('places SL at structure invalidation with optional zero buffer', () => {
    const entry = { index:4, timestamp:'2026-01-01T00:04:00Z', direction:'BUY' as const, entryPrice:101, triggerLevel:99, reason:'CORRECTION_EXTREME_RECLAIM' as const };
    const sl = calculateStructureStopLoss(entry, correction);
    expect(sl.stopLoss).toBe(99);
    expect(sl.riskDistance).toBe(2);
  });
});
