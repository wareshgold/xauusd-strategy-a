import type { Candle } from '../market/Candle.js';
import type { Correction } from './CorrectionDetector.js';
import type { EntryTrigger } from './EntryTrigger.js';

export interface StructureStopLoss {
  readonly direction: 'BUY' | 'SELL';
  readonly entryPrice: number;
  readonly stopLoss: number;
  readonly riskDistance: number;
  readonly structureReference: number;
}

/**
 * Structure-based SL. No fixed pip/point distance is introduced.
 * A small configurable buffer can be applied later only after backtest validation.
 */
export function calculateStructureStopLoss(
  entry: EntryTrigger,
  correction: Correction,
  buffer: number = 0,
): StructureStopLoss {
  if (buffer < 0 || !Number.isFinite(buffer)) throw new Error('SL buffer must be a non-negative finite number');
  const sl = entry.direction === 'BUY'
    ? correction.extremePrice - buffer
    : correction.extremePrice + buffer;
  return {
    direction: entry.direction,
    entryPrice: entry.entryPrice,
    stopLoss: sl,
    riskDistance: Math.abs(entry.entryPrice - sl),
    structureReference: correction.extremePrice,
  };
}
