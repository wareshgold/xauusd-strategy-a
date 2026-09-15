import { strict as assert } from 'node:assert';
import { evaluateTrailingStop, type OpenPosition } from './PositionManager.js';

const position: OpenPosition = {
  direction: 'BUY',
  entryPrice: 2500,
  stopLoss: 2490,
  takeProfit: 2520,
};

const disabled = evaluateTrailingStop(position, { enabled: false });
assert.deepEqual(disabled, {
  action: 'NO_ACTION',
  newStopLoss: null,
  reason: 'TRAILING_DISABLED',
});

const unspecified = evaluateTrailingStop(position, { enabled: true });
assert.deepEqual(unspecified, {
  action: 'NO_ACTION',
  newStopLoss: null,
  reason: 'TRAILING_UNSPECIFIED',
});

console.log('PositionManager trailing-stop boundary tests: PASS');
