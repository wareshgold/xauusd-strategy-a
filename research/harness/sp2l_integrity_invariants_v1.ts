export type IntegrityResult = {
  ok: boolean;
  reason?: string;
};

/**
 * Research-only integrity guards. These do not define trading geometry and
 * must never be used to generate production BUY/SELL decisions.
 */
export function assertNoTradingDecisionSurface(value: unknown): IntegrityResult {
  if (value === null || typeof value !== 'object') {
    return { ok: true };
  }

  const forbidden = new Set(['buy', 'sell', 'signal', 'order', 'position']);
  const keys = Object.keys(value as Record<string, unknown>);
  const hit = keys.find((key) => forbidden.has(key.toLowerCase()));

  return hit
    ? { ok: false, reason: `Trading-decision surface detected: ${hit}` }
    : { ok: true };
}

export function assertNoCanonicalPromotionFromPerformance(input: {
  provenanceConfirmed: boolean;
  performanceUsedForPromotion: boolean;
}): IntegrityResult {
  if (input.performanceUsedForPromotion && !input.provenanceConfirmed) {
    return {
      ok: false,
      reason: 'Performance cannot promote non-source-confirmed geometry.',
    };
  }

  return { ok: true };
}

export function assert125RPreserved(input: {
  originalR: number;
  currentR: number;
  originalClassification: string;
  currentClassification: string;
}): IntegrityResult {
  if (input.originalR !== 125 || input.currentR !== 125) {
    return { ok: false, reason: '125R value was changed.' };
  }

  if (
    input.originalClassification !== input.currentClassification
  ) {
    return { ok: false, reason: '125R classification was changed.' };
  }

  return { ok: true };
}
