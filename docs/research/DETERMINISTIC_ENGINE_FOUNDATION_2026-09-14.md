# Deterministic Engine Foundation — 2026-09-14

## Purpose

Advance implementation without creating an infinite source-resolution loop.

The current source corpus does not justify promoting unresolved P-Gap geometry,
A/B/C/D anchors, pending-limit fill semantics, exact structural stop boundary,
or target mapping into canonical Strategy A rules. Those remain outside the
production decision boundary.

## Implementation decision

The project now has an execution-neutral deterministic replay boundary with:

- typed XAUUSD candle and market-snapshot contracts;
- structured signal candidates;
- explicit strategy/version/rule provenance;
- a replay engine that evaluates one candle at a time;
- a hard `canonical=true` guard before any signal can be emitted;
- consistency checks for risk and expected-R;
- timeframe integrity checks;
- tests covering canonical, non-canonical, and invalid-input paths.

This is intentionally **not** a Strategy A detector. It is infrastructure that
can host the frozen source-confirmed detector later without allowing research
hypotheses to leak into signal production.

## Gate policy

The source-resolution gate is treated as a bounded blocker, not an infinite
loop. Implementation proceeds in parallel on components whose contracts do not
require unresolved geometry.

No geometry was invented by this change.

## Next implementation track

1. Add replay/data adapters around the existing reproducible XAUUSD dataset.
2. Add outcome accounting and deterministic trade ledger primitives.
3. Add canonical semantic-core detector interfaces for only source-confirmed
   concepts (context/range, breakout/follow-through, directional spike, and
   second-leg relationship where geometry is actually resolved).
4. Keep unresolved P-Gap/entry/SL/TP geometry behind explicit interfaces that
   cannot emit production signals.
5. Wire DEV backtest reporting once a complete source-confirmed execution
   specification exists.
