export interface SP2LFourTradeEntryAuditFixture {
  readonly id: 'T1' | 'T2' | 'T3' | 'T4';
  readonly direction: 'BUY' | 'SELL' | 'UNRESOLVED';
  readonly observedEntryPrice: number;
  readonly observedStopPrice: number;
  readonly geometricEntryResolved: false;
  readonly lastSpikeBreakoutRequired: false;
}

/**
 * Source-visible execution records from the four initial trade examples.
 * These fixtures intentionally preserve observed prices without converting
 * them into canonical OHLC geometry.
 */
export const SP2L_FOUR_TRADE_ENTRY_AUDIT_FIXTURES: readonly SP2LFourTradeEntryAuditFixture[] = [
  { id: 'T1', direction: 'UNRESOLVED', observedEntryPrice: 3229.08, observedStopPrice: 3237.73, geometricEntryResolved: false, lastSpikeBreakoutRequired: false },
  { id: 'T2', direction: 'UNRESOLVED', observedEntryPrice: 3223.84, observedStopPrice: 3235.50, geometricEntryResolved: false, lastSpikeBreakoutRequired: false },
  { id: 'T3', direction: 'UNRESOLVED', observedEntryPrice: 3228.88, observedStopPrice: 3235.50, geometricEntryResolved: false, lastSpikeBreakoutRequired: false },
  { id: 'T4', direction: 'UNRESOLVED', observedEntryPrice: 3232.41, observedStopPrice: 3237.80, geometricEntryResolved: false, lastSpikeBreakoutRequired: false },
];
