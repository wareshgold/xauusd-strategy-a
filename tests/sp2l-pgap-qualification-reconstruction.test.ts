import { describe, expect, it } from "vitest";
import { observeBullishPgapVariants, bullishHigherLowSequence, bearishLowerHighSequence } from "../research/fixtures/sp2l_pgap_qualification_reconstruction_v1.js";
import { PGAP_SOURCE_FIXTURES } from "../research/fixtures/sp2l_pgap_source_reconstruction_v1.js";

describe("P-Gap qualification reconstruction observations", () => {
  it("recognizes breakout → follow-through → gap as a source-shaped family", () => {
    const f = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-001")!;
    const o = observeBullishPgapVariants(f.candles, f.gapPair);
    expect(o.breakoutObserved).toBe(true);
    expect(o.gapObserved).toBe(true);
    expect(o.sourceVariant).toBe("breakout-follow-through-gap");
    expect(o.canonicalEligible).toBe(false);
  });

  it("recognizes higher-lows → gap as a source-shaped family", () => {
    const f = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-002")!;
    const o = observeBullishPgapVariants(f.candles, f.gapPair);
    expect(o.higherLowsObserved).toBe(true);
    expect(o.gapObserved).toBe(true);
    expect(o.sourceVariant).toBe("higher-lows-gap");
    expect(o.canonicalEligible).toBe(false);
  });

  it("does not turn a geometric gap into a qualified P-Gap by itself", () => {
    const f = PGAP_SOURCE_FIXTURES.find((x) => x.id === "PGAP-006")!;
    const o = observeBullishPgapVariants(f.candles, f.gapPair);
    expect(o.gapObserved).toBe(true);
    expect(o.sourceVariant).toBe("unresolved");
    expect(o.canonicalEligible).toBe(false);
  });

  it("keeps higher-low and lower-high observations deterministic without fixing their required count", () => {
    expect(bullishHigherLowSequence([
      { open: 100, high: 104, low: 99, close: 103 },
      { open: 103, high: 107, low: 100, close: 106 },
      { open: 106, high: 110, low: 101, close: 109 },
    ])).toBe(true);

    expect(bearishLowerHighSequence([
      { open: 100, high: 101, low: 96, close: 97 },
      { open: 97, high: 100, low: 93, close: 94 },
      { open: 94, high: 98, low: 90, close: 91 },
    ])).toBe(true);
  });

  it("does not encode a minimum gap threshold", () => {
    const tinyGap = [
      { open: 100, high: 100.01, low: 99, close: 100 },
      { open: 100.02, high: 101, low: 100.011, close: 100.8 },
    ];
    const o = observeBullishPgapVariants(tinyGap, [0, 1]);
    expect(o.gapObserved).toBe(true);
    expect(o.canonicalEligible).toBe(false);
  });
});
