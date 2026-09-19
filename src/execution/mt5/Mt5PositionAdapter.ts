import type { OpenPosition } from '../PositionManager.js';
import type { TrailingStopExecutionContract } from '../TrailingStopContract.js';

export interface Mt5PositionModificationRequest {
  readonly positionTicket: string;
  readonly newStopLoss: number;
}

export interface Mt5PositionModificationResult {
  readonly accepted: boolean;
  readonly request: Mt5PositionModificationRequest | null;
  readonly reason:
    | 'EXECUTION_DISABLED'
    | 'CONTRACT_UNFROZEN'
    | 'INVALID_INPUT'
    | 'NO_MODIFICATION'
    | 'MODIFICATION_READY';
}

export function buildMt5PositionModification(
  position: OpenPosition,
  positionTicket: string,
  proposedStopLoss: number | null,
  contract: TrailingStopExecutionContract,
): Mt5PositionModificationResult {
  if (!contract.enabled) {
    return { accepted: false, request: null, reason: 'EXECUTION_DISABLED' };
  }

  if (
    contract.evaluation === 'UNFROZEN' ||
    contract.brokerConstraints === 'UNFROZEN' ||
    contract.distancePrice === null ||
    contract.activationPrice === null ||
    contract.stepPrice === null
  ) {
    return { accepted: false, request: null, reason: 'CONTRACT_UNFROZEN' };
  }

  if (!positionTicket || proposedStopLoss === null || !Number.isFinite(proposedStopLoss)) {
    return { accepted: false, request: null, reason: 'INVALID_INPUT' };
  }

  const favorable = position.direction === 'BUY'
    ? proposedStopLoss >= position.stopLoss
    : proposedStopLoss <= position.stopLoss;

  if (!favorable) {
    return { accepted: false, request: null, reason: 'NO_MODIFICATION' };
  }

  return {
    accepted: true,
    request: { positionTicket, newStopLoss: proposedStopLoss },
    reason: 'MODIFICATION_READY',
  };
}
