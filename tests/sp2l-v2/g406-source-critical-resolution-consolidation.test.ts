import { describe, expect, it } from 'vitest';
import {
  G406_SOURCE_CRITICAL_DIMENSIONS,
  G406_STATUS,
  g406AllSourceResolutionGatesRemainUnresolved,
  g406DoesNotAuthorizeGeometryFreeze
} from '../../src/domain/research/sp2l-v2/G406SourceCriticalResolutionConsolidation.js';

describe('G406 source-critical resolution consolidation', () => {
  it('keeps all five source-resolution gates unresolved', () => {
    expect(g406AllSourceResolutionGatesRemainUnresolved()).toBe(true);
    expect(Object.values(G406_STATUS.sourceResolutionGates)).toEqual([
      'UNRESOLVED',
      'UNRESOLVED',
      'UNRESOLVED',
      'UNRESOLVED',
      'UNRESOLVED'
    ]);
  });

  it('keeps the seven G400 source-critical dimensions explicit', () => {
    expect(G406_SOURCE_CRITICAL_DIMENSIONS).toEqual([
      'UNRES-PGAP-GEOMETRY',
      'UNRES-ABCD-ANCHORS',
      'UNRES-ABCD-TOLERANCE',
      'UNRES-ENTRY-PRICE',
      'UNRES-ENTRY-TIMING',
      'UNRES-STOP-BOUNDARY',
      'UNRES-TARGET-MAPPING'
    ]);
  });

  it('does not authorize executable geometry freeze', () => {
    expect(g406DoesNotAuthorizeGeometryFreeze()).toBe(true);
    expect(G406_STATUS.status).toBe('BLOCKED');
    expect(G406_STATUS.canonicalGeometryAuthorized).toBe(false);
  });

  it('does not treat consolidation as source evidence', () => {
    expect(G406_STATUS.geometryFreeze).toBe('BLOCKED');
  });
});
