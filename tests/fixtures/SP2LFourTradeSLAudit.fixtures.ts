export interface SP2LFourTradeSLAuditFixture {
  readonly id: 'T1' | 'T2' | 'T3' | 'T4';
  readonly observedEntryPrice: number;
  readonly observedStopPrice: number;
  readonly observedRiskDistance: number;
  readonly stopSemantic: 'BEHIND_SPIKE_ORIGIN_CANDLE';
  readonly exactStopBoundaryResolved: false;
  readonly fixedBufferResolved: false;
}

/**
 * Source-visible execution records preserved as observations only.
 * These fixtures intentionally do not encode a canonical OHLC stop formula.
 */
export const SP2L_FOUR_TRADE_SL_AUDIT_FIXTURES: readonly SP2LFourTradeSLAuditFixture[] = [
  { id: 'T1', observedEntryPrice: 3229.08, observedStopPrice: 3237.73, observedRiskDistance: 8.65, stopSemantic: 'BEHIND_SPIKE_ORIGIN_CANDLE', exactStopBoundaryResolved: false, fixedBufferResolved: false },
  { id: 'T2', observedEntryPrice: 3223.84, observedStopPrice: 3235.50, observedRiskDistance: 11.66, stopSemantic: 'BEHIND_SPIKE_ORIGIN_CANDLE', exactStopBoundaryResolved: false, fixedBufferResolved: false },
  { id: 'T3', observedEntryPrice: 3228.88, observedStopPrice: 3235.50, observedRiskDistance: 6.62, stopSemantic: 'BEHIND_SPIKE_ORIGIN_CANDLE', exactStopBoundaryResolved: false, fixedBufferResolved: false },
  { id: 'T4', observedEntryPrice: 3232.41, observedStopPrice: 3237.80, observedRiskDistance: 5.39, stopSemantic: 'BEHIND_SPIKE_ORIGIN_CANDLE', exactStopBoundaryResolved: false, fixedBufferResolved: false },
];
