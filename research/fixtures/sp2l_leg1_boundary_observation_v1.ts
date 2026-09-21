export interface LegBoundaryObservation {
  direction: "BUY" | "SELL";
  startIndex: number;
  endIndex: number;
  startPrice: number;
  endPrice: number;
  leg1Size: number;
  anchorSemantics: "SOURCE_SHAPED_RESEARCH_ONLY";
  canonicalEligible: false;
}

/**
 * Research observation only. The source describes a first leg followed by
 * correction and a second-leg objective, but does not uniquely specify the
 * exact A/B anchors or wick/body treatment.
 */
export function observeLeg1Candidate(
  direction: "BUY" | "SELL",
  candles: readonly { open:number; high:number; low:number; close:number }[],
  startIndex: number,
  endIndex: number,
): LegBoundaryObservation | null {
  const start = candles[startIndex];
  const end = candles[endIndex];
  if (!start || !end || endIndex < startIndex) return null;
  const startPrice = direction === "BUY" ? start.open : start.open;
  const endPrice = direction === "BUY" ? end.close : end.close;
  const leg1Size = Math.abs(endPrice - startPrice);
  if (!(leg1Size > 0)) return null;
  return {
    direction, startIndex, endIndex, startPrice, endPrice, leg1Size,
    anchorSemantics: "SOURCE_SHAPED_RESEARCH_ONLY",
    canonicalEligible: false,
  };
}
