import { describe, expect, it } from 'vitest';
import {
  applySp2lEvent,
  createInitialSp2lState,
  resolveSameCandleTouch,
  type Sp2lEvent,
} from '../src/domain/research/sp2l-v2/Sp2lSemanticState.js';
import { measureSp2lLegs } from '../src/domain/research/sp2l-v2/Sp2lGeometryMeasurement.js';

function replay(events: Sp2lEvent[]) {
  return events.reduce(applySp2lEvent, createInitialSp2lState());
}

const bullishSetup: Sp2lEvent[] = [
  { type: 'CONTEXT_IDENTIFIED', contextId: 'fixture-bull-context' },
  { type: 'STRONG_MOVE_STARTED', impulseId: 'impulse-bull-1', direction: 'BULLISH' },
  { type: 'FOLLOW_THROUGH_CONFIRMED', index: 8 },
  { type: 'SPIKE_CONFIRMED', spikeId: 'spike-bull-1' },
  {
    type: 'STRUCTURAL_REFERENCE_IDENTIFIED',
    index: 12,
    price: 2500,
    status: 'SOURCE_CONFIRMED',
    rationale: 'Fixture marks the first structural low explicitly; algorithm remains source/TBD.',
  },
  { type: 'CORRECTION_BEGAN', index: 13 },
  {
    type: 'PENDING_LIMIT_CREATED',
    index: 13,
    entryPrice: 2500,
    stopLoss: 2492,
    entryStatus: 'CANDIDATE',
    stopStatus: 'CANDIDATE',
    rationale: 'Fixture value only; no historical optimization.',
  },
];

