/**
 * SP2L source-discrimination fixtures — Entry / SL / 2X / Trigger / AB=CD.
 *
 * Research infrastructure only. These fixtures deliberately preserve competing
 * interpretations instead of selecting a canonical executable rule.
 */

export type Direction = "bullish" | "bearish";

export type TriggerForm =
  | "one-candle"
  | "two-candle"
  | "three-candle"
  | "bar"
  | "key-bar";

export type AnchorKind = "wick" | "body" | "structural-pivot";

export interface OHLC {
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface SourceDiscriminationFixture {
  id: string;
  question: string;
  sourceEvidence: string[];
  competingInterpretations: string[];
  canonicalStatus: "UNRESOLVED" | "PARTIAL";
}

export const ENTRY_SL_2X_TRIGGER_ABCD_FIXTURES: readonly SourceDiscriminationFixture[] = [
  {
    id: "F09-entry-anchor-vs-leg2-start",
    question: "Does the first entry anchor equal the start of Leg 2?",
    sourceEvidence: [
      "Correction can lead to a Limit order placed inside the initial structure.",
      "The source separately describes the later second leg and target completion.",
    ],
    competingInterpretations: [
      "entry-price is the Leg-2 start",
      "entry-price is distinct from the Leg-2 start",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F10-stop-anchor",
    question: "Which exact price defines the executable stop?",
    sourceEvidence: [
      "Return to the referenced invalidation level invalidates the setup.",
      "Exact OHLC stop anchor and numeric buffer are not specified.",
    ],
    competingInterpretations: [
      "structural invalidation price",
      "risk-budget-derived stop",
      "wick/body variant of the referenced level",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F11-limit-refresh",
    question: "When must a pending Limit be replaced after a new candle?",
    sourceEvidence: [
      "The source permits deleting and replacing the order when stop distance changes.",
    ],
    competingInterpretations: [
      "refresh whenever the relevant distance changes",
      "refresh only after a material change",
      "retain the original order unless an explicitly stated condition occurs",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F12-trigger-family",
    question: "Is there one fixed candle trigger or a broader trigger family?",
    sourceEvidence: [
      "The source describes one-, two-, and three-candle structures.",
      "Bar and key-bar confirmation variants are also described.",
    ],
    competingInterpretations: [
      "one-candle confirmation",
      "two-candle confirmation",
      "three-candle confirmation",
      "bar confirmation",
      "key-bar confirmation",
    ],
    canonicalStatus: "PARTIAL",
  },
  {
    id: "F13-2x-anchor",
    question: "What exact anchor is used for the approximately half-target 2X entry?",
    sourceEvidence: [
      "The source describes an optional second position.",
      "The source describes the second position at approximately half the target distance.",
    ],
    competingInterpretations: [
      "half the target distance measured from initial entry",
      "half the target distance measured from a structural reference",
      "another source-defined anchor not explicitly recoverable from the transcript",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F14-abcd-anchor",
    question: "Which exact A/B/C/D anchors implement the AB=CD concept?",
    sourceEvidence: [
      "SP2L is explicitly linked to AB=CD.",
      "The second leg is expected to become equal to the first leg.",
    ],
    competingInterpretations: [
      "wick-based A/B/C/D",
      "body-based A/B/C/D",
      "structural-pivot A/B/C/D",
    ],
    canonicalStatus: "UNRESOLVED",
  },
];

export const TRIGGER_FORMS: readonly TriggerForm[] = [
  "one-candle",
  "two-candle",
  "three-candle",
  "bar",
  "key-bar",
];

export const DISCRIMINATION_OHLC: readonly OHLC[] = [
  { open: 100, high: 108, low: 99, close: 106 },
  { open: 106, high: 112, low: 104, close: 111 },
  { open: 111, high: 115, low: 109, close: 114 },
];

export function halfTargetCandidates(
  entry: number,
  structuralAnchor: number,
  target: number,
): Readonly<{ fromEntry: number; fromStructuralAnchor: number }> {
  return {
    fromEntry: entry + (target - entry) / 2,
    fromStructuralAnchor: structuralAnchor + (target - structuralAnchor) / 2,
  };
}

export function abcdMagnitude(start: number, end: number): number {
  return Math.abs(end - start);
}

export function abcdEqualityObservation(
  leg1Start: number,
  leg1End: number,
  leg2Start: number,
  leg2End: number,
): boolean {
  return abcdMagnitude(leg1Start, leg1End) === abcdMagnitude(leg2Start, leg2End);
}

export function candidateAnchors(
  values: Record<string, number>,
  kind: AnchorKind,
): readonly [number, number, number, number] {
  if (kind === "wick") {
    return [values.A_wick, values.B_wick, values.C_wick, values.D_wick];
  }
  if (kind === "body") {
    return [values.A_body, values.B_body, values.C_body, values.D_body];
  }
  return [values.A_pivot, values.B_pivot, values.C_pivot, values.D_pivot];
}

export function entryAndLeg2AreDistinct(entry: number, leg2Start: number): boolean {
  return entry !== leg2Start;
}
