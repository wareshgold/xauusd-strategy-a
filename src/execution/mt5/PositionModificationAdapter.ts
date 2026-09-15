import type { PositionDirection } from '../PositionManager.js';

export interface PositionModificationRequest {
  readonly positionId: string;
  readonly direction: PositionDirection;
  readonly currentStopLoss: number | null;
  readonly proposedStopLoss: number;
}

export type PositionModificationResult =
  | { readonly accepted: true }
  | {
      readonly accepted: false;
      readonly reason:
        | 'INVALID_REQUEST'
        | 'BROKER_CONSTRAINTS_UNFROZEN'
        | 'BROKER_REJECTED';
    };

export interface Mt5PositionModificationAdapter {
  modifyStopLoss(
    request: PositionModificationRequest,
  ): PositionModificationResult;
}

export function validatePositionModificationRequest(
  request: PositionModificationRequest,
): PositionModificationResult {
  if (
    request.positionId.trim().length === 0 ||
    !Number.isFinite(request.proposedStopLoss) ||
    (request.currentStopLoss !== null && !Number.isFinite(request.currentStopLoss))
  ) {
    return { accepted: false, reason: 'INVALID_REQUEST' };
  }

  return { accepted: true };
}

export function rejectUntilBrokerConstraintsAreFrozen(): PositionModificationResult {
  return { accepted: false, reason: 'BROKER_CONSTRAINTS_UNFROZEN' };
}
