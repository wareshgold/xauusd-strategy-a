import { Provenance, Sp2lGeometryContract } from './sp2l_geometry_contract_v1.js';

export type FrozenGeometryGateStatus = 'READY' | 'BLOCKED';

export type FrozenGeometryGateResult = {
  status: FrozenGeometryGateStatus;
  blockedFields: (keyof Sp2lGeometryContract)[];
  reason: string;
};

const REQUIRED_FIELDS: (keyof Sp2lGeometryContract)[] = [
  'entry',
  'invalidation',
  'limitRefresh',
  'trigger',
  'twoX',
  'abcd',
  'pGap',
];

/**
 * Research-only gate. It does not define geometry and never generates BUY/SELL.
 * Canonical validation is allowed only when every required field is source-confirmed.
 */
export function evaluateFrozenGeometryGate(
  geometry: Sp2lGeometryContract,
): FrozenGeometryGateResult {
  const blockedFields = REQUIRED_FIELDS.filter(
    (field) => geometry[field].provenance !== ('SOURCE_CONFIRMED' as Provenance),
  );

  if (blockedFields.length > 0) {
    return {
      status: 'BLOCKED',
      blockedFields,
      reason: `FROZEN_GEOMETRY_BLOCKED: ${blockedFields.join(', ')}`,
    };
  }

  return {
    status: 'READY',
    blockedFields: [],
    reason: 'FROZEN_GEOMETRY_READY: all required fields are SOURCE_CONFIRMED',
  };
}
