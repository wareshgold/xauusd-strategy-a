import type { OpenPosition } from './PositionManager.js';

export function isFavorableStop(direction: OpenPosition['direction'], current: number, proposed: number): boolean {
  if (!Number.isFinite(current) || !Number.isFinite(proposed)) return false;
  return direction === 'BUY' ? proposed >= current : proposed <= current;
}

export function clampFavorableStop(
  direction: OpenPosition['direction'],
  current: number,
  proposed: number,
): number | null {
  return isFavorableStop(direction, current, proposed) ? proposed : null;
}