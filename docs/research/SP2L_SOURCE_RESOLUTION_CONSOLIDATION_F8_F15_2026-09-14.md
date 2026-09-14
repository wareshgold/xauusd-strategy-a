# SP2L Source Resolution Consolidation — F8–F15 — 2026-09-14

## Purpose

This document consolidates the completed F8–F15 synthetic source-discrimination pass before any geometry freeze.

The governing rule is source meaning over backtest performance. Synthetic fixtures are used only to discriminate source interpretations; they do not authorize optimization, canonicalization, or production implementation.

## Consolidated adjudication

| Fixture | Source result | What is resolved | What remains unresolved |
|---|---|---|---|
| F8 | SOURCE-DOES-NOT-DISCRIMINATE | Demonstrated bullish example supports a dynamic/relevant higher-low entry reference | Universal relevant-low algorithm; exact anchor and update semantics |
| F9 | SOURCE-DISCRIMINATED | Entry is distinct from the start of Leg 2 | Exact executable entry anchor |
| F10 | SOURCE-DISCRIMINATED semantically; SOURCE-DOES-NOT-DISCRIMINATE at OHLC level | Structural invalidation is distinct from risk-budget stop; source supports Spike-origin/base structural semantics | Exact candle index, OHLC field, wick/body semantics, buffer/offset, execution adjustment |
| F11 | SOURCE-DOES-NOT-DISCRIMINATE | Pending-Limit refresh/replacement is permitted when new structure develops | Deterministic retain/replace threshold and exact update rule |
| F12 | SOURCE-DISCRIMINATED for family existence; BLOCKED for final classifier | One-, two-, and three-candle trigger family exists | Exact executable classifier and overlap/priority rules |
| F13 | SOURCE-DOES-NOT-DISCRIMINATE | Second-position/reward-management concept and TP1 preference are source concepts | Exact 2X meaning, anchor, fraction, sequencing, TP1/TP2 formulas |
| F14 | SOURCE-DOES-NOT-DISCRIMINATE | AB=CD means Leg-2 magnitude approximately relates to Leg-1 magnitude | Exact A/B/C/D candle/OHLC anchors and equality tolerance |
| F15 | BLOCKED | No complete deterministic bearish mirror is source-established | Independent bearish evidence versus mirrored semantics; all executable bearish geometry |

## Source meaning sufficiently narrowed

The following semantics are sufficiently supported to remain stable research constraints:

1. SP2L is a Spike → 2 Leg structure.
2. Breakout/follow-through and a source-recognized P-Gap are relevant to the valid-breakout concept.
3. Correction is an entry phase rather than a generic market-entry replacement.
4. Canonical execution is a Pending Limit model.
5. Entry is distinct from the start of Leg 2.
6. Entry is distinct from structural invalidation.
7. Structural invalidation is distinct from the risk-budget position-sizing calculation.
8. The source demonstrates one-, two-, and three-candle trigger constructions.
9. AB=CD is source-confirmed at the magnitude-relationship level: Leg2Magnitude ≈ Leg1Magnitude.
10. P-Gap is a source concept identified as Pressure Gap; a generic three-candle imbalance formula must not be substituted for it.

These are semantic constraints, not permission to invent executable geometry.

## Remaining geometry blockers

The current blockers to Frozen Geometry are finite and explicit:

1. **P-Gap executable geometry** — exact candle index, OHLC boundaries, equality/overlap semantics, and variant handling.
2. **Entry anchor** — universal algorithm for the relevant Low/High across all source variants.
3. **Structural invalidation / SL boundary** — exact candle/OHLC field, wick versus body, and any source-defined buffer or execution adjustment.
4. **Pending-order refresh** — deterministic retain/replace condition and replacement priority.
5. **Trigger classifier** — exact acceptance taxonomy and overlap priority for the 1/2/3-candle family.
6. **2X / TP1 / TP2** — exact operational meaning and executable target/position-management formulas.
7. **AB=CD anchors** — exact A/B/C/D definitions and equality tolerance.
8. **Bearish mirror** — source evidence sufficient for deterministic bearish execution is not yet established.
9. **Execution semantics still requiring strategy-side confirmation** — exact fill-price interpretation and any strategy-specific stop/target interaction not already fixed by infrastructure semantics.
10. **Session/time filter** — only source-confirmed constraints may become canonical; no inferred session rule is permitted.

## Explicit non-decisions

The following remain prohibited as canonical substitutions unless directly source-confirmed:

- generic three-candle FVG/imbalance arithmetic as P-Gap;
- `Entry = latest swing low/high` as a universal algorithm;
- `Entry = Leg-2 start`;
- risk-distance or ATR-derived stop geometry;
- arbitrary wick/body selection;
- invented stop buffers;
- invented pending-order replacement thresholds;
- `C = Entry` as a universal AB=CD anchor;
- Fibonacci percentages as a replacement for source AB=CD;
- numeric AB=CD tolerance selected by backtest performance;
- sign-flip or geometric mirroring as proof of bearish canonical rules;
- market-entry-on-close-reclaim as a replacement for Pending Limit;
- any backtest-profitability criterion as evidence of source meaning.

## Gate decision

### SOURCE RESOLUTION
**PARTIAL / CONSOLIDATION COMPLETE FOR F8–F15**

The current F8–F15 fixture pass is complete as a source-discrimination pass. It has reduced the search space and explicitly recorded where the source does not uniquely determine executable geometry.

### SYNTHETIC FIXTURES
**ADJUDICATION COMPLETE FOR F8–F15**

No unresolved fixture may be forced to a unique answer by optimization. `SOURCE-DOES-NOT-DISCRIMINATE` and `BLOCKED` are valid research outcomes.

### FROZEN GEOMETRY
**BLOCKED**

No canonical executable P-Gap, Entry, SL/invalidation, refresh, trigger classifier, 2X/TP1/TP2, AB=CD anchor/tolerance, or bearish mirror has been frozen by this pass.

### DEVELOPMENT / VALIDATION / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION
**LOCKED**

The project must not use historical performance to resolve these remaining source questions and must not enter Fresh Holdout until the deterministic strategy specification is source-confirmed and frozen.

## Next research gate

Only source-first work that can materially discriminate one of the remaining blockers should proceed. If additional authoritative evidence still fails to discriminate a blocker, the correct state is `UNRESOLVED`, not parameter optimization.

Before any executable geometry is promoted to `CANONICAL`, Ali must explicitly approve the source interpretation. AI may prepare evidence and reconstruction but may not perform the canonical promotion.

## Traceability

This consolidation is aligned with the F8–F15 fixture definitions and adjudication records, including the separate F10, F11, F12, F13, F14, and F15 research documents. It intentionally contains no engine implementation and no historical-performance selection.