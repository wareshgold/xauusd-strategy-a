import { describe, expect, it } from 'vitest';
import { calculateStructureStopLoss } from '../src/domain/strategy-a/StructureStopLoss.js';
import { validateStructureSL } from '../src/domain/strategy-a/SLValidity.js';

const correction = { spikeStartIndex:0, spikeEndIndex:2, correctionStartIndex:3, correctionExtremeIndex:3, direction:'BULLISH' as const, extremePrice:99 };
const entry = { index:4, timestamp:'2026-01-01T00:04:00Z', direction:'BUY' as const, entryPrice:101, triggerLevel:99, reason:'CORRECTION_EXTREME_RECLAIM' as const };

describe('structural SL validity', () => {
  it('accepts a positive-risk SL on the correct side', () => {
    const sl = calculateStructureStopLoss(entry, correction);
    expect(validateStructureSL(entry, correction, sl)).toEqual({ valid:true, reason:'VALID' });
  });

  it('rejects non-positive risk without adding a distance threshold', () => {
    const zeroRisk = { ...calculateStructureStopLoss(entry, correction), stopLoss:101, riskDistance:0 };
    expect(validateStructureSL(entry, correction, zeroRisk)).toEqual({ valid:false, reason:'NON_POSITIVE_RISK' });
  });
});
