import type { StructureStopLoss } from './StructureStopLoss.js';

/**
 * A structure SL is valid only when all prices are finite and the stop is
 * strictly on the invalidation side of the entry. No arbitrary minimum
 * distance is imposed here; that requires separate statistical validation.
 */
export function isValidStructureStopLoss(sl: StructureStopLoss): boolean {
  if (!Number.isFinite(sl.entryPrice) || !Number.isFinite(sl.stopLoss)) return false;
  if (!Number.isFinite(sl.riskDistance) || sl.riskDistance <= 0) return false;
  if (!Number.isFinite(sl.structureReference)) return false;

  if (sl.direction === 'BUY') return sl.stopLoss < sl.entryPrice;
  return sl.stopLoss > sl.entryPrice;
}