describe('SP2L V2 semantic state model (non-production)', () => {
  it('accepts the source-shaped bullish lifecycle up to a pending order', () => {
    const state = replay(bullishSetup);

    expect(state.phase).toBe('PENDING');
    expect(state.direction).toBe('BULLISH');
    expect(state.followThroughIndex).toBe(8);
    expect(state.geometry.firstStructuralReference.price).toBe(2500);
    expect(state.geometry.pendingEntryPrice.price).toBe(2500);
    expect(state.geometry.structuralStop.price).toBe(2492);
  });

  it('accepts the bearish mirror lifecycle', () => {
    const state = replay([
      { type: 'CONTEXT_IDENTIFIED', contextId: 'fixture-bear-context' },
      { type: 'STRONG_MOVE_STARTED', impulseId: 'impulse-bear-1', direction: 'BEARISH' },
      { type: 'FOLLOW_THROUGH_CONFIRMED', index: 8 },
      { type: 'SPIKE_CONFIRMED', spikeId: 'spike-bear-1' },
      { type: 'STRUCTURAL_REFERENCE_IDENTIFIED', index: 12, price: 2500, status: 'SOURCE_CONFIRMED' },
      { type: 'CORRECTION_BEGAN', index: 13 },
      { type: 'PENDING_LIMIT_CREATED', index: 13, entryPrice: 2500, stopLoss: 2508 },
    ]);

    expect(state.phase).toBe('PENDING');
    expect(state.direction).toBe('BEARISH');
  });

  it('rejects a strong move without context', () => {
    const state = replay([
      { type: 'STRONG_MOVE_STARTED', impulseId: 'impulse-1', direction: 'BULLISH' },
    ]);

    expect(state.phase).toBe('REJECTED');
    expect(state.rejectionReason).toBe('STRONG_MOVE_REQUIRES_CONTEXT');
  });

  it('rejects follow-through that returns into the prior area', () => {
    const state = replay([
      { type: 'CONTEXT_IDENTIFIED', contextId: 'ctx' },
      { type: 'STRONG_MOVE_STARTED', impulseId: 'impulse', direction: 'BULLISH' },
      { type: 'FOLLOW_THROUGH_REJECTED', reason: 'FOLLOW_THROUGH_RETURNED_INTO_PRIOR_AREA' },
    ]);

    expect(state.phase).toBe('REJECTED');
    expect(state.rejectionReason).toBe('FOLLOW_THROUGH_RETURNED_INTO_PRIOR_AREA');
  });

  it('requires the structural reference before correction begins', () => {
    const state = replay([
      { type: 'CONTEXT_IDENTIFIED', contextId: 'ctx' },
      { type: 'STRONG_MOVE_STARTED', impulseId: 'impulse', direction: 'BULLISH' },
      { type: 'FOLLOW_THROUGH_CONFIRMED', index: 8 },
      { type: 'SPIKE_CONFIRMED', spikeId: 'spike' },
      { type: 'CORRECTION_BEGAN', index: 10 },
    ]);

    expect(state.phase).toBe('REJECTED');
    expect(state.rejectionReason).toBe('CORRECTION_REQUIRES_STRUCTURAL_REFERENCE');
  });

  it('requires an explicit stop before a pending order exists', () => {
    const state = replay([
      ...bullishSetup.slice(0, -1),
      { type: 'PENDING_LIMIT_CREATED', index: 13, entryPrice: 2500, stopLoss: null },
    ]);

    expect(state.phase).toBe('REJECTED');
    expect(state.rejectionReason).toBe('PENDING_LIMIT_REQUIRES_EXPLICIT_STRUCTURAL_STOP');
  });

  it('models pending-before-fill and fills only on an exact limit touch', () => {
    const pending = replay(bullishSetup);
    expect(pending.phase).toBe('PENDING');
    expect(pending.fillIndex).toBeNull();

    const untouched = applySp2lEvent(pending, { type: 'LIMIT_TOUCHED', index: 14, price: 2501 });
    expect(untouched.phase).toBe('PENDING');
    expect(untouched.fillIndex).toBeNull();

    const filled = applySp2lEvent(untouched, { type: 'LIMIT_TOUCHED', index: 15, price: 2500 });
    expect(filled.phase).toBe('FILLED');
    expect(filled.fillIndex).toBe(15);
    expect(filled.position.entryPrice).toBe(2500);
    expect(filled.position.stopLoss).toBe(2492);
  });

  it('cancels an untouched pending order on structural invalidation', () => {
    const state = applySp2lEvent(replay(bullishSetup), {
      type: 'STRUCTURAL_INVALIDATION',
      index: 14,
    });

    expect(state.phase).toBe('INVALIDATED');
    expect(state.fillIndex).toBeNull();
    expect(state.invalidationIndex).toBe(14);
  });

  it('records a post-fill stop as a stop outcome, not as pending invalidation', () => {
    const filled = applySp2lEvent(replay(bullishSetup), {
      type: 'LIMIT_TOUCHED',
      index: 15,
      price: 2500,
    });

    const stopped = applySp2lEvent(filled, {
      type: 'STOP_HIT',
      index: 16,
      price: 2492,
    });

    expect(stopped.phase).toBe('STOPPED');
    expect(stopped.fillIndex).toBe(15);
    expect(stopped.invalidationIndex).toBe(16);
    expect(stopped.position.stopLoss).toBe(2492);
  });

  it('ignores a non-matching post-fill stop price', () => {
    const filled = applySp2lEvent(replay(bullishSetup), {
      type: 'LIMIT_TOUCHED',
      index: 15,
      price: 2500,
    });

    const unchanged = applySp2lEvent(filled, {
      type: 'STOP_HIT',
      index: 16,
      price: 2491,
    });

    expect(unchanged.phase).toBe('FILLED');
  });

  it('keeps Leg 1 and Leg 2 geometry explicit instead of inventing formulas', () => {
    const state = replay(bullishSetup);

    expect(state.geometry.leg1Endpoint.status).toBe('TBD');
    expect(state.geometry.leg1Endpoint.index).toBeNull();
    expect(state.geometry.leg2ProjectionOrigin.status).toBe('TBD');
    expect(state.geometry.leg2EqualityTolerance).toBeNull();
    expect(state.position.position2xEnabled).toBe(false);
  });

  it('keeps an unresolved Leg 2 origin separate from the pending fill price', () => {
    const filled = applySp2lEvent(replay(bullishSetup), {
      type: 'LIMIT_TOUCHED',
      index: 15,
      price: 2500,
    });

    expect(filled.phase).toBe('FILLED');
    expect(filled.position.entryPrice).toBe(2500);
    expect(filled.geometry.leg2ProjectionOrigin.status).toBe('TBD');
    expect(filled.geometry.leg2ProjectionOrigin.price).toBeNull();
    expect(filled.geometry.leg2ProjectionOrigin.index).toBeNull();
  });

  it('accepts a source-shaped correction-origin classification without equating it to fill', () => {
    const pending = replay(bullishSetup);
    const classified = applySp2lEvent(pending, {
      type: 'LEG2_PROJECTION_ORIGIN_IDENTIFIED',
      index: 14,
      price: null,
      status: 'SOURCE_CONFIRMED',
      rationale: 'Source confirms the parent Leg 2 begins from the intervening deep correction; exact OHLC coordinate remains unresolved.',
    });

    expect(classified.phase).toBe('PENDING');
    expect(classified.geometry.leg2ProjectionOrigin.status).toBe('SOURCE_CONFIRMED');
    expect(classified.geometry.leg2ProjectionOrigin.index).toBe(14);
    expect(classified.geometry.leg2ProjectionOrigin.price).toBeNull();
    expect(classified.geometry.pendingEntryPrice.price).toBe(2500);
  });

  it('rejects a Leg 2 origin placed before the correction begins', () => {
    const pending = replay(bullishSetup);
    const invalid = applySp2lEvent(pending, {
      type: 'LEG2_PROJECTION_ORIGIN_IDENTIFIED',
      index: 12,
      price: 2498,
      status: 'CANDIDATE',
    });

    expect(invalid.phase).toBe('REJECTED');
    expect(invalid.rejectionReason).toBe('LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION');
  });

  it('keeps 2X separate from position 1', () => {
    const state = applySp2lEvent(replay(bullishSetup), {
      type: 'LIMIT_TOUCHED',
      index: 15,
      price: 2500,
    });

    expect(state.position.position2xEnabled).toBe(false);
  });

  it('makes same-candle entry/SL/TP ordering an explicit simulator policy', () => {
    const touches = { entry: true, stop: true, tp1: true };

    expect(resolveSameCandleTouch('SL_FIRST', touches)).toBe('STOP');
    expect(resolveSameCandleTouch('TP_FIRST', touches)).toBe('TP1');
    expect(resolveSameCandleTouch('AMBIGUOUS', touches)).toBe('AMBIGUOUS');
    expect(resolveSameCandleTouch('AMBIGUOUS', { entry: true, stop: false, tp1: false })).toBe('FILL');
  });

  it('preserves the pending-limit semantic distinction from the old close-reclaim model', () => {
    const state = replay(bullishSetup);

    expect(state.phase).toBe('PENDING');
    expect(state.pendingCreatedAt).toBe(13);
    expect(state.fillIndex).toBeNull();
  });

  it('measures explicit leg endpoints without selecting them or fitting tolerance', () => {
    const measurement = measureSp2lLegs({
      leg1StartPrice: 2500,
      leg1EndPrice: 2520,
      leg2StartPrice: 2508,
      leg2EndPrice: 2528,
    });

    expect(measurement.leg1Magnitude).toBe(20);
    expect(measurement.leg2Magnitude).toBe(20);
    expect(measurement.leg2ToLeg1Ratio).toBe(1);
    expect(measurement.equalityRelation).toBe('APPROXIMATELY_EQUAL_CANDIDATE');
    expect(measurement.equalityTolerance).toBeNull();
  });

  it('returns an undetermined equality relation when Leg 1 has zero magnitude', () => {
    const measurement = measureSp2lLegs({
      leg1StartPrice: 2500,
      leg1EndPrice: 2500,
      leg2StartPrice: 2508,
      leg2EndPrice: 2528,
    });

    expect(measurement.leg1Magnitude).toBe(0);
    expect(measurement.leg2ToLeg1Ratio).toBeNull();
    expect(measurement.equalityRelation).toBe('UNDETERMINED');
    expect(measurement.equalityTolerance).toBeNull();
  });

  it('rejects non-finite explicit endpoint prices', () => {
    expect(() => measureSp2lLegs({
      leg1StartPrice: Number.NaN,
      leg1EndPrice: 2520,
      leg2StartPrice: 2508,
      leg2EndPrice: 2528,
    })).toThrow('LEG1_START_PRICE_MUST_BE_FINITE');
  });
});
