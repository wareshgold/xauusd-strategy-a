import { describe, expect, it } from 'vitest';
import { canSubmitStopModification } from './BrokerConstraintGate';

describe('broker constraint gate', () => {
  it('blocks unknown constraints', () => {
    expect(
      canSubmitStopModification({
        known: false,
        minimumStopDistancePrice: null,
        freezeDistancePrice: null,
      }),
    ).toBe(false);
  });

  it('blocks partially specified constraints', () => {
    expect(
      canSubmitStopModification({
        known: true,
        minimumStopDistancePrice: 1,
        freezeDistancePrice: null,
      }),
    ).toBe(false);
  });

  it('blocks non-finite constraints', () => {
    expect(
      canSubmitStopModification({
        known: true,
        minimumStopDistancePrice: Number.POSITIVE_INFINITY,
        freezeDistancePrice: 1,
      }),
    ).toBe(false);
  });

  it('accepts a fully specified non-negative constraint state', () => {
    expect(
      canSubmitStopModification({
        known: true,
        minimumStopDistancePrice: 1,
        freezeDistancePrice: 0,
      }),
    ).toBe(true);
  });
});
