import { describe, expect, it } from 'vitest';
import { evaluateBrokerConstraintState } from './BrokerConstraintEvaluation.js';

describe('deterministic broker constraint evaluation', () => {
  it('blocks unknown constraints', () => {
    expect(evaluateBrokerConstraintState({
      known: false,
      minimumStopDistancePrice: null,
      freezeDistancePrice: null,
    })).toBe('BROKER_CONSTRAINT_BLOCKED');
  });

  it('blocks partially specified constraints', () => {
    expect(evaluateBrokerConstraintState({
      known: true,
      minimumStopDistancePrice: 0.5,
      freezeDistancePrice: null,
    })).toBe('BROKER_CONSTRAINT_BLOCKED');
  });

  it('blocks non-finite constraints', () => {
    expect(evaluateBrokerConstraintState({
      known: true,
      minimumStopDistancePrice: Number.POSITIVE_INFINITY,
      freezeDistancePrice: 0,
    })).toBe('BROKER_CONSTRAINT_BLOCKED');
  });

  it('blocks negative constraints', () => {
    expect(evaluateBrokerConstraintState({
      known: true,
      minimumStopDistancePrice: -0.1,
      freezeDistancePrice: 0,
    })).toBe('BROKER_CONSTRAINT_BLOCKED');
  });

  it('accepts a complete non-negative constraint state', () => {
    expect(evaluateBrokerConstraintState({
      known: true,
      minimumStopDistancePrice: 0.5,
      freezeDistancePrice: 0.2,
    })).toBe('BROKER_CONSTRAINTS_VALID');
  });
});
