import { describe, expect, it } from 'vitest';
import {
  createPendingLimitEntry,
  projectABEqualCD,
  requireSourceConfirmedPGAP,
  type SourceAlignedSP2LSetup,
} from '../src/domain/strategy-a/SourceAlignedSP2L.js';

describe('source-aligned SP2L semantics', () => {
  const setup: SourceAlignedSP2LSetup = {
    side: 'BUY',
    gap: { kind: 'P_GAP', startIndex: 3, endIndex: 5 },
    leg1: { startIndex: 1, endIndex: 3, startPrice: 100, endPrice: 120 },
    correction: { index: 6, price: 110 },
    pendingLimit: createPendingLimitEntry(112),
  };

  it('projects CD from source-confirmed C using AB magnitude', () => {
    expect(projectABEqualCD(setup)).toEqual({
      leg1Magnitude: 20,
      leg2Magnitude: 20,
      target: 130,
    });
  });

  it('requires an explicitly source-confirmed P-GAP', () => {
    expect(() => requireSourceConfirmedPGAP(null)).toThrow('SOURCE_P_GAP_CONFIRMATION_REQUIRED');
    expect(requireSourceConfirmedPGAP(setup.gap)).toEqual(setup.gap);
  });

  it('represents entry as a pending limit rather than a close-reclaim', () => {
    expect(setup.pendingLimit).toEqual({ price: 112, placedBeforeFill: true });
  });

  it('rejects non-finite pending limit prices', () => {
    expect(() => createPendingLimitEntry(Number.NaN)).toThrow('INVALID_PENDING_LIMIT_PRICE');
  });
});
