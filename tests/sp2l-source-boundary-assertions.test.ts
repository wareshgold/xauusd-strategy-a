import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'SOURCE_DISCRIMINATED' | 'UNRESOLVED';

interface BoundaryCase {
  readonly id: string;
  readonly resolution: Resolution;
  readonly canonical: boolean;
}

/**
 * Research-only guardrail. These cases mirror the current evidence ledger:
 * unresolved source meaning must remain outside canonical geometry.
 * This test does not define or choose any strategy geometry.
 */
const cases: readonly BoundaryCase[] = [
  { id: 'ENTRY', resolution: 'UNRESOLVED', canonical: false },
  { id: 'INVALIDATION', resolution: 'UNRESOLVED', canonical: false },
  { id: 'LIMIT-REFRESH', resolution: 'UNRESOLVED', canonical: false },
  { id: 'TRIGGER', resolution: 'UNRESOLVED', canonical: false },
  { id: '2X', resolution: 'UNRESOLVED', canonical: false },
  { id: 'ABCD', resolution: 'UNRESOLVED', canonical: false },
  { id: 'P-GAP', resolution: 'UNRESOLVED', canonical: false },
  { id: 'CONTEXT', resolution: 'UNRESOLVED', canonical: false },
  { id: 'CORRECTION', resolution: 'UNRESOLVED', canonical: false },
  { id: 'F09-ENTRY-VS-LEG2', resolution: 'SOURCE_DISCRIMINATED', canonical: false },
  { id: 'F16-ROUND-LEVEL', resolution: 'UNRESOLVED', canonical: false },
];

describe('SP2L source-boundary assertions', () => {
  it('keeps every unresolved geometry blocker out of the canonical rule set', () => {
    const unresolved = cases.filter((x) => x.resolution === 'UNRESOLVED');
    expect(unresolved.length).toBeGreaterThanOrEqual(7);

    for (const item of unresolved) {
      expect(item.canonical, item.id).toBe(false);
    }
  });

  it('covers all seven Frozen Geometry evidence fields as unresolved', () => {
    const requiredFields = [
      'ENTRY',
      'INVALIDATION',
      'LIMIT-REFRESH',
      'TRIGGER',
      '2X',
      'ABCD',
      'P-GAP',
    ];

    for (const id of requiredFields) {
      const item = cases.find((x) => x.id === id);
      expect(item, id).toBeDefined();
      expect(item?.resolution, id).toBe('UNRESOLVED');
      expect(item?.canonical, id).toBe(false);
    }
  });

  it('does not treat source-discriminated boundaries as fully frozen geometry', () => {
    const f9 = cases.find((x) => x.id === 'F09-ENTRY-VS-LEG2')!;
    expect(f9.resolution).toBe('SOURCE_DISCRIMINATED');
    expect(f9.canonical).toBe(false);
  });

  it('fails closed if any unresolved blocker is accidentally promoted', () => {
    const promotedBlockers = cases.filter(
      (x) => x.resolution === 'UNRESOLVED' && x.canonical,
    );
    expect(promotedBlockers).toEqual([]);
  });
});
