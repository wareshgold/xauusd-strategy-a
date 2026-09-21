import type { Direction } from './sp2l_author_replica_candidate.js';

export type UnresolvedFeature =
  | 'F08' | 'F09' | 'F10' | 'F11' | 'F12' | 'F13' | 'F14' | 'F15'
  | 'P-GAP' | 'ROUND-LEVEL';

export type EvidenceState = 'UNRESOLVED' | 'SOURCE_CONFIRMED_EXECUTABLE';
export type EventKind =
  | 'touch' | 'breach' | 'close' | 'placement' | 'trigger'
  | 'activation' | 'fill' | 'delete' | 'replace' | 'none';

export interface SyntheticFixture {
  readonly id: string;
  readonly feature: UnresolvedFeature;
  readonly direction?: Direction;
  readonly candidates: readonly string[];
  readonly events: readonly EventKind[];
  readonly evidenceState: EvidenceState;
  readonly canonicalEligible: false;
  readonly forbiddenInference: string;
}

export interface FixtureEvaluation {
  readonly id: string;
  readonly canonicalEligible: false;
  readonly preservedCandidates: readonly string[];
  readonly preservedEvents: readonly EventKind[];
  readonly sourceState: EvidenceState;
}

export function evaluateUnresolvedFixture(fixture: SyntheticFixture): FixtureEvaluation {
  if (fixture.canonicalEligible !== false) {
    throw new Error('Unresolved fixture ' + fixture.id + ' cannot be canonical-eligible');
  }
  return {
    id: fixture.id,
    canonicalEligible: false,
    preservedCandidates: [...fixture.candidates],
    preservedEvents: [...fixture.events],
    sourceState: fixture.evidenceState,
  };
}

const f = (
  id: string,
  feature: UnresolvedFeature,
  candidates: readonly string[],
  events: readonly EventKind[],
  forbiddenInference: string,
  direction?: Direction,
): SyntheticFixture => ({
  id,
  feature,
  direction,
  candidates,
  events,
  evidenceState: 'UNRESOLVED',
  canonicalEligible: false,
  forbiddenInference,
});

