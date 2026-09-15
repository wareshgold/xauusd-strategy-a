import { describe, expect, it } from 'vitest';
import {
  rejectUntilBrokerConstraintsAreFrozen,
  validatePositionModificationRequest,
} from './PositionModificationAdapter';

describe('MT5 position modification adapter boundary', () => {
  it('accepts a finite, identified request at the adapter boundary', () => {
    expect(
      validatePositionModificationRequest({
        positionId: 'position-1',
        direction: 'BUY',
        currentStopLoss: 3300,
        proposedStopLoss: 3310,
      }),
    ).toEqual({ accepted: true });
  });

  it('rejects an empty position identity', () => {
    expect(
      validatePositionModificationRequest({
        positionId: '  ',
        direction: 'SELL',
        currentStopLoss: 3300,
        proposedStopLoss: 3290,
      }),
    ).toEqual({ accepted: false, reason: 'INVALID_REQUEST' });
  });

  it('rejects non-finite prices', () => {
    expect(
      validatePositionModificationRequest({
        positionId: 'position-1',
        direction: 'BUY',
        currentStopLoss: null,
        proposedStopLoss: Number.NaN,
      }),
    ).toEqual({ accepted: false, reason: 'INVALID_REQUEST' });
  });

  it('blocks modification while broker constraints are unfrozen', () => {
    expect(rejectUntilBrokerConstraintsAreFrozen()).toEqual({
      accepted: false,
      reason: 'BROKER_CONSTRAINTS_UNFROZEN',
    });
  });
});
