import { SP2L_GEOMETRY_FREEZE_GATE } from './G400GeometryFreezeGate.js';
import { G401_STATUS } from './G401PgapSourceResolution.js';
import { G402_STATUS } from './G402AbcdAnchorSourceResolution.js';
import { G403_STATUS } from './G403EntryExecutionSourceResolution.js';
import { G404_STATUS } from './G404StructuralStopBoundarySourceResolution.js';
import { G405_STATUS } from './G405TargetMappingSourceResolution.js';

export type G406Status = 'BLOCKED' | 'READY_FOR_SOURCE_EVIDENCE_REVIEW';

export const G406_SOURCE_CRITICAL_DIMENSIONS = [
  'UNRES-PGAP-GEOMETRY',
  'UNRES-ABCD-ANCHORS',
  'UNRES-ABCD-TOLERANCE',
  'UNRES-ENTRY-PRICE',
  'UNRES-ENTRY-TIMING',
  'UNRES-STOP-BOUNDARY',
  'UNRES-TARGET-MAPPING'
] as const;

/**
 * G406 consolidates the five source-resolution gates without promoting any
 * hypothesis to canonical geometry. It is a bookkeeping/readiness gate only.
 */
export const G406_STATUS = {
  gate: 'G406',
  status: 'BLOCKED' as G406Status,
  sourceResolutionGates: {
    G401: G401_STATUS.status,
    G402: G402_STATUS.status,
    G403: G403_STATUS.status,
    G404: G404_STATUS.status,
    G405: G405_STATUS.status
  },
  geometryFreeze: SP2L_GEOMETRY_FREEZE_GATE.readiness,
  unresolvedDimensions: G406_SOURCE_CRITICAL_DIMENSIONS,
  canonicalGeometryAuthorized: false
} as const;

export function g406AllSourceResolutionGatesRemainUnresolved(): boolean {
  return [G401_STATUS, G402_STATUS, G403_STATUS, G404_STATUS, G405_STATUS]
    .every((gate) => gate.status === 'UNRESOLVED');
}

export function g406DoesNotAuthorizeGeometryFreeze(): boolean {
  return SP2L_GEOMETRY_FREEZE_GATE.readiness === 'BLOCKED'
    && SP2L_GEOMETRY_FREEZE_GATE.blockers.length === G406_SOURCE_CRITICAL_DIMENSIONS.length;
}