export const UNRESOLVED_SYNTHETIC_FIXTURES: readonly SyntheticFixture[] = [
  f('F08-001', 'F08', ['original-low', 'later-higher-low'], [], 'latest-vs-original swing selection'),
  f('F08-002', 'F08', ['original-low'], [], 'universal swing selector'),
  f('F08-003', 'F08', ['equal-low-first', 'equal-low-second'], [], 'implicit tie-break'),
  f('F08-004', 'F08', ['bearish-lh-1', 'bearish-lh-2'], [], 'bullish-to-bearish symmetry', 'SELL'),
  f('F09-001', 'F09', ['base-entry', 'latest-structure-entry'], ['placement'], 'entry anchor selection'),
  f('F09-002', 'F09', ['open', 'high', 'low', 'close', 'wick', 'body'], [], 'OHLC/wick/body field selection'),
  f('F09-003', 'F09', ['old-entry', 'new-structural-entry'], ['replace'], 'automatic entry update'),
  f('F09-004', 'F09', ['entry-reference-a', 'entry-reference-b'], [], 'entry precedence'),
  f('F10-001', 'F10', ['spike-wick', 'spike-body'], [], 'wick-vs-body stop anchor'),
  f('F10-002', 'F10', ['spike-extreme', 'structural-reference'], [], 'stop anchor selection'),
  f('F10-003', 'F10', ['structural-stop', 'fixed-distance-stop'], [], 'risk-budget selection'),
  f('F10-004', 'F10', ['geometry-spread-zero', 'geometry-spread-nonzero'], [], 'spread promoted into geometry'),
  f('F10-005', 'F10', ['old-stop', 'new-stop'], ['replace'], 'automatic stop refresh'),
  f('F11-001', 'F11', ['pending-order'], ['placement'], 'pending=active position'),
  f('F11-002', 'F11', ['old-reference', 'new-reference'], ['delete', 'replace'], 'structural update causes replacement'),
  f('F11-003', 'F11', ['structural-change', 'unchanged-structure', 'elapsed-candles'], ['delete'], 'delete cause'),
  f('F11-004', 'F11', ['wait-1', 'wait-2', 'wait-3', 'wait-longer'], [], 'timeout threshold'),
  f('F11-005', 'F11', ['old-order', 'new-order'], ['replace'], 'replacement threshold'),
  f('F11-006', 'F11', ['touch', 'breach', 'close'], ['touch', 'breach', 'close', 'fill'], 'touch=fill'),
  f('F12-001', 'F12', ['touch', 'breach', 'close'], ['touch', 'breach', 'close', 'trigger'], 'trigger event semantics'),
  f('F12-002', 'F12', ['trigger', 'activation'], ['trigger', 'activation'], 'trigger=activation'),
  f('F12-003', 'F12', ['activation', 'fill'], ['activation', 'fill'], 'activation=fill'),
  f('F12-004', 'F12', ['one-candle', 'two-candle', 'three-candle'], ['trigger'], 'invented 1/2/3 mapping'),
  f('F12-005', 'F12', ['trigger-a', 'trigger-b'], ['trigger'], 'trigger precedence'),
  f('F13-001', 'F13', ['2x-no-coordinate'], [], '2X visual position as price rule'),
  f('F13-002', 'F13', ['half-target-candidate'], [], '2X=50% inference'),
  f('F13-003', 'F13', ['tp1', 'tp2', 'entry', 'sl'], [], '2X target binding'),
  f('F13-004', 'F13', ['entry', 'sl', 'r'], [], 'R-derived 2X geometry'),
  f('PG-001', 'P-GAP', ['pressure-start-a', 'pressure-start-b'], [], 'pressure boundary'),
  f('PG-002', 'P-GAP', ['high', 'low', 'open', 'close', 'body', 'wick'], [], 'gap endpoint field'),
  f('PG-003', 'P-GAP', ['index-a', 'index-b'], [], 'fixed candle indexing'),
  f('PG-004', 'P-GAP', ['below-threshold', 'at-threshold', 'above-threshold'], [], 'performance-selected threshold'),
  f('PG-005', 'P-GAP', ['bullish', 'bearish'], [], 'synthetic bearish mirror'),
  f('PG-006', 'P-GAP', ['gap-only', 'extended-order-space'], [], 'order-space boundary'),
  f('F14-001', 'F14', ['A1/B1/C1/D1', 'A2/B2/C2/D2'], [], 'automatic A/B/C/D anchors'),
  f('F14-002', 'F14', ['wick', 'body', 'ohlc'], [], 'anchor field selection'),
  f('F14-003', 'F14', ['observed-D', 'projected-D', 'incomplete-D'], [], 'D completion semantics'),
  f('F14-004', 'F14', ['exact-equality', 'small-deviation', 'large-deviation'], [], 'AB=CD tolerance'),
  f('F15-001', 'F15', ['bullish-rule', 'mirrored-bearish-rule'], [], 'bullish-to-bearish symmetry', 'SELL'),
  f('F15-002', 'F15', ['sell-high', 'sell-wick', 'sell-body', 'sell-low'], [], 'bearish price-field selection', 'SELL'),
  f('F15-003', 'F15', ['sell-limit', 'trigger', 'delete', 'replace', 'activation', 'fill'], ['placement', 'trigger', 'delete', 'replace', 'activation', 'fill'], 'invented bearish lifecycle', 'SELL'),
  f('ROUND-001', 'ROUND-LEVEL', ['round-level-near', 'no-round-level'], [], 'round level affects execution'),
  f('ROUND-002', 'ROUND-LEVEL', ['distance-a', 'distance-b', 'distance-c'], [], 'round-level threshold'),
  f('ROUND-003', 'ROUND-LEVEL', ['with-round-level', 'without-round-level'], [], 'round-level binding'),
  f('SAFETY-001', 'F09', ['required-geometry-unresolved'], [], 'unresolved geometry may produce canonical signal'),
  f('SAFETY-002', 'F10', ['backtest-preferred-a', 'backtest-preferred-b'], [], 'backtest selects source rule'),
  f('SAFETY-003', 'P-GAP', ['implementation-formula'], [], 'implementation promotes to source'),
  f('SAFETY-004', 'F15', ['bullish-complete', 'bearish-incomplete'], [], 'synthetic bearish symmetry'),
  f('SAFETY-005', 'F12', ['price-touch', 'successful-fill'], ['touch', 'fill'], 'touch=fill'),
] as const;
