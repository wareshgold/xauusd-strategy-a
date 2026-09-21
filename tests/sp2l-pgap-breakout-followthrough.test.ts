import { describe, expect, it } from "vitest";
import { observeBreakoutFollowThrough } from "../research/fixtures/sp2l_pgap_qualification_reconstruction_v1.js";

describe("source-shaped breakout follow-through observation", () => {
  const prev = { open: 100, high: 103, low: 99, close: 102 };

  it("requires the breakout close and a following candle that does not return", () => {
    const o = observeBreakoutFollowThrough(
      prev,
      { open: 102, high: 108, low: 101, close: 107 },
      { open: 107, high: 109, low: 106, close: 108 },
    );
    expect(o.breakoutCloseBeyondPreviousRange).toBe(true);
    expect(o.followThroughDoesNotReturn).toBe(true);
    expect(o.sourceBreakoutObserved).toBe(true);
    expect(o.canonicalEligible).toBe(false);
  });

  it("rejects a breakout whose next candle returns into the prior range", () => {
    const o = observeBreakoutFollowThrough(
      prev,
      { open: 102, high: 108, low: 99, close: 107 },
      { open: 107, high: 109, low: 102, close: 103 },
    );
    expect(o.breakoutCloseBeyondPreviousRange).toBe(true);
    expect(o.followThroughDoesNotReturn).toBe(false);
    expect(o.sourceBreakoutObserved).toBe(false);
  });

  it("does not create canonical geometry", () => {
    const o = observeBreakoutFollowThrough(
      prev,
      { open: 102, high: 108, low: 101, close: 107 },
      { open: 107, high: 109, low: 106, close: 108 },
    );
    expect(o.canonicalEligible).toBe(false);
  });
});
