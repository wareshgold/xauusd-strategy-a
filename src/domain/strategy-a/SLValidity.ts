import type { Correction } from './CorrectionDetector.js';
import type { EntryTrigger } from './EntryTrigger.js';
import type { StructureStopLoss } from './StructureStopLoss.js';

export interface SLValidity {
  readonly valid: boolean;
  readonly reason: 'VALID' | 'ENTRY_ON_WRONG_SIDE' | 'NON_POSITIVE_RISK';
}

/**
 * Validates geometry only. It does not introduce a fixed pip/point threshold.
 * Risk validity is checked first so malformed/non-positive risk is reported
 * deterministically regardless of the other geometry fields.
 */
export function validateStructureSL(
  entry: EntryTrigger,
  correction: Correction,
  sl: StructureStopLoss,
): SLValidity {
  if (!(sl.riskDistance > 0) || !Number.isFinite(sl.riskDistance)) {
    return { valid: false, reason: 'NON_POSITIVE_RISK' };
  }

  const onTradableSide = entry.direction === 'BUY'
    ? entry.entryPrice > correction.extremePrice && sl.stopLoss < entry.entryPrice
    : entry.entryPrice < correction.extremePrice && sl.stopLoss > entry.entryPrice;

  if (!onTradableSide) return { valid: false, reason: 'ENTRY_ON_WRONG_SIDE' };
  return { valid: true, reason: 'VALID' };
}
