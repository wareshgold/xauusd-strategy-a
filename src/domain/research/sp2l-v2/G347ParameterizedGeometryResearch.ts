import {
  G341_SOURCE_SEMANTIC_FIXTURE,
  type AnchorSelector,
  type PriceField,
  type SyntheticCandle,
  selectPrice,
  resolveSelector,
} from './G341AbcdCompetingModels.js';

export type G347Dimension =
  | 'A_SELECTOR'
  | 'B_SELECTOR'
  | 'C_SELECTOR'
  | 'PRICE_FIELD'
  | 'SCALE'
  | 'PROJECTION'
  | 'TOLERANCE'
  | 'TP_MAPPING'
  | 'P_GAP_HYPOTHESIS';

export type G347Candidate = {
  id: string;
  dimension: G347Dimension;
  value: string;
  canonical: false;
};

export type G347GeometryModel = {
  id: string;
  aSelector: AnchorSelector;
  bSelector: AnchorSelector;
  cSelector: AnchorSelector;
  priceField: PriceField;
  scale: 'PARENT' | 'NESTED';
  projection: 'AB_EQ_CD_TRANSLATION';
  tolerance: number | null;
  tpMapping: 'D' | 'D_PLUS_1R' | 'D_PLUS_2R' | 'UNRESOLVED';
  pGapHypothesis: 'UNRESOLVED' | 'THREE_CANDLE_RANGE_GAP' | 'BODY_BOUNDARY_GAP';
  canonical: false;
};

export type G347Evaluation = {
  modelId: string;
  aId: string;
  bId: string;
  cId: string;
  aPrice: number;
  bPrice: number;
  cPrice: number;
  projectedD: number;
  tolerance: number | null;
  tpMapping: G347GeometryModel['tpMapping'];
  pGapHypothesis: G347GeometryModel['pGapHypothesis'];
};

export const G347_PARAMETER_SPACE = {
  aSelectors: ['SOURCE_DEEP_ORIGIN', 'FIRST_BREAKOUT_CANDLE', 'NEAREST_SWING'] as const,
  bSelectors: ['PARENT_B', 'NESTED_B'] as const,
  cSelectors: ['SOURCE_CORRECTION_REFERENCE', 'FILL_AS_C'] as const,
  priceFields: ['HIGH', 'LOW', 'OPEN', 'CLOSE', 'BODY_HIGH', 'BODY_LOW'] as const,
  scales: ['PARENT', 'NESTED'] as const,
  projections: ['AB_EQ_CD_TRANSLATION'] as const,
  tolerances: [null, 0, 0.5, 1] as const,
  tpMappings: ['D', 'D_PLUS_1R', 'D_PLUS_2R', 'UNRESOLVED'] as const,
  pGapHypotheses: ['UNRESOLVED', 'THREE_CANDLE_RANGE_GAP', 'BODY_BOUNDARY_GAP'] as const,
};

export const G347_BASELINE_MODEL: G347GeometryModel = {
  id: 'G347_BASELINE',
  aSelector: 'SOURCE_DEEP_ORIGIN',
  bSelector: 'PARENT_B',
  cSelector: 'SOURCE_CORRECTION_REFERENCE',
  priceField: 'LOW',
  scale: 'PARENT',
  projection: 'AB_EQ_CD_TRANSLATION',
  tolerance: null,
  tpMapping: 'UNRESOLVED',
  pGapHypothesis: 'UNRESOLVED',
  canonical: false,
};

export const G347_SOURCE_FIXTURE: SyntheticCandle[] = [
  ...G341_SOURCE_SEMANTIC_FIXTURE,
  { id: 'gap-left', index: 10, open: 114, high: 116, low: 113, close: 115 },
  { id: 'gap-middle', index: 11, open: 115, high: 120, low: 114, close: 119 },
  { id: 'gap-right', index: 12, open: 119, high: 125, low: 118, close: 124 },
];

function price(candles: SyntheticCandle[], selector: AnchorSelector, field: PriceField): number {
  const id = resolveSelector(candles, selector);
  const candle = candles.find((item) => item.id === id);
  if (!candle) throw new Error(`FIXTURE_CANDLE_MISSING:${id}`);
  return selectPrice(candle, field);
}

export function evaluateG347Model(candles: SyntheticCandle[], model: G347GeometryModel): G347Evaluation {
  const aId = resolveSelector(candles, model.aSelector);
  const bId = resolveSelector(candles, model.bSelector);
  const cId = resolveSelector(candles, model.cSelector);
  const aPrice = price(candles, model.aSelector, model.priceField);
  const bPrice = price(candles, model.bSelector, model.priceField);
  const cPrice = price(candles, model.cSelector, model.priceField);

  // Research-only AB=CD translation. This is not a frozen production formula.
  const projectedD = cPrice + (bPrice - aPrice);
  return {
    modelId: model.id,
    aId,
    bId,
    cId,
    aPrice,
    bPrice,
    cPrice,
    projectedD,
    tolerance: model.tolerance,
    tpMapping: model.tpMapping,
    pGapHypothesis: model.pGapHypothesis,
  };
}

export function g347Model(id: string, patch: Partial<Omit<G347GeometryModel, 'id' | 'canonical'>>): G347GeometryModel {
  return { ...G347_BASELINE_MODEL, ...patch, id, canonical: false };
}

export function compareG347Models(left: G347GeometryModel, right: G347GeometryModel): {
  projectedDDiffers: boolean;
  anchorSelectionDiffers: boolean;
  priceFieldDiffers: boolean;
  targetMappingDiffers: boolean;
  pGapHypothesisDiffers: boolean;
} {
  const l = evaluateG347Model(G347_SOURCE_FIXTURE, left);
  const r = evaluateG347Model(G347_SOURCE_FIXTURE, right);
  return {
    projectedDDiffers: l.projectedD !== r.projectedD,
    anchorSelectionDiffers: l.aId !== r.aId || l.bId !== r.bId || l.cId !== r.cId,
    priceFieldDiffers: l.aPrice !== r.aPrice || l.bPrice !== r.bPrice || l.cPrice !== r.cPrice,
    targetMappingDiffers: l.tpMapping !== r.tpMapping,
    pGapHypothesisDiffers: l.pGapHypothesis !== r.pGapHypothesis,
  };
}

export function allG347CandidatesRemainNonCanonical(candidates: G347Candidate[]): boolean {
  return candidates.every((candidate) => candidate.canonical === false);
}

export function g347NoCandidateIsCanonical(models: G347GeometryModel[]): boolean {
  return models.every((model) => model.canonical === false);
}
