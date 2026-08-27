import { describe, expect, it } from 'vitest';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const c = (index: number, open: number, high: number, low: number, close: number) => ({
  index,
  timestamp: `2026-01-01T00:${String(index).padStart(2, '0')}:00Z`,
  open,
  high,
  low,
  close,
  volume: 1,
});

const correction = {
  direction: 'BULLISH' as const,
  correctionExtremeIndex: 3,
  extremePrice: 99,
};

describe('Strategy A entry reclaim regression', () => {
  it('accepts a post-correction close reclaim even when the candle opens above the level', () => {
    const trigger = detectEntryTrigger([
      c(0, 100, 101, 99, 100),
      c(1, 100, 104, 100, 103),
      c(2, 103, 106, 102, 105),
      c(3, 105, 102, 99, 100),
      c(4, 100, 103, 99.5, 101),
    ], correction);

    expect(trigger?.direction).toBe('BUY');
    expect(trigger?.triggerLevel).toBe(99);
    expect(trigger?.index).toBe(4);
  });

  it('does not trigger before the correction extreme index', () => {
    const trigger = detectEntryTrigger([
      c(0, 100, 101, 99, 100),
      c(1, 100, 104, 100, 103),
      c(2, 103, 106, 102, 105),
    ], { ...correction, correctionExtremeIndex: 1 });

    expect(trigger?.index).toBe(2);
  });
});
