export type SP2LRealTradeEntryHypothesis =
  | 'RELEVANT_PREVIOUS_HIGH'
  | 'FIRST_CORRECTION_HIGH'
  | 'SPIKE_ORIGIN_HIGH'
  | 'BODY_EDGE'
  | 'FIXED_BUFFER';

export interface SP2LRealTradeEntryHypothesisFixture {
  readonly tradeId: 'T1' | 'T2' | 'T3' | 'T4';
  readonly observedEntry: number;
  readonly hypothesis: SP2LRealTradeEntryHypothesis;
  readonly sourceSupported: boolean;
  readonly executableFormulaResolved: false;
}

/** Research-only: candidate Entry interpretations remain unresolved. */
export const SP2L_REAL_TRADE_ENTRY_CANDLE_HYPOTHESES: readonly SP2LRealTradeEntryHypothesisFixture[] = [
  ...(['T1', 'T2', 'T3', 'T4'] as const).flatMap((tradeId) => {
    const observedEntry = ({
      T1: 3229.08,
      T2: 3223.84,
      T3: 3228.88,
      T4: 3232.41,
    } as const)[tradeId];
    return (['RELEVANT_PREVIOUS_HIGH', 'FIRST_CORRECTION_HIGH', 'SPIKE_ORIGIN_HIGH', 'BODY_EDGE', 'FIXED_BUFFER'] as const).map(
      (hypothesis) => ({
        tradeId,
        observedEntry,
        hypothesis,
        sourceSupported: hypothesis === 'RELEVANT_PREVIOUS_HIGH',
        executableFormulaResolved: false as const,
      }),
    );
  }),
];
