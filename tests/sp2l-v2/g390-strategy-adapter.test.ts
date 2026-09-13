import { describe, expect, it } from 'vitest';
import { noCanonicalStrategyAdapter } from '../../src/domain/research/sp2l-v2/G390StrategyAdapter.js';

describe('Strategy adapter boundary', () => {
  it('cannot emit canonical candidates before geometry is frozen', () => {
    const adapter = noCanonicalStrategyAdapter();
    expect(adapter.canonical).toBe(false);
    expect(adapter.strategyVersion).toBe('SP2L-UNRESOLVED-GEOMETRY');
    expect(adapter.evaluate([], 0, 'DEV')).toBeNull();
  });
});
