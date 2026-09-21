import type { PositionDirection } from '../PositionManager.js';
export interface PositionModificationRequest {
  readonly positionId: string;
  readonly direction: PositionDirection;
  readonly currentStopLoss: number | null;
  readonly proposedStopLoss: number;
}
export interface PositionModificationResult { readonly accepted: boolean; readonly reason: string; }
export function validatePositionModificationRequest(request: PositionModificationRequest): PositionModificationResult {
  if (!request.positionId || !Number.isFinite(request.proposedStopLoss)) return { accepted: false, reason: 'INVALID_REQUEST' };
  if (request.currentStopLoss !== null && !Number.isFinite(request.currentStopLoss)) return { accepted: false, reason: 'INVALID_CURRENT_STOP' };
  return { accepted: true, reason: 'VALID' };
}
