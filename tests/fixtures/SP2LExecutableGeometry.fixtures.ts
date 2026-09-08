export type Direction = 'BULLISH' | 'BEARISH';

export interface GeometryFixture {
  readonly id: string;
  readonly purpose: string;
  readonly direction: Direction;
  readonly candles: readonly {
    readonly open: number;
    readonly high: number;
    readonly low: number;
    readonly close: number;
  }[];
  readonly competingInterpretations: readonly string[];
  readonly expectedResolution: 'DISCRIMINATE' | 'UNRESOLVED';
}

export const SP2L_EXECUTABLE_GEOMETRY_FIXTURES: readonly GeometryFixture[] = [
  {
    id: 'ENTRY-BULL-MULTI-LOW',
    purpose: 'Multiple prior lows exist; fixture must not silently choose an executable entry anchor.',
    direction: 'BULLISH',
    candles: [
      { open: 100, high: 102, low: 99, close: 101 },
      { open: 101, high: 105, low: 100, close: 104 },
      { open: 104, high: 108, low: 103, close: 107 },
      { open: 107, high: 108, low: 102, close: 103 },
    ],
    competingInterpretations: ['immediately previous low', 'Spike-origin low', 'most recent relevant structural low'],
    expectedResolution: 'UNRESOLVED',
  },
  {
    id: 'ENTRY-BEAR-MULTI-HIGH',
    purpose: 'Bearish mirror of multiple candidate highs.',
    direction: 'BEARISH',
    candles: [
      { open: 100, high: 101, low: 98, close: 99 },
      { open: 99, high: 100, low: 95, close: 96 },
      { open: 96, high: 97, low: 92, close: 93 },
      { open: 93, high: 98, low: 92, close: 97 },
    ],
    competingInterpretations: ['immediately previous high', 'Spike-origin high', 'most recent relevant structural high'],
    expectedResolution: 'UNRESOLVED',
  },
  {
    id: 'SL-BULL-WICK-BODY',
    purpose: 'Origin candle wick and body imply different executable stop prices.',
    direction: 'BULLISH',
    candles: [
      { open: 100, high: 101, low: 96, close: 100.5 },
      { open: 100.5, high: 105, low: 100, close: 104 },
      { open: 104, high: 108, low: 103, close: 107 },
    ],
    competingInterpretations: ['origin low/wick', 'origin body boundary', 'origin structural invalidation level'],
    expectedResolution: 'UNRESOLVED',
  },
  {
    id: 'SL-BEAR-WICK-BODY',
    purpose: 'Bearish mirror of origin wick/body ambiguity.',
    direction: 'BEARISH',
    candles: [
      { open: 100, high: 104, low: 99, close: 99.5 },
      { open: 99.5, high: 100, low: 95, close: 96 },
      { open: 96, high: 97, low: 92, close: 93 },
    ],
    competingInterpretations: ['origin high/wick', 'origin body boundary', 'origin structural invalidation level'],
    expectedResolution: 'UNRESOLVED',
  },
  {
    id: 'LEG1-BULL-ANCHOR-COMPETITION',
    purpose: 'Separates Spike-origin-to-extreme from breakout-to-extreme and structural-anchor candidates.',
    direction: 'BULLISH',
    candles: [
      { open: 100, high: 101, low: 99, close: 100 },
      { open: 100, high: 103, low: 100, close: 102 },
      { open: 102, high: 106, low: 102, close: 105 },
      { open: 105, high: 110, low: 104, close: 109 },
      { open: 109, high: 110, low: 105, close: 106 },
    ],
    competingInterpretations: ['Spike-origin → Spike-extreme', 'breakout level → Spike-extreme', 'first structural low → Spike-extreme'],
    expectedResolution: 'UNRESOLVED',
  },
  {
    id: 'LEG1-BEAR-ANCHOR-COMPETITION',
    purpose: 'Bearish mirror of Leg-1 anchor competition.',
    direction: 'BEARISH',
    candles: [
      { open: 100, high: 101, low: 99, close: 100 },
      { open: 100, high: 100, low: 97, close: 98 },
      { open: 98, high: 98, low: 94, close: 95 },
      { open: 95, high: 96, low: 90, close: 91 },
      { open: 91, high: 95, low: 90, close: 94 },
    ],
    competingInterpretations: ['Spike-origin → Spike-extreme', 'breakout level → Spike-extreme', 'first structural high → Spike-extreme'],
    expectedResolution: 'UNRESOLVED',
  },
  {
    id: 'ABCD-EXACT-VS-TOLERANCE',
    purpose: 'Exact equal legs are distinguishable from near-equal legs, but source does not define a tolerance.',
    direction: 'BULLISH',
    candles: [
      { open: 100, high: 101, low: 99, close: 100 },
      { open: 100, high: 106, low: 100, close: 105 },
      { open: 105, high: 105, low: 102, close: 103 },
      { open: 103, high: 109, low: 103, close: 108 },
    ],
    competingInterpretations: ['exact AB = CD', 'near-equality with unspecified tolerance'],
    expectedResolution: 'UNRESOLVED',
  },
];
