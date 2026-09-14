import { describe, expect, it } from 'vitest';
import {
  SP2L_GEOMETRY_FREEZE_GATE,
  assertGeometryFreezeAllowed,
  canFreezeExecutableGeometry,
  isGeometryFreezeBlocked
} from '../../src/domain/research/sp2l-v2/G400GeometryFreezeGate.js';

describe('G400 geometry freeze gate', () => {
  it('remains blocked while source-critical geometry is unresolved', () => {
    expect(isGeometryFreezeBlocked()).toBe(true);
    expect(canFreezeExecutableGeometry()).toBe(false);
    expect(SP2L_GEOMETRY_FREEZE_GATE.readiness).toBe('BLOCKED');
    expect(SP2L_GEOMETRY_FREEZE_GATE.blockers.length).toBe(7);
  });

  it('keeps the critical blockers explicit', () => {
    const ids = SP2L_GEOMETRY_FREEZE_GATE.blockers.map((item) => item.id);
    expect(ids).toEqual([
      'UNRES-PGAP-GEOMETRY',
      'UNRES-ABCD-ANCHORS',
      'UNRES-ABCD-TOLERANCE',
      'UNRES-ENTRY-PRICE',
      'UNRES-ENTRY-TIMING',
      'UNRES-STOP-BOUNDARY',
      'UNRES-TARGET-MAPPING'
    ]);
  });

  it('cannot be cleared by an implementation shortcut', () => {
    expect(() => assertGeometryFreezeAllowed()).toThrow(
      'executable geometry cannot be frozen while source-critical dimensions remain unresolved'
    );
  });
});
