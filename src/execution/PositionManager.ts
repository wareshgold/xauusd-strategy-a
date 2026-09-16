export type PositionDirection = 'BUY' | 'SELL';

export interface OpenPosition {
  readonly direction: PositionDirection;
  readonly entryPrice: number;
  readonly stopLoss: number;
  readonly takeProfit: number | null;
}

export interface TrailingStopConfig {
  readonly enabled: boolean;
  /** Deliberately unresolved until an explicit execution contract freezes it. */
  readonly distancePrice?: number;
  readonly activationPrice?: number;
  readonly stepPrice?: number;
}

export interface PositionManagerDecision {
  readonly action: 'NO_ACTION' | 'MODIFY_SL';
  readonly newStopLoss: number | null;
  readonly reason: 'TRAILING_DISABLED' | 'TRAILING_UNSPECIFIED';
}

/**
 * Execution-layer boundary only. It intentionally performs no trailing
 * calculation while trailing parameters remain unresolved.
 */
export function evaluateTrailingStop(
  _position: OpenPosition,
  config: TrailingStopConfig,
): PositionManagerDecision {
  if (!config.enabled) {
    return { action: 'NO_ACTION', newStopLoss: null, reason: 'TRAILING_DISABLED' };
  }

  if (!Number.isFinite(config.distancePrice) || (config.distancePrice ?? 0) <= 0) {
    return { action: 'NO_ACTION', newStopLoss: null, reason: 'TRAILING_UNSPECIFIED' };
  }

  // Activation/step semantics are intentionally not implemented yet.
  return { action: 'NO_ACTION', newStopLoss: null, reason: 'TRAILING_UNSPECIFIED' };
}