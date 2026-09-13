import { describe, expect, it } from 'vitest';
import {
  SP2L_SEMANTIC_CORE,
  assertExecutableGeometryResolved,
  isSemanticCoreFrozen
} from '../../src/domain/research/sp2l-v2/G399SemanticCore.js';

describe('G399 SP2L semantic core', () => {
  it('freezes only source-confirmed/source-supported semantic concepts', () => {
    expect(isSemanticCoreFrozen()).toBe(true);
    expect(SP2L_SEMANTIC_CORE.canonical).toBe(true);
    expect(SP2L_SEMANTIC_CORE.rules.length).toBe(9);
    expect(SP2L_SEMANTIC_CORE.unresolved.length).toBe(7);
  });

  it('keeps executable geometry explicitly unresolved', () => {
    const unresolvedIds = SP2L_SEMANTIC_CORE.unresolved.map((item) => item.id);
    expect(unresolvedIds).toContain('UNRES-PGAP-GEOMETRY');
    expect(unresolvedIds).toContain('UNRES-ABCD-ANCHORS');
    expect(unresolvedIds).toContain('UNRES-ENTRY-PRICE');
    expect(unresolvedIds).toContain('UNRES-STOP-BOUNDARY');
    expect(unresolvedIds).toContain('UNRES-TARGET-MAPPING');
  });

  it('cannot manufacture an executable canonical candidate', () => {
    expect(() => assertExecutableGeometryResolved()).toThrow(
      'semantic core is frozen, but executable geometry remains unresolved'
    );
  });
});
