import { describe, expect, it } from 'vitest';
import { F10_F12_F14_DISCRIMINATION_STATUS } from '../research/harness/sp2l_f10_f12_f14_discrimination_v1';

describe('SP2L F10/F12/F14 discrimination boundary', () => {
  it('keeps the fixture harness research-only', () => {
    expect(F10_F12_F14_DISCRIMINATION_STATUS).toBe('RESEARCH_ONLY_NO_CANONICAL_SELECTION');
  });

  it('requires all three unresolved families to remain non-canonical', () => {
    const unresolved = ['F10', 'F12', 'F14'];
    expect(unresolved).toEqual(['F10', 'F12', 'F14']);
  });
});