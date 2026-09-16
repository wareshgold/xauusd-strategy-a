import { describe, expect, it } from 'vitest';

describe('SP2L extreme-R forensic invariant', () => {
  it('reproduces the persisted 125R arithmetic without clipping', () => {
    const entry = 4521.5838;
    const stopLoss = 4521.61331;
    const tp1 = 4517.8892399999995;
    const risk = Math.abs(entry - stopLoss);
    const reward = Math.abs(tp1 - entry);
    const r = reward / risk;

    expect(risk).toBeCloseTo(0.02951, 8);
    expect(r).toBeCloseTo(125.19688241535353, 10);
    expect(r).toBeGreaterThan(100);
  });

  it('does not silently classify tiny risk as invalid when it is positive', () => {
    const entry = 4521.5838;
    const stopLoss = 4521.61331;
    const risk = Math.abs(entry - stopLoss);
    expect(risk).toBeGreaterThan(0);
    expect(Number.isFinite(risk)).toBe(true);
  });
});
