import type { PositionDirection } from './PositionManager.js';
export function isFavorableStop(direction: PositionDirection, currentStopLoss: number, proposedStopLoss: number): boolean {
  return direction === 'BUY' ? proposedStopLoss >= currentStopLoss : proposedStopLoss <= currentStopLoss;
}
