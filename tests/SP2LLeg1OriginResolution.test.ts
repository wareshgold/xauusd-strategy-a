import { describe, expect, it } from 'vitest';

type Resolution =
  | 'SOURCE_CONFIRMED'
  | 'STRONGEST_CANDIDATE'
  | 'UNRESOLVED';

const resolution: Record<string, Resolution> = {
  equalLegSemantic: 'SOURCE_CONFIRMED',
  spikeOriginToExtreme: 'STRONGEST_CANDIDATE',
  breakoutToExtreme: 'UNRESOLVED',
  structuralExtremeToExtreme: 'UNRESOLVED',
  exactOHLCAnchor: 'UNRESOLVED',
  abEqualCdTolerance: 'UNRESOLVED',
};

describe('SP2L Leg-1 origin source-resolution guardrails', () => {
  it('locks only the source-confirmed equal-leg semantic', () => {
    expect(resolution.equalLegSemantic).toBe('SOURCE_CONFIRMED');
  });

  it('records Spike-origin to extreme as the strongest candidate without freezing it', () => {
    expect(resolution.spikeOriginToExtreme).toBe('STRONGEST_CANDIDATE');
  });

  it('keeps competing candle-level origins unresolved', () => {
    expect(resolution.breakoutToExtreme).toBe('UNRESOLVED');
    expect(resolution.structuralExtremeToExtreme).toBe('UNRESOLVED');
  });

  it('does not invent executable OHLC anchors or AB=CD tolerance', () => {
    expect(resolution.exactOHLCAnchor).toBe('UNRESOLVED');
    expect(resolution.abEqualCdTolerance).toBe('UNRESOLVED');
  });
});
