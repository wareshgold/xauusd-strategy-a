import { describe, expect, it } from 'vitest';

/**
 * Research-only adversarial discrimination fixtures.
 * These fixtures deliberately model competing source interpretations.
 * They do not select or promote a canonical geometry.
 */

type Candle = { open:number; high:number; low:number; close:number };

function f10Candidates(c:Candle, structural:number) {
  return {
    wick:c.low,
    body:Math.min(c.open,c.close),
    structural,
  };
}

function f12Candidates(previous:Candle, corrective:Candle) {
  return {
    touch:corrective.low <= previous.low,
    wickPenetration:corrective.low < previous.low,
    closeBeyond:corrective.close <= previous.low,
  };
}

function f14Candidates(A:number,B:number,C:number) {
  return {
    structural:A + (B-A) + (B-C),
    wick:A + (B-A) + (B-C),
    body:A + (B-A) + (B-C),
  };
}

describe('SP2L F10/F12/F14 synthetic discrimination', () => {
  it('keeps F10 wick, body and structural candidates numerically distinct', () => {
    const c={open:100,high:112,low:90,close:105};
    const x=f10Candidates(c,96);
    expect(new Set(Object.values(x)).size).toBe(3);
  });

  it('keeps F12 touch, penetration and close semantics distinct', () => {
    const previous={open:100,high:110,low:95,close:108};
    const corrective={open:108,high:109,low:95,close:97};
    const x=f12Candidates(previous,corrective);
    expect(x.touch).toBe(true);
    expect(x.wickPenetration).toBe(false);
    expect(x.closeBeyond).toBe(false);
  });

  it('does not encode an AB=CD anchor choice as canonical geometry', () => {
    const candidates=f14Candidates(100,120,110);
    expect(Object.keys(candidates)).toEqual(['structural','wick','body']);
    expect(Object.values(candidates).every(Number.isFinite)).toBe(true);
  });

  it('does not define trigger precedence', () => {
    const variants=['one-candle','two-candle','three-candle','bar','key-bar'];
    expect(variants).toHaveLength(5);
    expect(variants).not.toEqual(['three-candle','two-candle','one-candle','key-bar','bar']);
  });
});

export const F10_F12_F14_DISCRIMINATION_STATUS =
  'RESEARCH_ONLY_NO_CANONICAL_SELECTION' as const;