# G400 — Geometry Freeze Gate

## Purpose

G400 is a **blocking research gate** between the frozen semantic layer and any future executable geometry freeze.

It does not select, optimize, or promote a geometry hypothesis. It makes the remaining source-critical gaps explicit and mechanically prevents a premature geometry freeze.

## Evidence position

G399 freezes only the semantic layer. The current canonical concepts are SP2L, breakout/follow-through, P-Gap association, correction, pending-limit entry, structural invalidation, second-leg continuation, AB=CD, and TP1/TP2 terminology.

The following remain unresolved and therefore cannot be canonical executable rules:

1. P-Gap OHLC geometry/formula
2. A/B/C anchors and wick/body semantics
3. AB=CD equality tolerance
4. exact pending-limit price/fill semantics
5. entry trigger/persistence/activation/invalidation-before-fill semantics
6. structural stop boundary / executable stop price
7. TP1/TP2 mapping to executable prices

## Gate rule

`READY` is permitted only when every source-critical geometry dimension has authoritative source resolution and has passed the required synthetic discrimination. The current state is **BLOCKED**.

Synthetic fixtures, parameterized hypotheses, or historical performance may discriminate or measure candidates, but they cannot clear a source-evidence blocker.

## Non-promotion rule

G400 explicitly does **not**:

- invent a P-Gap formula;
- choose A/B/C/D anchors;
- define an AB=CD tolerance;
- equate fill price with geometric C;
- define a stop boundary from backtest performance;
- map TP1/TP2 to prices without source evidence.

## Gate outcome

**SOURCE RESOLUTION remains open. FROZEN GEOMETRY is not yet authorized.**

The next research work should target authoritative evidence and discriminating fixtures for the blockers above, not optimization or production implementation.
