import { describe, expect, it } from 'vitest';

type Resolution = 'CANDIDATE' | 'UNRESOLVED' | 'REJECTED_AS_CANONICAL' | 'SOURCE_SUPPORTED_VARIANT';

type Fixture = {
  readonly id: string;
  readonly wick: Resolution;
  readonly body: Resolution;
  readonly genericThreeCandle: Resolution;
};

/**
 * Research-only fixture ledger.
 * These fixtures deliberately model ambiguity; they do not implement P-Gap.
 */
const fixtures: readonly Fixture[] = [
  { id: 'PG-SYN-01', wick: 'CANDIDATE', body: 'CANDIDATE', genericThreeCandle: 'CANDIDATE' },
  { id: 'PG-SYN-02', wick: 'CANDIDATE', body: 'UNRESOLVED', genericThreeCandle: 'CANDIDATE' },
  { id: 'PG-SYN-03', wick: 'UNRESOLVED', body: 'CANDIDATE', genericThreeCandle: 'CANDIDATE' },
  { id: 'PG-SYN-04', wick: 'UNRESOLVED', body: 'UNRESOLVED', genericThreeCandle: 'UNRESOLVED' },
  { id: 'PG-SYN-05', wick: 'SOURCE_SUPPORTED_VARIANT', body: 'SOURCE_SUPPORTED_VARIANT', genericThreeCandle: 'SOURCE_SUPPORTED_VARIANT' },
  { id: 'PG-SYN-06', wick: 'SOURCE_SUPPORTED_VARIANT', body: 'SOURCE_SUPPORTED_VARIANT', genericThreeCandle: 'SOURCE_SUPPORTED_VARIANT' },
  { id: 'PG-SYN-07', wick: 'UNRESOLVED', body: 'UNRESOLVED', genericThreeCandle: 'UNRESOLVED' },
  { id: 'PG-SYN-08', wick: 'UNRESOLVED', body: 'UNRESOLVED', genericThreeCandle: 'REJECTED_AS_CANONICAL' },
  { id: 'PG-SYN-09', wick: 'UNRESOLVED', body: 'UNRESOLVED', genericThreeCandle: 'UNRESOLVED' },
  { id: 'PG-SYN-10', wick: 'UNRESOLVED', body: 'UNRESOLVED', genericThreeCandle: 'UNRESOLVED' },
];

describe('SP2L synthetic P-Gap discrimination', () => {
  it('keeps wick/body ambiguity explicit', () => {
    expect(fixtures.find((x) => x.id === 'PG-SYN-02')?.wick).toBe('CANDIDATE');
    expect(fixtures.find((x) => x.id === 'PG-SYN-02')?.body).toBe('UNRESOLVED');
    expect(fixtures.find((x) => x.id === 'PG-SYN-03')?.wick).toBe('UNRESOLVED');
    expect(fixtures.find((x) => x.id === 'PG-SYN-03')?.body).toBe('CANDIDATE');
  });

  it('does not decide equality/touch without source evidence', () => {
    const f = fixtures.find((x) => x.id === 'PG-SYN-04');
    expect(f?.wick).toBe('UNRESOLVED');
    expect(f?.body).toBe('UNRESOLVED');
  });

  it('preserves both source-supported temporal constructions', () => {
    expect(fixtures.find((x) => x.id === 'PG-SYN-05')?.wick).toBe('SOURCE_SUPPORTED_VARIANT');
    expect(fixtures.find((x) => x.id === 'PG-SYN-06')?.wick).toBe('SOURCE_SUPPORTED_VARIANT');
  });

  it('rejects generic three-candle imbalance as canonical P-Gap', () => {
    expect(fixtures.find((x) => x.id === 'PG-SYN-08')?.genericThreeCandle)
      .toBe('REJECTED_AS_CANONICAL');
  });

  it('does not manufacture an early-trend threshold or channel-gap rule', () => {
    expect(fixtures.find((x) => x.id === 'PG-SYN-07')?.wick).toBe('UNRESOLVED');
    expect(fixtures.find((x) => x.id === 'PG-SYN-10')?.wick).toBe('UNRESOLVED');
  });
});
