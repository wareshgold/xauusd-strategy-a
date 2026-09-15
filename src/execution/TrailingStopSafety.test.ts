import { clampFavorableStop, isFavorableStop } from './TrailingStopSafety';

describe('TrailingStopSafety', () => {
  it('allows BUY stop to move upward or remain equal', () => {
    expect(isFavorableStop('BUY', 100, 101)).toBe(true);
    expect(isFavorableStop('BUY', 100, 100)).toBe(true);
    expect(isFavorableStop('BUY', 100, 99)).toBe(false);
  });

  it('allows SELL stop to move downward or remain equal', () => {
    expect(isFavorableStop('SELL', 100, 99)).toBe(true);
    expect(isFavorableStop('SELL', 100, 100)).toBe(true);
    expect(isFavorableStop('SELL', 100, 101)).toBe(false);
  });

  it('rejects non-finite prices', () => {
    expect(clampFavorableStop('BUY', 100, Number.NaN)).toBeNull();
    expect(clampFavorableStop('SELL', Number.POSITIVE_INFINITY, 99)).toBeNull();
  });
});
