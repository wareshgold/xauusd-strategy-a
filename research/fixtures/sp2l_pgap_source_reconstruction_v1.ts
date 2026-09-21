/**
 * SP2L P-Gap source-reconstruction synthetic fixtures — 2026-09-21.
 *
 * Research-only. These fixtures isolate the source-discriminated adjacent-candle
 * non-overlap primitive from the still-unresolved P-Gap qualification layer.
 *
 * Source-derived primitive:
 *   bullish: High[i] < Low[i+1]
 *   bearish: Low[i] > High[i+1]
 *
 * The fixtures intentionally do not freeze sequence/indexing, gap threshold,
 * early-trend definition, breakout relation, or E-Gap exclusion as canonical.
 */

export type PgapDirection = "bullish" | "bearish";

export interface PgapCandle {
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface PgapFixture {
  id: string;
  variant:
    | "breakout-follow-through-gap"
    | "higher-lows-gap"
    | "three-candle-spike"
    | "overlap-negative"
    | "equality-negative"
    | "late-extension-negative"
    | "fixed-index-negative"
    | "bearish-mirror";
  direction: PgapDirection;
  candles: readonly PgapCandle[];
  gapPair: readonly [number, number];
  expectedPrimitive: boolean;
  canonicalEligible: false;
  qualificationStatus: "UNRESOLVED";
  note: string;
}

export function bullishGapPrimitive(a: PgapCandle, b: PgapCandle): boolean {
  return a.high < b.low;
}

export function bearishGapPrimitive(a: PgapCandle, b: PgapCandle): boolean {
  return a.low > b.high;
}

const c = (open: number, high: number, low: number, close: number): PgapCandle => ({
  open, high, low, close,
});

export const PGAP_SOURCE_FIXTURES: readonly PgapFixture[] = [
  {
    id: "PGAP-001",
    variant: "breakout-follow-through-gap",
    direction: "bullish",
    candles: [
      c(100, 103, 99, 102),
      c(102, 108, 101, 107),
      c(107, 109, 106, 108),
      c(108, 112, 109, 111),
    ],
    gapPair: [2, 3],
    expectedPrimitive: true,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Source-described breakout/continuation family; only adjacent non-overlap is tested.",
  },
  {
    id: "PGAP-002",
    variant: "higher-lows-gap",
    direction: "bullish",
    candles: [
      c(100, 104, 99, 103),
      c(103, 107, 102, 106),
      c(106, 110, 105, 109),
      c(109, 113, 111, 112),
    ],
    gapPair: [2, 3],
    expectedPrimitive: true,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Source-described higher-lows-then-gap family.",
  },
  {
    id: "PGAP-003",
    variant: "three-candle-spike",
    direction: "bullish",
    candles: [
      c(100, 104, 99, 103),
      c(103, 109, 102, 108),
      c(108, 112, 107, 111),
      c(111, 116, 113, 115),
    ],
    gapPair: [2, 3],
    expectedPrimitive: true,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Three-candle-related spike construction; exact source indexing remains unresolved.",
  },
  {
    id: "PGAP-004",
    variant: "overlap-negative",
    direction: "bullish",
    candles: [
      c(100, 106, 99, 104),
      c(104, 108, 105, 107),
    ],
    gapPair: [0, 1],
    expectedPrimitive: false,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Overlap invalidates the reconstructed non-overlap primitive.",
  },
  {
    id: "PGAP-005",
    variant: "equality-negative",
    direction: "bullish",
    candles: [
      c(100, 105, 99, 104),
      c(104, 110, 105, 109),
    ],
    gapPair: [0, 1],
    expectedPrimitive: false,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Equality is rejected because source wording describes non-overlap.",
  },
  {
    id: "PGAP-006",
    variant: "late-extension-negative",
    direction: "bullish",
    candles: [
      c(100, 104, 99, 103),
      c(103, 109, 102, 108),
      c(108, 114, 107, 113),
      c(113, 118, 117, 117.5),
    ],
    gapPair: [2, 3],
    expectedPrimitive: true,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Geometric primitive is true, but late/E-Gap qualification is deliberately unresolved.",
  },
  {
    id: "PGAP-007",
    variant: "fixed-index-negative",
    direction: "bullish",
    candles: [
      c(100, 104, 99, 103),
      c(103, 108, 102, 107),
      c(107, 111, 106, 110),
      c(110, 116, 115, 115.5),
    ],
    gapPair: [3, 4],
    expectedPrimitive: true,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Valid primitive outside a fixed [-4,-3,-2] assumption; demonstrates why indexing cannot be frozen from code.",
  },
  {
    id: "PGAP-008",
    variant: "bearish-mirror",
    direction: "bearish",
    candles: [
      c(100, 104, 99, 101),
      c(101, 102, 96, 97),
    ],
    gapPair: [0, 1],
    expectedPrimitive: true,
    canonicalEligible: false,
    qualificationStatus: "UNRESOLVED",
    note: "Bearish mirror is source-consistent but not independently demonstrated in the preserved excerpt.",
  },
] as const;
