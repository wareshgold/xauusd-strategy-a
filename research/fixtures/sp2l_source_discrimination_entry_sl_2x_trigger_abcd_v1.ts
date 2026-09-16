/**
 * SP2L source-discrimination fixtures — Entry / SL / 2X / Trigger / AB=CD.
 *
 * Research infrastructure only. These fixtures deliberately preserve competing
 * interpretations instead of selecting a canonical executable rule.
 *
 * Reconciliation note (2026-09-16): transcript + visual evidence materially
 * narrows several questions, but no F09-F14 field is promoted to canonical
 * executable geometry. Demonstrated bullish visual behavior must not be
 * generalized to every Spike variant without source confirmation.
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
    question: "Does the first entry anchor equal the start of Leg 2, or is the entry tied to a currently relevant structural higher-low?",
    sourceEvidence: [
      "38:38–39:26: correction/Limit-entry sequence is source-described.",
      "38:40–39:50 visual triangulation supports a dynamic/relevant completed higher-low Buy Limit in the demonstrated bullish variant.",
      "The source separately describes the later second leg and target completion.",
    ],
    competingInterpretations: [
      "entry-price is the Leg-2 start",
      "entry-price is the currently relevant completed higher-low",
      "entry-price is another source-defined structural anchor",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F10-stop-anchor",
    question: "Which exact price defines the executable stop?",
    sourceEvidence: [
      "39:26 establishes structural invalidation at the referenced level.",
      "Visual triangulation shows invalidation deeper than the demonstrated pending entry level.",
      "Exact OHLC stop anchor, wick/body semantics and numeric buffer are not specified.",
    ],
    competingInterpretations: [
      "structural invalidation price",
      "risk-budget-derived stop",
      "wick/body variant of the referenced structural level",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F11-limit-refresh",
    question: "When must a pending Limit be replaced after a new candle?",
    sourceEvidence: [
      "39:48 explicitly permits delete/re-place after another candle forms.",
      "40:07 distinguishes materially changed stop distance (new order/new sizing) from small change (retain/move).",
      "The numeric/materiality threshold is not source-defined.",
    ],
    competingInterpretations: [
      "refresh whenever the relevant distance changes",
      "refresh only after a material change",
      "retain the existing order unless another explicit source condition occurs",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F12-trigger-family",
    question: "Is there one fixed candle trigger or a broader trigger family?",
    sourceEvidence: [
      "40:42–41:03 and 53:16 describe one-, two-, and three-candle structures plus Bar/Key-Bar confirmation variants.",
      "The source does not define a deterministic classifier or precedence among those variants.",
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
      "22:43 associates the second position with approximately half-target distance.",
      "38:05 and 41:26–41:53 describe an optional later/second position and a larger-R outcome.",
      "The exact price anchor, sizing, stop and fill semantics remain unresolved.",
    ],
    competingInterpretations: [
      "half the target distance measured from initial entry",
      "half the target distance measured from another source-defined structural anchor",
      "another source-defined anchor not recoverable from current evidence",
    ],
    canonicalStatus: "UNRESOLVED",
  },
  {
    id: "F14-abcd-anchor",
    question: "Which exact A/B/C/D anchors implement the AB=CD concept?",
    sourceEvidence: [
      "36:15 and 36:59–37:08 explicitly link SPIKE-2LEG to AB=CD and describe Leg 2 as equal in magnitude to Leg 1.",
      "1:02:41–1:03:19 provides a later worked leg-hierarchy example.",
      "Exact A/B/C/D OHLC anchors and equality tolerance remain unresolved.",
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
