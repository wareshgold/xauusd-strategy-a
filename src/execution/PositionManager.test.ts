import { strict as assert } from 'node:assert';
import { describe, it } from 'vitest';
import { evaluateTrailingStop, type OpenPosition } from './PositionManager.js';

const position: OpenPosition = {
  direction: 'BUY',
  entryPrice: 2500,
  stopLoss: 2490,
  takeProfit: 2520,
};

describe('PositionManager trailing-stop boundary', () => {
  it('does not modify the stop when trailing is disabled', () => {
    const disabled = evaluateTrailingStop(position, { enabled: false });
    assert.deepEqual(disabled, {
      action: 'NO_ACTION',
      newStopLoss: null,
      reason: 'TRAILING_DISABLED',
    });
  });

  it('does not modify the stop while trailing parameters are unspecified', () => {
    const unspecified = evaluateTrailingStop(position, { enabled: true });
    assert.deepEqual(unspecified, {
      action: 'NO_ACTION',
      newStopLoss: null,
      reason: 'TRAILING_UNSPECIFIED',
    });
  });
});
