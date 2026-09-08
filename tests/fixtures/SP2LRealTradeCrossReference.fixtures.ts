export interface SP2LRealTradeCrossReferenceFixture {
  readonly tradeId: 'T1' | 'T2' | 'T3' | 'T4';
  readonly direction: 'SELL';
  readonly entry: number;
  readonly stop: number;
  readonly target: number;
  readonly observedStructuralEntryContext: 'CORRECTION_PREVIOUS_HIGH_CONTEXT';
  readonly exactEntryCandleResolved: false;
  readonly exactEntryBoundaryResolved: false;
  readonly exactPGAPBoundaryResolved: false;
  readonly exactPGAPCandleResolved: false;
  readonly exactSLBoundaryResolved: false;
}

/**
 * Research-only preservation of the four XAUUSD trades visible in the
 * authoritative source recording. These observations must not be converted
 * into executable geometry without additional source evidence.
 */
export const SP2L_REAL_TRADE_CROSS_REFERENCE_FIXTURES: readonly SP2LRealTradeCrossReferenceFixture[] = [
  { tradeId: 'T1', direction: 'SELL', entry: 3229.08, stop: 3237.73, target: 0, observedStructuralEntryContext: 'CORRECTION_PREVIOUS_HIGH_CONTEXT', exactEntryCandleResolved: false, exactEntryBoundaryResolved: false, exactPGAPBoundaryResolved: false, exactPGAPCandleResolved: false, exactSLBoundaryResolved: false },
  { tradeId: 'T2', direction: 'SELL', entry: 3223.84, stop: 3235.50, target: 3213.37, observedStructuralEntryContext: 'CORRECTION_PREVIOUS_HIGH_CONTEXT', exactEntryCandleResolved: false, exactEntryBoundaryResolved: false, exactPGAPBoundaryResolved: false, exactPGAPCandleResolved: false, exactSLBoundaryResolved: false },
  { tradeId: 'T3', direction: 'SELL', entry: 3228.88, stop: 3235.50, target: 3213.37, observedStructuralEntryContext: 'CORRECTION_PREVIOUS_HIGH_CONTEXT', exactEntryCandleResolved: false, exactEntryBoundaryResolved: false, exactPGAPBoundaryResolved: false, exactPGAPCandleResolved: false, exactSLBoundaryResolved: false },
  { tradeId: 'T4', direction: 'SELL', entry: 3232.41, stop: 3237.80, target: 0, observedStructuralEntryContext: 'CORRECTION_PREVIOUS_HIGH_CONTEXT', exactEntryCandleResolved: false, exactEntryBoundaryResolved: false, exactPGAPBoundaryResolved: false, exactPGAPCandleResolved: false, exactSLBoundaryResolved: false },
];
