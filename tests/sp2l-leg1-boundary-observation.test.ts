import { describe, expect, it } from "vitest";
import { observeLeg1Candidate } from "../research/fixtures/sp2l_leg1_boundary_observation_v1.js";

describe("SP2L Leg-1 boundary observation", () => {
  const candles = [
    {open:100,high:103,low:99,close:102},
    {open:102,high:108,low:101,close:107},
    {open:107,high:109,low:104,close:108},
  ];

  it("records a candidate boundary without promoting anchor semantics", () => {
    const x = observeLeg1Candidate("BUY", candles, 0, 2)!;
    expect(x.leg1Size).toBe(8);
    expect(x.anchorSemantics).toBe("SOURCE_SHAPED_RESEARCH_ONLY");
    expect(x.canonicalEligible).toBe(false);
  });

  it("keeps direction symmetric at the observation layer", () => {
    const x = observeLeg1Candidate("SELL", candles, 0, 2)!;
    expect(x.leg1Size).toBe(8);
    expect(x.canonicalEligible).toBe(false);
  });
});
