import type { BrokerConstraintState } from './BrokerConstraintGate.js';

export type BrokerConstraintDecision =
  | 'BROKER_CONSTRAINT_BLOCKED'
  | 'BROKER_CONSTRAINTS_VALID';

export function evaluateBrokerConstraintState(
  state: BrokerConstraintState,
): BrokerConstraintDecision {
  if (!state.known) return 'BROKER_CONSTRAINT_BLOCKED';
  if (state.minimumStopDistancePrice === null || state.freezeDistancePrice === null) {
    return 'BROKER_CONSTRAINT_BLOCKED';
  }
  if (!Number.isFinite(state.minimumStopDistancePrice) || !Number.isFinite(state.freezeDistancePrice)) {
    return 'BROKER_CONSTRAINT_BLOCKED';
  }
  if (state.minimumStopDistancePrice < 0 || state.freezeDistancePrice < 0) {
    return 'BROKER_CONSTRAINT_BLOCKED';
  }
  return 'BROKER_CONSTRAINTS_VALID';
}
