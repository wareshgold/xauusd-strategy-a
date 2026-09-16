/**
 * Immutable research reference for the persisted 125R forensic observation.
 *
 * This fixture preserves observed values only. It does not define canonical
 * SP2L geometry, execution semantics, or any BUY/SELL decision surface.
 */
export const SP2L_125R_GOLDEN_FIXTURE = Object.freeze({
  fixtureId: 'SP2L-125R-2026-08-20-20:54:00',
  direction: 'SELL',
  entry: 4521.5838,
  stopLoss: 4521.61331,
  tp1: 4517.8892399999995,
  riskDistance: 0.02951,
  rMultiple: 125.19688241535353,
  sourceClassification: 'UNRESOLVED_AT_SOURCE_LEVEL',
} as const);

export type Sp2l125RGoldenFixture = typeof SP2L_125R_GOLDEN_FIXTURE;
