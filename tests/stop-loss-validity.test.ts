import { describe, expect, it } from 'vitest';
import { isValidStructureStopLoss } from '../src/domain/strategy-a/StopLossValidity.js';
import type { StructureStopLoss } from '../src/domain/strategy-a/StructureStopLoss.js';

const make = (overrides: Partial<StructureStopLoss> = {}): StructureStopLoss => ({
  direction: 'BUY', entryPrice: 101, stopLoss: 99, riskDistance: 2, structureReference: 99, ...overrides,
});

describe('Strategy A SL validity', () => {
  it('accepts a finite stop strictly beyond BUY invalidation', () => {
    expect(isValidStructureStopLoss(make())).toBe(true);
  });

  it('accepts a finite stop strictly beyond SELL invalidation', () => {
    expect(isValidStructureStopLoss(make({ direction: 'SELL', entryPrice: 99, stopLoss: 101, riskDistance: 2, structureReference: 101 }))).toBe(true);
  });

  it('rejects zero or negative risk', () => {
    expect(isValidStructureStopLoss(make({ riskDistance: 0 }))).toBe(false);
    expect(isValidStructureStopLoss(make({ riskDistance: -1 }))).toBe(false);
  });

  it('rejects a stop on the wrong side of entry', () => {
    expect(isValidStructureStopLoss(make({ stopLoss: 102, riskDistance: 1 }))).toBe(false);
    expect(isValidStructureStopLoss(make({ direction: 'SELL', entryPrice: 99, stopLoss: 98, riskDistance: 1 }))).toBe(false);
  });

  it('rejects non-finite prices and risk', () => {
    expect(isValidStructureStopLoss(make({ entryPrice: Number.NaN }))).toBe(false);
    expect(isValidStructureStopLoss(make({ stopLoss: Number.POSITIVE_INFINITY }))).toBe(false);
    expect(isValidStructureStopLoss(make({ riskDistance: Number.NaN }))).toBe(false);
  });
});
