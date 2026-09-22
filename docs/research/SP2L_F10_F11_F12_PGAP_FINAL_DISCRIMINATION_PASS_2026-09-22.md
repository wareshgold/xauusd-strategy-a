# SP2L F10/F11/F12/P-Gap Final Discrimination Pass — 2026-09-22

## Objective

Final source-first discrimination pass across the four geometry blockers using current archived evidence.

## P-Gap

Frozen semantic statement: a valid breakout is associated with the source concept called P-Gap, distinct from a generic/common gap.

Not frozen: candle boundaries, OHLC fields, indexing, strict/equality boundary, minimum size, relationship to Spike/breakout, universal three-candle construction.

Fixture matrix: bullish separated boundaries; bearish mirror; equality/touch; zero-gap/common-gap control; competing index candidates; Spike-linked versus breakout-linked candidate.

Decision: no candidate wins without new primary evidence.

## F10 — Stop / invalidation

Frozen semantic statement: structural invalidation is distinct from the risk-budget stop, and SL is tied to the Spike-origin/base structural area.

Strong candidate, not canonical: author implementation uses BUY low[-4] / SELL high[-4].

Not frozen: wick/body/open/close, buffer/spread, touch versus close invalidation, evaluation timing.

Fixture matrix: origin wick breach; body breach; close-only breach; buffer boundary; later higher-low invalidation versus original/base invalidation.

Decision: implementation cross-confirmation does not close the primary-source gate.

## F11 — Pending order refresh

Frozen semantic statement: Pending Limit is demonstrated; the actionable pending reference can evolve; delete/replace is demonstrated when stop distance changes.

Not frozen: mandatory/optional refresh, changed-distance predicate, replacement price, timeout/expiry, candidate precedence.

Fixture matrix: unchanged distance; materially changed distance; smaller distance; larger distance; multiple eligible levels; no-fill expiry candidate.

Decision: do not promote a numerical refresh threshold or 1–2 candle timeout.

## F12 — Trigger family

Frozen semantic statement: Second-Leg activation is directionally related to the prior candle extreme: bullish reaches/breaches prior low; bearish reaches/breaches prior high.

Strong candidate, not canonical: author implementation uses BUY low[-1] < low[-2] / SELL high[-1] > high[-2].

Not frozen: strict/equality, intrabar/completed candle, broker-side fill price, exact canonical indexing, refresh interaction.

Fixture matrix: strict breach; equality; intrabar-only touch; close-only breach; resting pending order; refreshed order immediately before trigger.

Decision: semantic trigger family is source-supported, but executable comparison/fill semantics remain unresolved.

## Cross-gate result

No one of the four areas can be promoted to executable canonical geometry without importing an unresolved implementation assumption.

- P-Gap: semantic only.
- F10: origin-candle structural concept.
- F11: Pending Limit plus evolving reference.
- F12: directional prior-candle trigger family.

The discrimination fixtures are regression/specification infrastructure, not optimization experiments.

No historical win rate, parameter sweep, or backtest result is used to select a candidate.

## Gate

| Area | Semantic status | Executable status |
|---|---|---|
| P-Gap | SOURCE-CONFIRMED | UNRESOLVED |
| F10 | SOURCE-CONFIRMED | UNRESOLVED |
| F11 | SOURCE-CONFIRMED | UNRESOLVED |
| F12 | SOURCE-CONFIRMED | UNRESOLVED |

**Frozen Geometry: BLOCKED**

**Untouched Validation: LOCKED**

**Fresh Holdout: LOCKED**

**Production: OFF**

No canonical production code changed.
