import { describe, expect, it } from "vitest";
import { observePgapTiming } from "../research/fixtures/sp2l_pgap_qualification_reconstruction_v1.js";

describe("P-Gap vs E-Gap timing observations", () => {
  it("represents an early-trend gap as P-Gap-shaped timing without freezing qualification", () => {
    const o = observePgapTiming(true, 0);
    expect(o.timing).toBe("early-trend");
    expect(o.executableQualification).toBe("UNRESOLVED");
    expect(o.canonicalEligible).toBe(false);
  });

  it("represents repeated extension as E-Gap-like timing without inventing a cutoff", () => {
    const o = observePgapTiming(true, 1);
    expect(o.timing).toBe("repeated-extension");
    expect(o.executableQualification).toBe("UNRESOLVED");
    expect(o.canonicalEligible).toBe(false);
  });

  it("keeps the teacher's stronger warning after multiple extensions as unresolved", () => {
    const o = observePgapTiming(true, 2);
    expect(o.timing).toBe("repeated-extension");
    expect(o.executableQualification).toBe("UNRESOLVED");
  });

  it("does not classify absence of a gap as E-Gap", () => {
    const o = observePgapTiming(false, 3);
    expect(o.timing).toBe("unresolved");
    expect(o.executableQualification).toBe("UNRESOLVED");
  });
});
