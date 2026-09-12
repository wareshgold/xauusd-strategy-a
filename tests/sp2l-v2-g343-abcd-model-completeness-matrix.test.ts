import { describe, expect, it } from 'vitest';
import {
  G343_A_SELECTORS,
  G343_B_SELECTORS,
  G343_C_SELECTORS,
  G343_EXPECTED_MATRIX_SIZE,
  G343_PRICE_FIELDS,
  G343_PROJECTIONS,
  G343_SCALES,
  buildG343ModelCompletenessMatrix,
  g343AllRowsAreResearchOnly,
  g343CoverageSignature,
  g343HasUnresolvedCoverage,
} from '../src/domain/research/sp2l-v2/G343AbcdModelCompletenessMatrix.js';

describe('G343 — AB=CD model completeness matrix', () => {
  it('enumerates the full Cartesian product of known unresolved dimensions', () => {
    const rows = buildG343ModelCompletenessMatrix();

    expect(rows).toHaveLength(G343_EXPECTED_MATRIX_SIZE);
    expect(new Set(rows.map((row) => row.id)).size).toBe(G343_EXPECTED_MATRIX_SIZE);
  });

  it('covers every known selector, price field, scale, and projection', () => {
    const rows = buildG343ModelCompletenessMatrix();
    const signatures = new Set(g343CoverageSignature(rows));

    for (const value of G343_A_SELECTORS) expect(signatures.has(`A:${value}`)).toBe(true);
    for (const value of G343_B_SELECTORS) expect(signatures.has(`B:${value}`)).toBe(true);
    for (const value of G343_C_SELECTORS) expect(signatures.has(`C:${value}`)).toBe(true);
    for (const value of G343_PRICE_FIELDS) expect(signatures.has(`PRICE_FIELD:${value}`)).toBe(true);
    for (const value of G343_SCALES) expect(signatures.has(`SCALE:${value}`)).toBe(true);
    for (const value of G343_PROJECTIONS) expect(signatures.has(`PROJECTION:${value}`)).toBe(true);
  });

  it('marks every matrix row as research-only', () => {
    const rows = buildG343ModelCompletenessMatrix();
    expect(g343AllRowsAreResearchOnly(rows)).toBe(true);
    expect(rows.every((row) => row.canonical === false)).toBe(true);
  });

  it('retains unresolved executable dimensions instead of canonicalizing them', () => {
    const rows = buildG343ModelCompletenessMatrix();

    expect(g343HasUnresolvedCoverage(rows)).toBe(true);
    expect(rows.some((row) => row.aStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
    expect(rows.some((row) => row.priceFieldStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
    expect(rows.some((row) => row.scaleStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
    expect(rows.some((row) => row.cStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
  });

  it('records the source-supported deep origin without treating it as a frozen candle rule', () => {
    const rows = buildG343ModelCompletenessMatrix();
    const deepOriginRows = rows.filter((row) => row.aSelector === 'SOURCE_DEEP_ORIGIN');
    const breakoutRows = rows.filter((row) => row.aSelector === 'FIRST_BREAKOUT_CANDLE');
    const swingRows = rows.filter((row) => row.aSelector === 'NEAREST_SWING');

    expect(deepOriginRows.every((row) => row.aStatus === 'SOURCE_SUPPORTED')).toBe(true);
    expect(breakoutRows.every((row) => row.aStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
    expect(swingRows.every((row) => row.aStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
  });

  it('keeps fill-as-C visible as a negative control, not a canonical candidate', () => {
    const rows = buildG343ModelCompletenessMatrix();
    const fillRows = rows.filter((row) => row.cSelector === 'FILL_AS_C');
    const correctionRows = rows.filter((row) => row.cSelector === 'SOURCE_CORRECTION_REFERENCE');

    expect(fillRows.every((row) => row.cStatus === 'EXPLICITLY_REJECTED_AS_CANONICAL')).toBe(true);
    expect(correctionRows.every((row) => row.cStatus === 'UNRESOLVED_EXECUTABLE')).toBe(true);
  });

  it('does not rank, optimize, or select a winning model', () => {
    const rows = buildG343ModelCompletenessMatrix();

    expect(rows.every((row) => row.projection === 'AB_EQ_CD_TRANSLATION')).toBe(true);
    expect(rows.some((row) => row.id.includes('TOLERANCE'))).toBe(false);
    expect(rows.some((row) => row.id.includes('OPTIMIZED'))).toBe(false);
  });
});
