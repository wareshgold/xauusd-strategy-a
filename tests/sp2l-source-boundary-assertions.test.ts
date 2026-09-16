import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'SOURCE_DISCRIMINATED' | 'UNRESOLVED';

interface BoundaryCase {
  readonly id: string;
  readonly resolution: Resolution;
  readonly canonical: boolean;
}

const cases: readonly BoundaryCase[] = [
  { id: 'C01-P-GAP', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C02-SL-GEOMETRY', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C03-ABCD', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C04-TP-2X', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C05-CONTEXT', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C06-PENDING-REFRESH', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C07-TRIGGER', resolution: 'UNRESOLVED', canonical: false },
  { id: 'C08-CORRECTION-INVALIDATION', resolution: 'UNRESOLVED', canonical: false },
  { id: 'F09-ENTRY-VS-LEG2', resolution: 'SOURCE_DISCRIMINATED', canonical: false },
];

describe('SP2L source-boundary assertions', () => {
  it('keeps unresolved geometry out of the canonical rule set', () => {
    for (const item of cases.filter((x) => x.resolution === 'UNRESOLVED')) {
      expect(item.canonical, item.id).toBe(false);
    }
  });

  it('does not treat source-discriminated boundaries as fully frozen geometry', () => {
    const f9 = cases.find((x) => x.id === 'F09-ENTRY-VS-LEG2')!;
    expect(f9.resolution).toBe('SOURCE_DISCRIMINATED');
    expect(f9.canonical).toBe(false);
  });

  it('fails closed if a blocker is accidentally promoted', () => {
    const promotedBlockers = cases.filter(
      (x) => x.resolution === 'UNRESOLVED' && x.canonical,
    );
    expect(promotedBlockers).toEqual([]);
  });
});
