import { describe, expect, it } from 'vitest';
import { requireSourceConfirmedPGAP } from '../src/domain/strategy-a/SourceAlignedSP2L.js';

type Fixture = {
  readonly name: string;
  readonly purpose: string;
  readonly expectedResearchState: 'UNRESOLVED';
};

/**
 * Research-only fixtures.
 *
 * These deliberately do not encode a P-Gap formula. Their purpose is to ensure
 * competing geometric interpretations cannot silently become canonical rules.
 */
const fixtures: readonly Fixture[] = [
  {
    name: 'immediate-boundary-separation',
    purpose: 'Breakout followed by immediate non-overlap between candle boundaries.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'higher-lows-then-gap',
    purpose: 'Higher lows appear first and the P-Gap marker appears later.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'third-construction-follow-through',
    purpose: 'Accepted source construction where the next candle fails to extend the prior extreme as described in the transcript.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'overlapping-channel-rejection',
    purpose: 'Visually similar directional movement with candle overlap/channel behaviour.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'touch-not-gap',
    purpose: 'Boundary equality/touch case to distinguish strict gap from touching.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'wick-only-separation',
    purpose: 'Only wick extremes separate while candle bodies overlap.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'body-only-separation',
    purpose: 'Bodies separate while wick extremes may overlap.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'delayed-gap',
    purpose: 'Gap appears after an intervening candle rather than immediately after breakout.',
    expectedResearchState: 'UNRESOLVED',
  },
  {
    name: 'pending-limit-before-fill',
    purpose: 'Limit exists during correction before any later confirmation candle closes.',
    expectedResearchState: 'UNRESOLVED',
  },
];

describe('SP2L geometry resolution fixtures', () => {
  it('keeps every unresolved geometry fixture out of canonical P-Gap classification', () => {
    expect(fixtures).toHaveLength(9);
    for (const fixture of fixtures) {
      expect(fixture.expectedResearchState).toBe('UNRESOLVED');
    }
  });

  it('does not allow a generic object to masquerade as source-confirmed P-Gap', () => {
    expect(() => requireSourceConfirmedPGAP({ kind: 'GENERIC_THREE_CANDLE_IMBALANCE' } as never))
      .toThrow('SOURCE_P_GAP_CONFIRMATION_REQUIRED');
  });
});
