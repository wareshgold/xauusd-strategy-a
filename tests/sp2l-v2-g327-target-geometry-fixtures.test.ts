import { describe, expect, it } from 'vitest';
import {
  C1_EQUAL_LADDER,
  C2_SEQUENTIAL_INTERVALS,
  C3_SHIFTED_ANCHORS,
  C4_EXAMPLE_ONLY,
  G327_TARGET_FIXTURES,
  targetDistance,
} from '../src/domain/research/sp2l-v2/SP2LTargetGeometryFixtures.js';

describe('SP2L G327 source-derived target geometry fixtures (research-only)', () => {
  it('keeps C1 deterministic and records the equal-ladder hypothesis without freezing it', () => {
    expect(targetDistance(C1_EQUAL_LADDER, 'SL_TO_ENTRY')).toBe(500);
    expect(targetDistance(C1_EQUAL_LADDER, 'ENTRY_TO_TP1')).toBe(250);
    expect(targetDistance(C1_EQUAL_LADDER, 'ENTRY_TO_TP2')).toBe(500);
    expect(targetDistance(C1_EQUAL_LADDER, 'SL_TO_TP2')).toBe(1000);
    expect(C1_EQUAL_LADDER.mappingStatus).toBe('DETERMINISTIC_CANDIDATE');
  });

  it('keeps C2 distinct from C1 rather than silently normalizing it to the equal ladder', () => {
    expect(targetDistance(C2_SEQUENTIAL_INTERVALS, 'SL_TO_ENTRY')).toBe(250);
    expect(targetDistance(C2_SEQUENTIAL_INTERVALS, 'ENTRY_TO_TP1')).toBe(250);
    expect(targetDistance(C2_SEQUENTIAL_INTERVALS, 'ENTRY_TO_TP2')).toBe(750);
    expect(targetDistance(C2_SEQUENTIAL_INTERVALS, 'SL_TO_TP2')).toBe(1000);
    expect(targetDistance(C2_SEQUENTIAL_INTERVALS, 'ENTRY_TO_TP2')).not.toBe(
      targetDistance(C1_EQUAL_LADDER, 'ENTRY_TO_TP2'),
    );
  });

  it('keeps C3 distinct and exposes its shifted-anchor interpretation', () => {
    expect(targetDistance(C3_SHIFTED_ANCHORS, 'SL_TO_ENTRY')).toBe(250);
    expect(targetDistance(C3_SHIFTED_ANCHORS, 'ENTRY_TO_TP1')).toBe(500);
    expect(targetDistance(C3_SHIFTED_ANCHORS, 'ENTRY_TO_TP2')).toBe(1000);
    expect(targetDistance(C3_SHIFTED_ANCHORS, 'SL_TO_TP2')).toBe(1250);
  });

  it('does not invent executable levels for C4 when the numbers may be examples only', () => {
    expect(C4_EXAMPLE_ONLY.mappingStatus).toBe('NON_MAPPABLE');
    expect(targetDistance(C4_EXAMPLE_ONLY, 'SL_TO_ENTRY')).toBeNull();
    expect(targetDistance(C4_EXAMPLE_ONLY, 'ENTRY_TO_TP1')).toBeNull();
    expect(targetDistance(C4_EXAMPLE_ONLY, 'ENTRY_TO_TP2')).toBeNull();
    expect(targetDistance(C4_EXAMPLE_ONLY, 'SL_TO_TP2')).toBeNull();
  });

  it('contains exactly C1-C4 and no canonical selection field', () => {
    expect(Object.keys(G327_TARGET_FIXTURES)).toEqual(['C1', 'C2', 'C3', 'C4']);
  });

  it('uses one shared synthetic entry price so differences come from interpretation, not data fitting', () => {
    expect(C1_EQUAL_LADDER.entry).toBe(C2_SEQUENTIAL_INTERVALS.entry);
    expect(C2_SEQUENTIAL_INTERVALS.entry).toBe(C3_SHIFTED_ANCHORS.entry);
    expect(C3_SHIFTED_ANCHORS.entry).toBe(C4_EXAMPLE_ONLY.entry);
  });
});
