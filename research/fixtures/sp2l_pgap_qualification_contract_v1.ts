/**
 * P-Gap qualification research contract.
 *
 * This file is intentionally fail-closed: it represents dimensions that must
 * be resolved from primary source evidence before a complete P-Gap detector can
 * be frozen. It does not select values for those dimensions.
 */

export type QualificationResolution =
  | "SOURCE_CONFIRMED"
  | "SOURCE_DISCRIMINATED"
  | "UNRESOLVED";

export interface PgapQualificationContract {
  sequence: QualificationResolution;
  indexing: QualificationResolution;
  earlyTrendContext: QualificationResolution;
  minimumGapThreshold: QualificationResolution;
  breakoutRelation: QualificationResolution;
  lateExtensionExclusion: QualificationResolution;
  bearishIndependentEvidence: QualificationResolution;
}

export const PGAP_QUALIFICATION_CONTRACT: Readonly<PgapQualificationContract> = {
  sequence: "UNRESOLVED",
  indexing: "UNRESOLVED",
  earlyTrendContext: "UNRESOLVED",
  minimumGapThreshold: "UNRESOLVED",
  breakoutRelation: "UNRESOLVED",
  lateExtensionExclusion: "UNRESOLVED",
  bearishIndependentEvidence: "UNRESOLVED",
};

export function isCompletePgapQualificationResolved(
  contract: PgapQualificationContract,
): boolean {
  return Object.values(contract).every((value) => value === "SOURCE_CONFIRMED");
}

/**
 * A geometric gap may be observed without being classified as P-Gap.
 * Qualification therefore cannot silently collapse to the primitive.
 */
export function classifyPgapResearchOnly(
  primitivePositive: boolean,
  contract: PgapQualificationContract,
): "PRIMITIVE_POSITIVE_QUALIFICATION_BLOCKED" | "NO_PRIMITIVE_GAP" {
  if (!primitivePositive) return "NO_PRIMITIVE_GAP";
  if (!isCompletePgapQualificationResolved(contract)) {
    return "PRIMITIVE_POSITIVE_QUALIFICATION_BLOCKED";
  }
  return "PRIMITIVE_POSITIVE_QUALIFICATION_BLOCKED";
}
