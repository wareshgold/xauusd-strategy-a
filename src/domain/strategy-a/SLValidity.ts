import type { Correction } from './CorrectionDetector.js';
import type { EntryTrigger } from './EntryTrigger.js';
import type { StructureStopLoss } from './StructureStopLoss.js';

export interface SLValidity {
  readonly valid: boolean;
  readonly reason: 'VALID' | 'ENTRY_ON_WRONG_SIDE' | 'NON_POSITIVE_RISK';
}

/**
 * Validates geometry only. It does not introduce a fixed pip/point threshold.
 * The entry must remain on the tradable side of the structural invalidation,
 * and the resulting distance must be strictly positive.
 */
export function validateStructureSL(
  entry: EntryTrigger,
  correction: Correction,
  sl: StructureStopLoss,
): SLValidity {
  const onTradableSide = entry.direction === 'BUY'
    ? entry.entryPrice > correction.extremePrice && sl.stopLoss < entry.entryPrice
    : entry.entryPrice < correction.extremePrice && sl.stopLoss > entry.entryPrice;

  if (!onTradableSide) return { valid: false, reason: 'ENTRY_ON_WRONG_SIDE' };
  if (!(sl.riskDistance > 0) || !Number.isFinite(sl.riskDistance)) {
    return { valid: false, reason: 'NON_POSITIVE_RISK' };
  }
  return { valid: true, reason: 'VALID' };
}
