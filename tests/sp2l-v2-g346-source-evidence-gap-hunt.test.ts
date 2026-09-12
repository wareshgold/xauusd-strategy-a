import { describe, expect, it } from 'vitest';
import {
  G346_GAPS,
  g346NoNewResolvingEvidenceFound,
  g346SourceConfirmedConceptsRemain,
  g346UnresolvedHaveRequirements,
} from '../src/domain/research/sp2l-v2/G346SourceEvidenceGapHunt.js';

describe('SP2L G346 source evidence gap hunt', () => {
  it('covers every unresolved dimension with an explicit requirement', () => {
    expect(g346UnresolvedHaveRequirements()).toBe(true);
  });

  it('records no newly resolving authoritative evidence', () => {
    expect(g346NoNewResolvingEvidenceFound()).toBe(true);
  });

  it('preserves source-confirmed semantic concepts', () => {
    expect(g346SourceConfirmedConceptsRemain()).toEqual([
      'AB=CD',
      'Leg2≈Leg1',
      'Pending-limit',
      'Parent/nested hierarchy',
    ]);
  });

  it('keeps fill-as-C explicitly rejected', () => {
    expect(G346_GAPS.find((gap) => gap.id === 'FILL_AS_C')?.status).toBe('EXPLICITLY_REJECTED');
  });

  it('does not silently freeze geometry', () => {
    expect(G346_GAPS.some((gap) => gap.status === 'UNRESOLVED')).toBe(true);
  });
});
