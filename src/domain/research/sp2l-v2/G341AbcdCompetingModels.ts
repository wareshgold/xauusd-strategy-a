export type PriceField = 'HIGH' | 'LOW' | 'OPEN' | 'CLOSE' | 'BODY_HIGH' | 'BODY_LOW';

export type AnchorSelector =
  | 'SOURCE_DEEP_ORIGIN'
  | 'FIRST_BREAKOUT_CANDLE'
  | 'NEAREST_SWING'
  | 'PARENT_B'
  | 'NESTED_B'
  | 'SOURCE_CORRECTION_REFERENCE'
  | 'FILL_AS_C';

export type LegScale = 'PARENT' | 'NESTED';

export type ProjectionModel = 'AB_EQ_CD_TRANSLATION';

export type SyntheticCandle = {
  id: string;
  index: number;
  open: number;
  high: number;
  low: number;
  close: number;
};

export type CompetingAbcdModel = {
  id: string;
  aSelector: AnchorSelector;
  bSelector: AnchorSelector;
  cSelector: AnchorSelector;
  priceField: PriceField;
  scale: LegScale;
  projection: ProjectionModel;
  canonical: false;
};

export type ModelEvaluation = {
  modelId: string;
  aId: string;
  bId: string;
  cId: string;
  aPrice: number;
  bPrice: number;
  cPrice: number;
  projectedD: number;
};

export const G341_SOURCE_SEMANTIC_FIXTURE: SyntheticCandle[] = [
  { id: 'range', index: 0, open: 100, high: 102, low: 98, close: 101 },
  { id: 'deep-origin', index: 1, open: 101, high: 103, low: 94, close: 99 },
  { id: 'breakout', index: 2, open: 99, high: 111, low: 97, close: 108 },
  { id: 'parent-b', index: 3, open: 108, high: 116, low: 106, close: 114 },
  { id: 'nested-b', index: 4, open: 112, high: 115, low: 109, close: 113 },
  { id: 'swing-near-b', index: 5, open: 113, high: 114, low: 105, close: 107 },
  { id: 'correction', index: 6, open: 107, high: 109, low: 101, close: 103 },
  { id: 'pending', index: 7, open: 103, high: 106, low: 99, close: 101 },
  { id: 'fill', index: 8, open: 101, high: 104, low: 98, close: 100 },
  { id: 'leg2-end', index: 9, open: 100, high: 116, low: 99, close: 114 },
];

export const G341_MODELS: CompetingAbcdModel[] = [
  {
    id: 'SOURCE_DEEP_LOW_TO_PARENT_HIGH__CORRECTION_LOW__WICK',
    aSelector: 'SOURCE_DEEP_ORIGIN',
    bSelector: 'PARENT_B',
    cSelector: 'SOURCE_CORRECTION_REFERENCE',
    priceField: 'LOW',
    scale: 'PARENT',
    projection: 'AB_EQ_CD_TRANSLATION',
    canonical: false,
  },
  {
    id: 'BREAKOUT_CLOSE_TO_PARENT_CLOSE__CORRECTION_CLOSE__BODY',
    aSelector: 'FIRST_BREAKOUT_CANDLE',
    bSelector: 'PARENT_B',
    cSelector: 'SOURCE_CORRECTION_REFERENCE',
    priceField: 'CLOSE',
    scale: 'PARENT',
    projection: 'AB_EQ_CD_TRANSLATION',
    canonical: false,
  },
  {
    id: 'NEAREST_SWING_TO_NESTED_HIGH__CORRECTION_HIGH__WICK',
    aSelector: 'NEAREST_SWING',
    bSelector: 'NESTED_B',
    cSelector: 'SOURCE_CORRECTION_REFERENCE',
    priceField: 'HIGH',
    scale: 'NESTED',
    projection: 'AB_EQ_CD_TRANSLATION',
    canonical: false,
  },
  {
    id: 'SOURCE_ORIGIN_TO_PARENT_HIGH__FILL_AS_C__WICK',
    aSelector: 'SOURCE_DEEP_ORIGIN',
    bSelector: 'PARENT_B',
    cSelector: 'FILL_AS_C',
    priceField: 'LOW',
    scale: 'PARENT',
    projection: 'AB_EQ_CD_TRANSLATION',
    canonical: false,
  },
];

function bodyHigh(candle: SyntheticCandle): number {
  return Math.max(candle.open, candle.close);
}

function bodyLow(candle: SyntheticCandle): number {
  return Math.min(candle.open, candle.close);
}

export function selectPrice(candle: SyntheticCandle, field: PriceField): number {
  switch (field) {
    case 'HIGH':
      return candle.high;
    case 'LOW':
      return candle.low;
    case 'OPEN':
      return candle.open;
    case 'CLOSE':
      return candle.close;
    case 'BODY_HIGH':
      return bodyHigh(candle);
    case 'BODY_LOW':
      return bodyLow(candle);
  }
}

function event(candles: SyntheticCandle[], id: string): SyntheticCandle {
  const value = candles.find((candle) => candle.id === id);
  if (!value) throw new Error(`FIXTURE_CANDLE_MISSING:${id}`);
  return value;
}

export function resolveSelector(candles: SyntheticCandle[], selector: AnchorSelector): string {
  switch (selector) {
    case 'SOURCE_DEEP_ORIGIN':
      return 'deep-origin';
    case 'FIRST_BREAKOUT_CANDLE':
      return 'breakout';
    case 'NEAREST_SWING':
      return 'swing-near-b';
    case 'PARENT_B':
      return 'parent-b';
    case 'NESTED_B':
      return 'nested-b';
    case 'SOURCE_CORRECTION_REFERENCE':
      return 'correction';
    case 'FILL_AS_C':
      return 'fill';
  }
}

export function evaluateModel(candles: SyntheticCandle[], model: CompetingAbcdModel): ModelEvaluation {
  const aId = resolveSelector(candles, model.aSelector);
  const bId = resolveSelector(candles, model.bSelector);
  const cId = resolveSelector(candles, model.cSelector);
  const a = event(candles, aId);
  const b = event(candles, bId);
  const c = event(candles, cId);
  const aPrice = selectPrice(a, model.priceField);
  const bPrice = selectPrice(b, model.priceField);
  const cPrice = selectPrice(c, model.priceField);
  const projectedD = cPrice + (bPrice - aPrice);

  return { modelId: model.id, aId, bId, cId, aPrice, bPrice, cPrice, projectedD };
}

export function allModelsRemainNonCanonical(models: CompetingAbcdModel[]): boolean {
  return models.every((model) => model.canonical === false);
}
