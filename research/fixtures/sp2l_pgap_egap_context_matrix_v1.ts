import { PgapCandle, bullishGapPrimitive } from "./sp2l_pgap_source_reconstruction_v1.js";

export type PgapContextClass =
  | "early-pgap-shaped"
  | "late-egap-shaped"
  | "same-geometry-different-context"
  | "no-gap-control"
  | "overlap-control"
  | "equality-control";

export interface PgapEgapContextFixture {
  id: string;
  context: PgapContextClass;
  candles: readonly PgapCandle[];
  gapPair: readonly [number, number];
  expectedGapPrimitive: boolean;
  expectedQualification: "UNRESOLVED";
  canonicalEligible: false;
  note: string;
}

const c = (open:number, high:number, low:number, close:number): PgapCandle =>
  ({open, high, low, close});

export const PGAP_EGAP_CONTEXT_MATRIX: readonly PgapEgapContextFixture[] = [
  {
    id:"CTX-001", context:"early-pgap-shaped",
    candles:[c(100,103,99,102),c(102,108,101,107),c(107,109,106,108),c(108,112,109,111)],
    gapPair:[2,3], expectedGapPrimitive:true, expectedQualification:"UNRESOLVED",
    canonicalEligible:false, note:"Early/quick opportunity shape; no numeric cutoff inferred."
  },
  {
    id:"CTX-002", context:"late-egap-shaped",
    candles:[c(100,104,99,103),c(103,109,102,108),c(108,114,107,113),c(113,118,117,117.5)],
    gapPair:[2,3], expectedGapPrimitive:true, expectedQualification:"UNRESOLVED",
    canonicalEligible:false, note:"Repeated-extension context; geometric gap alone cannot establish E-Gap."
  },
  {
    id:"CTX-003", context:"same-geometry-different-context",
    candles:[c(100,103,99,102),c(102,108,101,107),c(107,109,106,108),c(108,112,109,111)],
    gapPair:[2,3], expectedGapPrimitive:true, expectedQualification:"UNRESOLVED",
    canonicalEligible:false, note:"Same OHLC gap geometry as CTX-001; context must be represented separately."
  },
  {
    id:"CTX-004", context:"no-gap-control",
    candles:[c(100,106,99,104),c(104,108,105,107)],
    gapPair:[0,1], expectedGapPrimitive:false, expectedQualification:"UNRESOLVED",
    canonicalEligible:false, note:"Overlap control."
  },
  {
    id:"CTX-005", context:"overlap-control",
    candles:[c(100,106,99,104),c(104,108,103,107)],
    gapPair:[0,1], expectedGapPrimitive:false, expectedQualification:"UNRESOLVED",
    canonicalEligible:false, note:"Explicit overlap control."
  },
  {
    id:"CTX-006", context:"equality-control",
    candles:[c(100,105,99,104),c(104,110,105,109)],
    gapPair:[0,1], expectedGapPrimitive:false, expectedQualification:"UNRESOLVED",
    canonicalEligible:false, note:"Touch/equality control; strict non-overlap remains required."
  },
] as const;

export function validateContextMatrixFixture(f: PgapEgapContextFixture): boolean {
  const [i,j] = f.gapPair;
  return bullishGapPrimitive(f.candles[i]!, f.candles[j]!) === f.expectedGapPrimitive
    && f.expectedQualification === "UNRESOLVED"
    && f.canonicalEligible === false;
}
