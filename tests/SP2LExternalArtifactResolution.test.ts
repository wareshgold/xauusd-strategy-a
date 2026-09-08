import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'CORROBORATIVE' | 'UNRESOLVED' | 'REJECTED';

const resolution = {
  spikeOriginSL: 'CORROBORATIVE' as Resolution,
  equalLegConcept: 'SOURCE_CONFIRMED' as Resolution,
  oneToOneTP: 'SOURCE_CONFIRMED' as Resolution,
  threeCandleSpike: 'CORROBORATIVE' as Resolution,
  body65Percent: 'CORROBORATIVE' as Resolution,
  numericSpikeThreshold: 'CORROBORATIVE' as Resolution,
  genericFVGAsPGAP: 'REJECTED' as Resolution,
  exactPGAPFormula: 'UNRESOLVED' as Resolution,
  lastSpikeCandleBreakAsEntry: 'CORROBORATIVE' as Resolution,
  pendingLimitExecution: 'SOURCE_CONFIRMED' as Resolution,
  exactEntryCandle: 'UNRESOLVED' as Resolution,
  exactSLPrice: 'UNRESOLVED' as Resolution,
};

describe('SP2L external artifact resolution guardrails', () => {
  it('does not promote protected/secondary implementation details to source truth', () => {
    expect(resolution.body65Percent).toBe('CORROBORATIVE');
    expect(resolution.numericSpikeThreshold).toBe('CORROBORATIVE');
    expect(resolution.threeCandleSpike).toBe('CORROBORATIVE');
  });

  it('does not equate generic FVG with canonical P-Gap', () => {
    expect(resolution.genericFVGAsPGAP).toBe('REJECTED');
    expect(resolution.exactPGAPFormula).toBe('UNRESOLVED');
  });

  it('preserves source-confirmed pending-limit semantics', () => {
    expect(resolution.pendingLimitExecution).toBe('SOURCE_CONFIRMED');
    expect(resolution.lastSpikeCandleBreakAsEntry).toBe('CORROBORATIVE');
  });

  it('keeps executable entry and SL prices unresolved', () => {
    expect(resolution.exactEntryCandle).toBe('UNRESOLVED');
    expect(resolution.exactSLPrice).toBe('UNRESOLVED');
  });
});
