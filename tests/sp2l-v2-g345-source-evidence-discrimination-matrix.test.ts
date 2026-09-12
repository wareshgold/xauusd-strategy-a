import { describe, expect, it } from 'vitest';
import {
  G345_SOURCE_EVIDENCE_MATRIX,
  G345_UNRESOLVED_IDS,
  g345EveryUnresolvedDimensionHasEvidenceRequirement,
  g345NoUnresolvedDimensionIsMarkedResolved,
} from '../src/domain/research/sp2l-v2/G345SourceEvidenceDiscriminationMatrix.js';

describe('SP2L G345 source-evidence discrimination matrix', () => {
  it('covers every unresolved executable dimension with an explicit evidence requirement', () => {
    expect(G345_UNRESOLVED_IDS.length).toBeGreaterThan(0);
    expect(g345EveryUnresolvedDimensionHasEvidenceRequirement()).toBe(true);
  });

  it('does not falsely resolve unresolved geometry', () => {
    expect(g345NoUnresolvedDimensionIsMarkedResolved()).toBe(true);
    expect(G345_UNRESOLVED_IDS).toEqual(expect.arrayContaining([
      'A_SELECTOR',
      'B_SELECTOR',
      'PRICE_FIELDS',
      'C_ANCHOR',
      'WICK_BODY',
      'SCALE',
      'D_FORMULA',
      'TOLERANCE',
      'TP_MAPPING',
      'P_GAP',
    ]));
  });

  it('retains explicit source confirmation and rejection separately from unresolved geometry', () => {
    expect(G345_SOURCE_EVIDENCE_MATRIX.find((row) => row.id === 'AB_EQ_CD_SEMANTIC')?.outcome).toBe('RESOLVED');
    expect(G345_SOURCE_EVIDENCE_MATRIX.find((row) => row.id === 'FILL_AS_C')?.outcome).toBe('SOURCE_REJECTED');
  });

  it('does not contain a ranking or optimization decision', () => {
    expect(JSON.stringify(G345_SOURCE_EVIDENCE_MATRIX)).not.toContain('winner');
    expect(JSON.stringify(G345_SOURCE_EVIDENCE_MATRIX)).not.toContain('optimize');
    expect(JSON.stringify(G345_SOURCE_EVIDENCE_MATRIX)).not.toContain('best');
  });
});
