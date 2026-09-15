import { describe, expect, it } from 'vitest';
import { evaluateTrailingExecutionState } from './TrailingExecutionStateMachine.js';

const base = {
  enabled: true,
  contractFrozen: true,
  brokerConstraintsKnown: true,
  requestValid: true,
  brokerAccepted: true,
  direction: 'BUY' as const,
  currentStopLoss: 3300,
  proposedStopLoss: 3310,
};

describe('deterministic trailing execution state machine', () => {
  it('A: disabled trailing stops immediately', () => {
    expect(evaluateTrailingExecutionState({ ...base, enabled: false })).toBe('TRAILING_DISABLED');
  });

  it('B: blocks an unfrozen execution contract', () => {
    expect(evaluateTrailingExecutionState({ ...base, contractFrozen: false })).toBe('CONTRACT_BLOCKED');
  });

  it('C: blocks unknown broker constraints', () => {
    expect(evaluateTrailingExecutionState({ ...base, brokerConstraintsKnown: false })).toBe('BROKER_CONSTRAINT_BLOCKED');
  });

  it('D: blocks an invalid request', () => {
    expect(evaluateTrailingExecutionState({ ...base, requestValid: false })).toBe('REQUEST_INVALID');
  });

  it('E: accepts a favorable BUY stop proposal when MT5 accepts it', () => {
    expect(evaluateTrailingExecutionState(base)).toBe('MODIFICATION_ACCEPTED');
  });

  it('F: rejects a BUY stop loosening proposal', () => {
    expect(evaluateTrailingExecutionState({ ...base, proposedStopLoss: 3290 })).toBe('REQUEST_INVALID');
  });

  it('G: accepts a favorable SELL stop proposal when MT5 accepts it', () => {
    expect(evaluateTrailingExecutionState({
      ...base,
      direction: 'SELL',
      currentStopLoss: 3300,
      proposedStopLoss: 3290,
    })).toBe('MODIFICATION_ACCEPTED');
  });

  it('H: rejects a SELL stop loosening proposal', () => {
    expect(evaluateTrailingExecutionState({
      ...base,
      direction: 'SELL',
      currentStopLoss: 3300,
      proposedStopLoss: 3310,
    })).toBe('REQUEST_INVALID');
  });

  it('I: preserves broker rejection after all local gates pass', () => {
    expect(evaluateTrailingExecutionState({ ...base, brokerAccepted: false })).toBe('MODIFICATION_REJECTED');
  });

  it('J: reaches modification accepted only after every gate passes', () => {
    expect(evaluateTrailingExecutionState(base)).toBe('MODIFICATION_ACCEPTED');
  });
});
