import { describe, expect, it } from 'vitest';
import { buildMt5PositionModification } from './Mt5PositionAdapter.js';
import type { OpenPosition } from '../PositionManager.js';
import { UNFROZEN_TRAILING_CONTRACT } from '../TrailingStopContract.js';

const buy: OpenPosition = {
  direction: 'BUY',
  entryPrice: 2500,
  stopLoss: 2490,
  takeProfit: 2520,
};

const sell: OpenPosition = {
  direction: 'SELL',
  entryPrice: 2500,
  stopLoss: 2510,
  takeProfit: 2480,
};

describe('MT5 position adapter boundary', () => {
  it('emits no request while execution is disabled', () => {
    expect(buildMt5PositionModification(buy, '1', 2495, UNFROZEN_TRAILING_CONTRACT)).toEqual({
      accepted: false,
      request: null,
      reason: 'EXECUTION_DISABLED',
    });
  });

  it('emits no request while the contract is unfrozen', () => {
    expect(buildMt5PositionModification(buy, '1', 2495, {
      ...UNFROZEN_TRAILING_CONTRACT,
      enabled: true,
    })).toEqual({
      accepted: false,
      request: null,
      reason: 'CONTRACT_UNFROZEN',
    });
  });

  it('rejects a proposed BUY stop that loosens protection', () => {
    const contract = {
      ...UNFROZEN_TRAILING_CONTRACT,
      enabled: true,
      distancePrice: 1,
      activationPrice: 2501,
      stepPrice: 0.1,
      evaluation: 'FROZEN' as const,
      brokerConstraints: 'FROZEN' as const,
    };

    expect(buildMt5PositionModification(buy, '1', 2489, contract)).toEqual({
      accepted: false,
      request: null,
      reason: 'NO_MODIFICATION',
    });
  });

  it('accepts a favorable SELL modification at the adapter boundary', () => {
    const contract = {
      ...UNFROZEN_TRAILING_CONTRACT,
      enabled: true,
      distancePrice: 1,
      activationPrice: 2499,
      stepPrice: 0.1,
      evaluation: 'FROZEN' as const,
      brokerConstraints: 'FROZEN' as const,
    };

    expect(buildMt5PositionModification(sell, '2', 2509, contract)).toEqual({
      accepted: true,
      request: { positionTicket: '2', newStopLoss: 2509 },
      reason: 'MODIFICATION_READY',
    });
  });

  it('rejects non-finite proposed stops and empty tickets', () => {
    const contract = {
      ...UNFROZEN_TRAILING_CONTRACT,
      enabled: true,
      distancePrice: 1,
      activationPrice: 2501,
      stepPrice: 0.1,
      evaluation: 'FROZEN' as const,
      brokerConstraints: 'FROZEN' as const,
    };

    expect(buildMt5PositionModification(buy, '', 2495, contract).reason).toBe('INVALID_INPUT');
    expect(buildMt5PositionModification(buy, '1', Number.NaN, contract).reason).toBe('INVALID_INPUT');
  });
});
