import type { PositionDirection } from './PositionManager.js';

export function isFavorableStop(
  direction: PositionDirection,
  currentStopLoss: number,
  proposedStopLoss: number,
): boolean {
  if (!Number.isFinite(currentStopLoss) || !Number.isFinite(proposedStopLoss)) return false;
  return direction === 'BUY'
    ? proposedStopLoss >= currentStopLoss
    : proposedStopLoss <= currentStopLoss;
}
