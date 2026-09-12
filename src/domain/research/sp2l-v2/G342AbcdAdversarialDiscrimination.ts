import {
  evaluateModel,
  G341_MODELS,
  G341_SOURCE_SEMANTIC_FIXTURE,
  SyntheticCandle,
  ModelEvaluation,
} from './G341AbcdCompetingModels.js';

export type G342Fixture = {
  id: string;
  candles: SyntheticCandle[];
  purpose: string;
};

export const G342_BASELINE: G342Fixture = {
  id: 'BASELINE',
  candles: G341_SOURCE_SEMANTIC_FIXTURE,
  purpose: 'Baseline source-semantic sequence used to compare unresolved anchor hypotheses.',
};

export const G342_NEAREST_SWING_DISTRACTOR: G342Fixture = {
  id: 'NEAREST_SWING_DISTRACTOR',
  candles: G341_SOURCE_SEMANTIC_FIXTURE.map((candle) =>
    candle.id === 'swing-near-b'
      ? { ...candle, open: 118, high: 124, low: 104, close: 119 }
      : candle,
  ),
  purpose: 'Perturbs the candidate local swing while leaving source-semantic deep-origin, parent-B, correction, pending, and fill events unchanged.',
};

export const G342_PRICE_FIELD_DISCRIMINATOR: G342Fixture = {
  id: 'PRICE_FIELD_DISCRIMINATOR',
  candles: G341_SOURCE_SEMANTIC_FIXTURE.map((candle) =>
    candle.id === 'deep-origin'
      ? { ...candle, open: 96, close: 100, low: 90, high: 104 }
      : candle.id === 'parent-b'
        ? { ...candle, open: 110, close: 115, low: 105, high: 120 }
        : candle,
  ),
  purpose: 'Widens wick/body/close divergence at source-semantic anchors so price-field hypotheses cannot collapse accidentally.',
};

export const G342_NESTED_PARENT_DISCRIMINATOR: G342Fixture = {
  id: 'NESTED_PARENT_DISCRIMINATOR',
  candles: G341_SOURCE_SEMANTIC_FIXTURE.map((candle) =>
    candle.id === 'nested-b'
      ? { ...candle, high: 118, low: 108, open: 111, close: 117 }
      : candle.id === 'parent-b'
        ? { ...candle, high: 125, low: 105, open: 107, close: 123 }
        : candle,
  ),
  purpose: 'Widens parent-versus-nested structural scale divergence.',
};

export function evaluateFixture(fixture: G342Fixture): ModelEvaluation[] {
  return G341_MODELS.map((model) => evaluateModel(fixture.candles, model));
}

export function projectedDByModel(fixture: G342Fixture): Map<string, number> {
  return new Map(evaluateFixture(fixture).map((result) => [result.modelId, result.projectedD]));
}

export function differingModelIds(fixture: G342Fixture): string[] {
  const values = projectedDByModel(fixture);
  const entries = [...values.entries()];
  if (entries.length === 0) return [];
  const baseline = entries[0]![1];
  return entries.filter(([, value]) => value !== baseline).map(([id]) => id);
}

export function everyModelIsResearchOnly(): boolean {
  return G341_MODELS.every((model) => model.canonical === false);
}
