import { describe, expect, it } from 'vitest';
import { assignSplit, canonicalExecutionAllowed } from '../../src/domain/research/sp2l-v2/G386DevHarness.js';

describe('G386 DEV harness ESM import', () => {
  it('uses explicit ESM source extension and preserves split semantics', () => {
    const config = {
      devStart: '2026-01-01 00:00:00', devEnd: '2026-03-31 23:59:59',
      valStart: '2026-04-01 00:00:00', valEnd: '2026-06-30 23:59:59',
      holdoutStart: '2026-07-01 00:00:00', holdoutEnd: '2026-09-30 23:59:59',
      costs: { spreadPrice: 0.1, slippagePrice: 0.05, commissionPrice: 0 }
    };
    expect(assignSplit('2026-02-01 00:00:00', config)).toBe('DEV');
    expect(assignSplit('2026-05-01 00:00:00', config)).toBe('VAL');
    expect(assignSplit('2026-08-01 00:00:00', config)).toBe('HOLDOUT');
    expect(canonicalExecutionAllowed()).toBe(false);
  });
});
