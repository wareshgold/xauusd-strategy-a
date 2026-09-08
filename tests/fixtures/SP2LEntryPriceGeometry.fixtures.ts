export type EntryPriceGeometryHypothesis =
  | 'H1_PREVIOUS_CANDLE_EXTREME'
  | 'H2_FIRST_CORRECTION_CANDLE_EXTREME'
  | 'H3_SPIKE_ORIGIN_EXTREME'
  | 'H4_PREVIOUS_CANDLE_BODY_EDGE'
  | 'H5_FIRST_CORRECTION_CANDLE_BODY_EDGE';

export interface SP2LEntryPriceGeometryFixture {
  readonly id: string;
  readonly direction: 'BUY' | 'SELL';
  readonly description: string;
  readonly sourceSemantic: 'PENDING_LIMIT_DURING_CORRECTION';
  readonly discriminates: readonly EntryPriceGeometryHypothesis[];
  readonly expectedHypothesisValues: Readonly<Record<EntryPriceGeometryHypothesis, 'MATCH' | 'MISMATCH' | 'UNRESOLVED'>>;
}

/**
 * Research-only fixtures for resolving the exact executable entry level.
 *
 * These fixtures intentionally describe relative candle geometry rather than
 * assigning a canonical price. The source confirms the correction reference
 * semantically, but not the exact OHLC anchor/body-vs-wick convention.
 */
export const SP2L_ENTRY_PRICE_GEOMETRY_FIXTURES: readonly SP2LEntryPriceGeometryFixture[] = [
  {
    id: 'EPG-BUY-DISTINCT-ALL-EXTREMES',
    direction: 'BUY',
    description: 'Previous candle low, first correction low, and Spike-origin low are deliberately separated.',
    sourceSemantic: 'PENDING_LIMIT_DURING_CORRECTION',
    discriminates: ['H1_PREVIOUS_CANDLE_EXTREME', 'H2_FIRST_CORRECTION_CANDLE_EXTREME', 'H3_SPIKE_ORIGIN_EXTREME'],
    expectedHypothesisValues: {
      H1_PREVIOUS_CANDLE_EXTREME: 'UNRESOLVED',
      H2_FIRST_CORRECTION_CANDLE_EXTREME: 'UNRESOLVED',
      H3_SPIKE_ORIGIN_EXTREME: 'UNRESOLVED',
      H4_PREVIOUS_CANDLE_BODY_EDGE: 'UNRESOLVED',
      H5_FIRST_CORRECTION_CANDLE_BODY_EDGE: 'UNRESOLVED',
    },
  },
  {
    id: 'EPG-SELL-DISTINCT-ALL-EXTREMES',
    direction: 'SELL',
    description: 'Previous candle high, first correction high, and Spike-origin high are deliberately separated.',
    sourceSemantic: 'PENDING_LIMIT_DURING_CORRECTION',
    discriminates: ['H1_PREVIOUS_CANDLE_EXTREME', 'H2_FIRST_CORRECTION_CANDLE_EXTREME', 'H3_SPIKE_ORIGIN_EXTREME'],
    expectedHypothesisValues: {
      H1_PREVIOUS_CANDLE_EXTREME: 'UNRESOLVED',
      H2_FIRST_CORRECTION_CANDLE_EXTREME: 'UNRESOLVED',
      H3_SPIKE_ORIGIN_EXTREME: 'UNRESOLVED',
      H4_PREVIOUS_CANDLE_BODY_EDGE: 'UNRESOLVED',
      H5_FIRST_CORRECTION_CANDLE_BODY_EDGE: 'UNRESOLVED',
    },
  },
  {
    id: 'EPG-BUY-WICK-BODY-DISCRIMINATION',
    direction: 'BUY',
    description: 'Previous candle low is separated from its body edge so wick-vs-body semantics can be distinguished.',
    sourceSemantic: 'PENDING_LIMIT_DURING_CORRECTION',
    discriminates: ['H1_PREVIOUS_CANDLE_EXTREME', 'H4_PREVIOUS_CANDLE_BODY_EDGE'],
    expectedHypothesisValues: {
      H1_PREVIOUS_CANDLE_EXTREME: 'UNRESOLVED',
      H2_FIRST_CORRECTION_CANDLE_EXTREME: 'UNRESOLVED',
      H3_SPIKE_ORIGIN_EXTREME: 'UNRESOLVED',
      H4_PREVIOUS_CANDLE_BODY_EDGE: 'UNRESOLVED',
      H5_FIRST_CORRECTION_CANDLE_BODY_EDGE: 'UNRESOLVED',
    },
  },
  {
    id: 'EPG-SELL-WICK-BODY-DISCRIMINATION',
    direction: 'SELL',
    description: 'Previous candle high is separated from its body edge so wick-vs-body semantics can be distinguished.',
    sourceSemantic: 'PENDING_LIMIT_DURING_CORRECTION',
    discriminates: ['H1_PREVIOUS_CANDLE_EXTREME', 'H4_PREVIOUS_CANDLE_BODY_EDGE'],
    expectedHypothesisValues: {
      H1_PREVIOUS_CANDLE_EXTREME: 'UNRESOLVED',
      H2_FIRST_CORRECTION_CANDLE_EXTREME: 'UNRESOLVED',
      H3_SPIKE_ORIGIN_EXTREME: 'UNRESOLVED',
      H4_PREVIOUS_CANDLE_BODY_EDGE: 'UNRESOLVED',
      H5_FIRST_CORRECTION_CANDLE_BODY_EDGE: 'UNRESOLVED',
    },
  },
  {
    id: 'EPG-BUY-NEW-CORRECTION-LOW',
    direction: 'BUY',
    description: 'A later correction candle makes a new low below the first correction candle while remaining above invalidation.',
    sourceSemantic: 'PENDING_LIMIT_DURING_CORRECTION',
    discriminates: ['H1_PREVIOUS_CANDLE_EXTREME', 'H2_FIRST_CORRECTION_CANDLE_EXTREME'],
    expectedHypothesisValues: {
      H1_PREVIOUS_CANDLE_EXTREME: 'UNRESOLVED',
      H2_FIRST_CORRECTION_CANDLE_EXTREME: 'UNRESOLVED',
      H3_SPIKE_ORIGIN_EXTREME: 'UNRESOLVED',
      H4_PREVIOUS_CANDLE_BODY_EDGE: 'UNRESOLVED',
      H5_FIRST_CORRECTION_CANDLE_BODY_EDGE: 'UNRESOLVED',
    },
  },
];
