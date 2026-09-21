import { describe, expect, it } from "vitest";
import {
  PGAP_QUALIFICATION_CONTRACT,
  classifyPgapResearchOnly,
  isCompletePgapQualificationResolved,
} from "../research/fixtures/sp2l_pgap_qualification_contract_v1.js";

describe("SP2L P-Gap qualification boundary", () => {
  it("keeps every unresolved qualification dimension explicitly unresolved", () => {
    expect(Object.values(PGAP_QUALIFICATION_CONTRACT)).toEqual([
      "UNRESOLVED",
      "UNRESOLVED",
      "UNRESOLVED",
      "UNRESOLVED",
      "UNRESOLVED",
      "UNRESOLVED",
      "UNRESOLVED",
    ]);
  });

  it("does not mistake a geometric gap for a complete P-Gap classification", () => {
    expect(isCompletePgapQualificationResolved(PGAP_QUALIFICATION_CONTRACT)).toBe(false);
    expect(classifyPgapResearchOnly(true, PGAP_QUALIFICATION_CONTRACT))
      .toBe("PRIMITIVE_POSITIVE_QUALIFICATION_BLOCKED");
  });

  it("fails closed when there is no geometric gap", () => {
    expect(classifyPgapResearchOnly(false, PGAP_QUALIFICATION_CONTRACT))
      .toBe("NO_PRIMITIVE_GAP");
  });
});
