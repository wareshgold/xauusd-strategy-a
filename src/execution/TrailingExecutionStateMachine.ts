import type { PositionDirection } from './PositionManager.js';

export type TrailingExecutionState =
  | 'TRAILING_DISABLED'
  | 'CONTRACT_BLOCKED'
  | 'BROKER_CONSTRAINT_BLOCKED'
  | 'REQUEST_INVALID'
  | 'MODIFICATION_REJECTED'
  | 'MODIFICATION_ACCEPTED';

export interface TrailingExecutionInput {
  readonly enabled: boolean;
  readonly contractFrozen: boolean;
  readonly brokerConstraintsKnown: boolean;
  readonly requestValid: boolean;
  readonly brokerAccepted: boolean;
  readonly direction: PositionDirection;
  readonly currentStopLoss: number;
  readonly proposedStopLoss: number;
}

/**
 * Deterministic execution-state contract only.
 * It does not calculate a trailing stop and does not freeze any trailing
 * distance, activation, step, tick/bar evaluation, or broker constraint.
 */
export function evaluateTrailingExecutionState(
  input: TrailingExecutionInput,
): TrailingExecutionState {
  if (!input.enabled) return 'TRAILING_DISABLED';
  if (!input.contractFrozen) return 'CONTRACT_BLOCKED';
  if (!input.brokerConstraintsKnown) return 'BROKER_CONSTRAINT_BLOCKED';
  if (!input.requestValid) return 'REQUEST_INVALID';

  const favorable = input.direction === 'BUY'
    ? input.proposedStopLoss >= input.currentStopLoss
    : input.proposedStopLoss <= input.currentStopLoss;

  if (!favorable) return 'REQUEST_INVALID';
  return input.brokerAccepted ? 'MODIFICATION_ACCEPTED' : 'MODIFICATION_REJECTED';
}
