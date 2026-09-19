import { Provenance, Sp2lGeometryContract } from './sp2l_geometry_contract_v1';

export type CanonicalPromotionGuardResult = {
  readonly allowed: boolean;
  readonly blockedFields: (keyof Sp2lGeometryContract)[];
  readonly reason: string;
};

/**
 * Research-only no-go guard.
 * It never defines geometry. It only prevents canonical promotion unless
 * every required geometry field is explicitly SOURCE_CONFIRMED.
 */
export function evaluateCanonicalPromotionGuard(
  geometry: Sp2lGeometryContract,
): CanonicalPromotionGuardResult {
  const blockedFields = (Object.keys(geometry) as (keyof Sp2lGeometryContract)[])
    .filter((field) => geometry[field].provenance !== ('SOURCE_CONFIRMED' as Provenance));

  if (blockedFields.length > 0) {
    return {
      allowed: false,
      blockedFields,
      reason: `CANONICAL_PROMOTION_BLOCKED: ${blockedFields.join(', ')}`,
    };
  }

  return {
    allowed: true,
    blockedFields: [],
    reason: 'CANONICAL_PROMOTION_ALLOWED: all geometry fields are SOURCE_CONFIRMED',
  };
}
