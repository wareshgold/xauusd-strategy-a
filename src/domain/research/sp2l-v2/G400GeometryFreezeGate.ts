import { SP2L_SEMANTIC_CORE } from './G399SemanticCore.js';

export type FreezeReadiness = 'BLOCKED' | 'READY';

export interface GeometryFreezeBlocker {
  readonly id: string;
  readonly reason: string;
}

/**
 * G400 is a gate, not a geometry freeze.
 * It proves that the semantic layer cannot be promoted to executable geometry
 * while any source-critical dimension remains unresolved.
 */
export const SP2L_GEOMETRY_FREEZE_GATE = {
  version: 'SP2L-GEOMETRY-FREEZE-GATE-G400',
  readiness: 'BLOCKED' as FreezeReadiness,
  blockers: SP2L_SEMANTIC_CORE.unresolved.map((item) => ({
    id: item.id,
    reason: item.description
  })) as readonly GeometryFreezeBlocker[]
} as const;

export function isGeometryFreezeBlocked(): boolean {
  return SP2L_GEOMETRY_FREEZE_GATE.blockers.length > 0;
}

export function canFreezeExecutableGeometry(): false {
  return false;
}

/** A profitable hypothesis or synthetic discriminator cannot clear a source blocker. */
export function assertGeometryFreezeAllowed(): never {
  throw new Error(
    'G400 freeze guard: executable geometry cannot be frozen while source-critical dimensions remain unresolved.'
  );
}
