import {
  G341_SOURCE_SEMANTIC_FIXTURE,
  type CompetingAbcdModel,
  type PriceField,
  type AnchorSelector,
  evaluateModel,
} from './G341AbcdCompetingModels.js';

export type G344Dimension = 'A_SELECTOR' | 'B_SELECTOR' | 'C_SELECTOR' | 'PRICE_FIELD' | 'SCALE' | 'PROJECTION';

export type G344MinimalPair = {
  dimension: G344Dimension;
  left: CompetingAbcdModel;
  right: CompetingAbcdModel;
};

export type G344PairResult = {
  dimension: G344Dimension;
  leftProjectedD: number;
  rightProjectedD: number;
  discriminates: boolean;
};

const baseline: CompetingAbcdModel = {
  id: 'G344_BASELINE',
  aSelector: 'SOURCE_DEEP_ORIGIN',
  bSelector: 'PARENT_B',
  cSelector: 'SOURCE_CORRECTION_REFERENCE',
  priceField: 'LOW',
  scale: 'PARENT',
  projection: 'AB_EQ_CD_TRANSLATION',
  canonical: false,
};

function variant(
  id: string,
  patch: Partial<Pick<CompetingAbcdModel, 'aSelector' | 'bSelector' | 'cSelector' | 'priceField' | 'scale' | 'projection'>>,
): CompetingAbcdModel {
  return { ...baseline, ...patch, id, canonical: false };
}

export const G344_MINIMAL_PAIRS: G344MinimalPair[] = [
  {
    dimension: 'A_SELECTOR',
    left: baseline,
    right: variant('G344_A_FIRST_BREAKOUT', { aSelector: 'FIRST_BREAKOUT_CANDLE' }),
  },
  {
    dimension: 'B_SELECTOR',
    left: baseline,
    right: variant('G344_B_NESTED', { bSelector: 'NESTED_B' }),
  },
  {
    dimension: 'C_SELECTOR',
    left: baseline,
    right: variant('G344_C_FILL_NEGATIVE_CONTROL', { cSelector: 'FILL_AS_C' }),
  },
  {
    dimension: 'PRICE_FIELD',
    left: baseline,
    right: variant('G344_PRICE_CLOSE', { priceField: 'CLOSE' }),
  },
  {
    dimension: 'SCALE',
    left: baseline,
    right: variant('G344_SCALE_NESTED', { scale: 'NESTED' }),
  },
];

export const G344_NON_CANONICAL_DIMENSIONS: G344Dimension[] = [
  'A_SELECTOR',
  'B_SELECTOR',
  'C_SELECTOR',
  'PRICE_FIELD',
  'SCALE',
];

export function evaluateG344Pair(pair: G344MinimalPair): G344PairResult {
  const left = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, pair.left);
  const right = evaluateModel(G341_SOURCE_SEMANTIC_FIXTURE, pair.right);

  return {
    dimension: pair.dimension,
    leftProjectedD: left.projectedD,
    rightProjectedD: right.projectedD,
    discriminates: left.projectedD !== right.projectedD,
  };
}

export function evaluateAllG344Pairs(): G344PairResult[] {
  return G344_MINIMAL_PAIRS.map(evaluateG344Pair);
}

export function g344PairsRemainResearchOnly(pairs: G344MinimalPair[]): boolean {
  return pairs.every((pair) => pair.left.canonical === false && pair.right.canonical === false);
}

export function g344CoveredDimensions(pairs: G344MinimalPair[]): G344Dimension[] {
  return [...new Set(pairs.map((pair) => pair.dimension))].sort() as G344Dimension[];
}

export function g344ProjectionSingletonIsNotInvented(): boolean {
  return baseline.projection === 'AB_EQ_CD_TRANSLATION';
}

export type { AnchorSelector, PriceField };
