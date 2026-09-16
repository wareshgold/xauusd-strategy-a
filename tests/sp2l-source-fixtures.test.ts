import { describe, expect, it } from 'vitest';

type FixtureId = 'F8'|'F9'|'F10'|'F11'|'F12'|'F13'|'F14'|'F15';
type FixtureStatus = 'SOURCE_DISCRIMINATED'|'UNRESOLVED';

interface FixtureCase {
  readonly id: FixtureId;
  readonly question: string;
  readonly status: FixtureStatus;
  readonly observations: readonly string[];
}

const fixtures: readonly FixtureCase[] = [
  { id:'F8', question:'relevant Low/High anchor', status:'UNRESOLVED', observations:['first structural reference','evolving latest HL/LH'] },
  { id:'F9', question:'Entry versus Start-of-Leg-2', status:'SOURCE_DISCRIMINATED', observations:['distinct price anchors'] },
  { id:'F10', question:'structural invalidation versus risk stop', status:'UNRESOLVED', observations:['wick/body distinction','opposite structural swing'] },
  { id:'F11', question:'pending-order replacement', status:'UNRESOLVED', observations:['order can evolve','replacement threshold unspecified'] },
  { id:'F12', question:'trigger candle family', status:'UNRESOLVED', observations:['1-candle','2-candle','3-candle'] },
  { id:'F13', question:'2X interpretation', status:'UNRESOLVED', observations:['half-target concept','second-position reward interpretation'] },
  { id:'F14', question:'AB=CD anchors', status:'UNRESOLVED', observations:['competing A/B/C/D candidates','no tolerance'] },
  { id:'F15', question:'bearish mirror', status:'UNRESOLVED', observations:['mirror of bullish questions'] },
];

describe('SP2L source-resolution synthetic fixture registry', () => {
  it('contains exactly F8-F15 with deterministic unique identifiers', () => {
    expect(fixtures.map(f => f.id)).toEqual(['F8','F9','F10','F11','F12','F13','F14','F15']);
  });

  it('does not silently promote unresolved geometry', () => {
    const unresolved = fixtures.filter(f => f.status === 'UNRESOLVED');
    expect(unresolved.map(f => f.id)).toEqual(['F8','F10','F11','F12','F13','F14','F15']);
  });

  it('keeps F9 as the source-confirmed separation of Entry and Leg-2 start', () => {
    const f9 = fixtures.find(f => f.id === 'F9')!;
    expect(f9.status).toBe('SOURCE_DISCRIMINATED');
    expect(f9.observations).toContain('distinct price anchors');
  });
});
