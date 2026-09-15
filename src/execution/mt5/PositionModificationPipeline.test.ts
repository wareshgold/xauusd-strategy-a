import { describe, expect, it } from 'vitest';
import { evaluatePositionModificationPipeline } from './PositionModificationPipeline.js';

const constraints = {
  known: true,
  minimumStopDistancePrice: 0.5,
  freezeDistancePrice: 0.2,
};

const request = {
  positionId: 'synthetic-position-1',
  direction: 'BUY' as const,
  currentStopLoss: 3300,
  proposedStopLoss: 3310,
};

describe('MT5 position modification pipeline', () => {
  it('blocks when trailing is disabled', () => {
    expect(evaluatePositionModificationPipeline({
      trailingEnabled: false,
      contractFrozen: true,
      brokerConstraints: constraints,
      request,
      brokerAccepted: true,
    })).toBe('TRAILING_DISABLED');
  });

  it('blocks before broker submission when the contract is not frozen', () => {
    expect(evaluatePositionModificationPipeline({
      trailingEnabled: true,
      contractFrozen: false,
      brokerConstraints: constraints,
      request,
      brokerAccepted: true,
    })).toBe('CONTRACT_BLOCKED');
  });

  it('blocks before broker submission when broker constraints are incomplete', () => {
    expect(evaluatePositionModificationPipeline({
      trailingEnabled: true,
      contractFrozen: true,
      brokerConstraints: { ...constraints, freezeDistancePrice: null },
      request,
      brokerAccepted: true,
    })).toBe('BROKER_CONSTRAINT_BLOCKED');
  });

  it('blocks a request that loosens a BUY stop', () => {
    expect(evaluatePositionModificationPipeline({
      trailingEnabled: true,
      contractFrozen: true,
      brokerConstraints: constraints,
      request: { ...request, proposedStopLoss: 3290 },
      brokerAccepted: true,
    })).toBe('REQUEST_INVALID');
  });

  it('accepts a favorable BUY modification when the broker accepts it', () => {
    expect(evaluatePositionModificationPipeline({
      trailingEnabled: true,
      contractFrozen: true,
      brokerConstraints: constraints,
      request,
      brokerAccepted: true,
    })).toBe('MODIFICATION_ACCEPTED');
  });

  it('preserves broker rejection after local gates pass', () => {
    expect(evaluatePositionModificationPipeline({
      trailingEnabled: true,
      contractFrozen: true,
      brokerConstraints: constraints,
      request,
      brokerAccepted: false,
    })).toBe('MODIFICATION_REJECTED');
  });
});
