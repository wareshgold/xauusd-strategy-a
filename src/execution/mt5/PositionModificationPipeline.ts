import { isFavorableStop } from '../TrailingStopSafety.js';
import { evaluateBrokerConstraintState } from './BrokerConstraintEvaluation.js';
import type { BrokerConstraintState } from './BrokerConstraintGate.js';
import { evaluateTrailingExecutionState, type TrailingExecutionInput, type TrailingExecutionState } from '../TrailingExecutionStateMachine.js';
import { validatePositionModificationRequest, type PositionModificationRequest, type PositionModificationResult } from './PositionModificationAdapter.js';

export interface PositionModificationPipelineInput {
  readonly trailingEnabled: boolean;
  readonly contractFrozen: boolean;
  readonly brokerConstraints: BrokerConstraintState;
  readonly request: PositionModificationRequest;
  readonly brokerAccepted: boolean;
}

export function evaluatePositionModificationPipeline(
  input: PositionModificationPipelineInput,
): TrailingExecutionState {
  const requestValidation = validatePositionModificationRequest(input.request);
  const brokerConstraintDecision = evaluateBrokerConstraintState(input.brokerConstraints);
  const brokerConstraintsKnown = brokerConstraintDecision === 'BROKER_CONSTRAINTS_VALID';
  const requestValid = requestValidation.accepted &&
    input.request.currentStopLoss !== null &&
    isFavorableStop(
      input.request.direction,
      input.request.currentStopLoss,
      input.request.proposedStopLoss,
    );

  const stateInput: TrailingExecutionInput = {
    enabled: input.trailingEnabled,
    contractFrozen: input.contractFrozen,
    brokerConstraintsKnown,
    requestValid,
    brokerAccepted: input.brokerAccepted,
    direction: input.request.direction,
    currentStopLoss: input.request.currentStopLoss ?? Number.NaN,
    proposedStopLoss: input.request.proposedStopLoss,
  };

  return evaluateTrailingExecutionState(stateInput);
}

export type { PositionModificationResult };
