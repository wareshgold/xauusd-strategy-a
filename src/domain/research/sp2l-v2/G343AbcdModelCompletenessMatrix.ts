import {
  type AnchorSelector,
  type LegScale,
  type PriceField,
  type ProjectionModel,
  type CompetingAbcdModel,
} from './G341AbcdCompetingModels.js';

export const G343_A_SELECTORS: AnchorSelector[] = [
  'SOURCE_DEEP_ORIGIN',
  'FIRST_BREAKOUT_CANDLE',
  'NEAREST_SWING',
];

export const G343_B_SELECTORS: AnchorSelector[] = ['PARENT_B', 'NESTED_B'];

export const G343_C_SELECTORS: AnchorSelector[] = [
  'SOURCE_CORRECTION_REFERENCE',
  'FILL_AS_C',
];

export const G343_PRICE_FIELDS: PriceField[] = [
  'HIGH',
  'LOW',
  'OPEN',
  'CLOSE',
  'BODY_HIGH',
  'BODY_LOW',
];

export const G343_SCALES: LegScale[] = ['PARENT', 'NESTED'];
export const G343_PROJECTIONS: ProjectionModel[] = ['AB_EQ_CD_TRANSLATION'];

export type G343DimensionStatus =
  | 'SOURCE_CONFIRMED'
  | 'SOURCE_SUPPORTED'
  | 'UNRESOLVED_EXECUTABLE'
  | 'EXPLICITLY_REJECTED_AS_CANONICAL';

export type G343MatrixRow = CompetingAbcdModel & {
  aStatus: G343DimensionStatus;
  bStatus: G343DimensionStatus;
  cStatus: G343DimensionStatus;
  priceFieldStatus: G343DimensionStatus;
  scaleStatus: G343DimensionStatus;
  projectionStatus: G343DimensionStatus;
};

export const G343_EXPECTED_MATRIX_SIZE =
  G343_A_SELECTORS.length *
  G343_B_SELECTORS.length *
  G343_C_SELECTORS.length *
  G343_PRICE_FIELDS.length *
  G343_SCALES.length *
  G343_PROJECTIONS.length;

function dimensionStatus(
  dimension: 'A' | 'B' | 'C' | 'PRICE_FIELD' | 'SCALE' | 'PROJECTION',
  value: string,
): G343DimensionStatus {
  if (dimension === 'A' && value === 'SOURCE_DEEP_ORIGIN') return 'SOURCE_SUPPORTED';
  if (dimension === 'A') return 'UNRESOLVED_EXECUTABLE';

  if (dimension === 'B') return 'SOURCE_CONFIRMED';

  if (dimension === 'C' && value === 'FILL_AS_C') {
    return 'EXPLICITLY_REJECTED_AS_CANONICAL';
  }
  if (dimension === 'C') return 'UNRESOLVED_EXECUTABLE';

  if (dimension === 'PRICE_FIELD') return 'UNRESOLVED_EXECUTABLE';

  if (dimension === 'SCALE') return 'UNRESOLVED_EXECUTABLE';

  return 'SOURCE_CONFIRMED';
}

export function buildG343ModelCompletenessMatrix(): G343MatrixRow[] {
  const rows: G343MatrixRow[] = [];

  for (const aSelector of G343_A_SELECTORS) {
    for (const bSelector of G343_B_SELECTORS) {
      for (const cSelector of G343_C_SELECTORS) {
        for (const priceField of G343_PRICE_FIELDS) {
          for (const scale of G343_SCALES) {
            for (const projection of G343_PROJECTIONS) {
              const id = [aSelector, bSelector, cSelector, priceField, scale, projection].join('__');
              rows.push({
                id,
                aSelector,
                bSelector,
                cSelector,
                priceField,
                scale,
                projection,
                canonical: false,
                aStatus: dimensionStatus('A', aSelector),
                bStatus: dimensionStatus('B', bSelector),
                cStatus: dimensionStatus('C', cSelector),
                priceFieldStatus: dimensionStatus('PRICE_FIELD', priceField),
                scaleStatus: dimensionStatus('SCALE', scale),
                projectionStatus: dimensionStatus('PROJECTION', projection),
              });
            }
          }
        }
      }
    }
  }

  return rows;
}

export function g343CoverageSignature(rows: G343MatrixRow[]): string[] {
  return [...new Set(rows.flatMap((row) => [
    `A:${row.aSelector}`,
    `B:${row.bSelector}`,
    `C:${row.cSelector}`,
    `PRICE_FIELD:${row.priceField}`,
    `SCALE:${row.scale}`,
    `PROJECTION:${row.projection}`,
  ]))].sort();
}

export function g343AllRowsAreResearchOnly(rows: G343MatrixRow[]): boolean {
  return rows.every((row) => row.canonical === false);
}

export function g343HasUnresolvedCoverage(rows: G343MatrixRow[]): boolean {
  return rows.some((row) =>
    [row.aStatus, row.cStatus, row.priceFieldStatus, row.scaleStatus].includes('UNRESOLVED_EXECUTABLE'),
  );
}
