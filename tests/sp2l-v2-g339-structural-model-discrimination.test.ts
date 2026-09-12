import { describe, expect, it } from 'vitest';
import {
  candidateIsCanonical,
  candidateSeparation,
  G339_NESTED_FIXTURE,
  G339_SOURCE_COMPATIBLE_FIXTURE,
  indexOfRole,
  legMagnitude,
} from '../src/domain/research/sp2l-v2/G339StructuralModelFixtures.js';

describe('SP2L G339 synthetic structural-model discrimination (research only)', () => {
  it('keeps all competing structural interpretations non-canonical', () => {
    for (const candidate of [
      'SOURCE_DEEP_ORIGIN',
      'FIRST_BREAKOUT_CANDLE',
      'NEAREST_SWING',
      'FILL_AS_C',
      'SOURCE_CORRECTION_REFERENCE',
    ] as const) {
      expect(candidateIsCanonical(candidate)).toBe(false);
    }
  });

  it('preserves the source semantic chain as distinct events', () => {
    const positions = candidateSeparation(G339_SOURCE_COMPATIBLE_FIXTURE);
    expect(positions.deepOriginIndex).toBeLessThan(positions.correctionIndex);
    expect(positions.correctionIndex).toBeLessThan(positions.pendingIndex);
    expect(positions.pendingIndex).toBeLessThan(positions.fillIndex);
    expect(indexOfRole(G339_SOURCE_COMPATIBLE_FIXTURE, 'DEEP_ORIGIN')).toEqual([2]);
    expect(indexOfRole(G339_SOURCE_COMPATIBLE_FIXTURE, 'CORRECTION')).toEqual([7]);
    expect(indexOfRole(G339_SOURCE_COMPATIBLE_FIXTURE, 'PENDING_LIMIT')).toEqual([8]);
    expect(indexOfRole(G339_SOURCE_COMPATIBLE_FIXTURE, 'FILL')).toEqual([9]);
  });

  it('demonstrates that fill cannot silently become the correction reference', () => {
    const positions = candidateSeparation(G339_SOURCE_COMPATIBLE_FIXTURE);
    expect(positions.fillIndex).not.toBe(positions.correctionIndex);
  });

  it('distinguishes parent-scale and nested-scale measurements', () => {
    const parent = legMagnitude(G339_NESTED_FIXTURE, 'n-origin', 'n-parent-b');
    const nested = legMagnitude(G339_NESTED_FIXTURE, 'n-origin', 'n-nested-b');
    expect(parent).not.toBe(nested);
    expect(parent).toBe(30);
    expect(nested).toBe(25);
  });

  it('keeps the second-leg fixture directionally separate from the parent first-leg anchor pair', () => {
    const firstLeg = legMagnitude(G339_SOURCE_COMPATIBLE_FIXTURE, 'origin', 'parent-b');
    const secondLeg = legMagnitude(G339_SOURCE_COMPATIBLE_FIXTURE, 'correction', 'leg2-end');
    expect(firstLeg).toBe(19);
    expect(secondLeg).toBe(12);
    expect(firstLeg).not.toBe(secondLeg);
  });

  it('does not encode wick/body selection or an AB=CD tolerance', () => {
    const fixture = G339_SOURCE_COMPATIBLE_FIXTURE;
    expect(fixture.find((event) => event.id === 'origin')).toMatchObject({ role: 'DEEP_ORIGIN' });
    expect(fixture.find((event) => event.id === 'correction')).toMatchObject({ role: 'CORRECTION' });
    expect(fixture.find((event) => event.id === 'fill')).toMatchObject({ role: 'FILL' });
    expect(fixture.every((event) => !('tolerance' in event))).toBe(true);
  });
});
