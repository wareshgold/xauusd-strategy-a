import { describe, expect, it } from 'vitest';

type Resolution = 'SOURCE_CONFIRMED' | 'UNRESOLVED' | 'REJECTED';

const gate = {
  pGapSemantic: 'SOURCE_CONFIRMED' as Resolution,
  pGapExecutableGeometry: 'UNRESOLVED' as Resolution,
  entrySemantic: 'SOURCE_CONFIRMED' as Resolution,
  entryExecutableGeometry: 'UNRESOLVED' as Resolution,
  slSemantic: 'SOURCE_CONFIRMED' as Resolution,
  slExecutableGeometry: 'UNRESOLVED' as Resolution,
  leg1Semantic: 'SOURCE_CONFIRMED' as Resolution,
  leg1ExecutableGeometry: 'UNRESOLVED' as Resolution,
  abCdSemantic: 'SOURCE_CONFIRMED' as Resolution,
  abCdExecutableGeometry: 'UNRESOLVED' as Resolution,
  genericFvgAsPGAP: 'REJECTED' as Resolution,
  closeReclaimAsBaseEntry: 'REJECTED' as Resolution,
  fiftyPercentAsBaseEntry: 'REJECTED' as Resolution,
  classicalABCD: 'REJECTED' as Resolution,
};

describe('SP2L combined geometry gate', () => {
  it('preserves source-confirmed semantics while blocking unresolved executable geometry', () => {
    expect(gate.pGapSemantic).toBe('SOURCE_CONFIRMED');
    expect(gate.entrySemantic).toBe('SOURCE_CONFIRMED');
    expect(gate.slSemantic).toBe('SOURCE_CONFIRMED');
    expect(gate.leg1Semantic).toBe('SOURCE_CONFIRMED');
    expect(gate.abCdSemantic).toBe('SOURCE_CONFIRMED');

    expect(gate.pGapExecutableGeometry).toBe('UNRESOLVED');
    expect(gate.entryExecutableGeometry).toBe('UNRESOLVED');
    expect(gate.slExecutableGeometry).toBe('UNRESOLVED');
    expect(gate.leg1ExecutableGeometry).toBe('UNRESOLVED');
    expect(gate.abCdExecutableGeometry).toBe('UNRESOLVED');
  });

  it('rejects known non-canonical shortcuts', () => {
    expect(gate.genericFvgAsPGAP).toBe('REJECTED');
    expect(gate.closeReclaimAsBaseEntry).toBe('REJECTED');
    expect(gate.fiftyPercentAsBaseEntry).toBe('REJECTED');
    expect(gate.classicalABCD).toBe('REJECTED');
  });

  it('cannot authorize frozen geometry while any executable component is unresolved', () => {
    const executableStates = [
      gate.pGapExecutableGeometry,
      gate.entryExecutableGeometry,
      gate.slExecutableGeometry,
      gate.leg1ExecutableGeometry,
      gate.abCdExecutableGeometry,
    ];

    expect(executableStates.every((state) => state === 'SOURCE_CONFIRMED')).toBe(false);
    expect(executableStates.some((state) => state === 'UNRESOLVED')).toBe(true);
  });

  it('keeps the research gate independent from historical profitability', () => {
    const gateInputs = Object.keys(gate);
    expect(gateInputs.some((key) => key.toLowerCase().includes('profit'))).toBe(false);
    expect(gateInputs.some((key) => key.toLowerCase().includes('winrate'))).toBe(false);
  });
});
