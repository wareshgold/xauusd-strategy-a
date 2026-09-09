# SP2L Source Geometry Decision Matrix V2 — 2026-09-09

## Critical distinction: strategy geometry vs risk management

SP2L research must keep two questions separate:

1. **Strategy geometry / structural invalidation:** where the source says the setup becomes invalid.
2. **Risk management / position sizing:** how much account capital is risked when that invalidation level is used.

A risk budget such as 1% of equity does **not** determine the structural location of the stop. It determines position size after Entry and stop distance are known.

Conceptually:

`Source setup → Entry + Structural Invalidation → Stop Price → Stop Distance → Position Size from Risk Budget`

The engine must never move a structurally required stop closer merely to satisfy a chosen risk percentage. If the structural stop is farther away, position size becomes smaller. Profitability must never be used to select a stop anchor or buffer.

## Primary evidence

- Authoritative video: Poorsamadi SP2L source video, YouTube `7HEC5mO3d3U`.
- Recovered transcript blob: Git blob `47f867385338738a23b2d06dc48e67b852127243`.
- Direct visual triangulation recorded in `SP2L_VISUAL_GEOMETRY_TRIANGULATION_V3_2026-09-09.md`.

## Core decisions

| Question | Decision | Confidence |
|---|---|---|
| Pending order? | **Pending Limit confirmed** | HIGH |
| Entry identical to Leg-2 start? | **No; keep separate** | HIGH |
| Entry fixed at original/base Spike low? | **Not universally proven** | MED-HIGH |
| Entry latest HL/LH? | **Leading candidate for demonstrated variant; not universal** | HIGH visual / MED-HIGH universal |
| Entry and SL same level? | **Separate** | HIGH |
| Fixed-distance SL from Entry? | **Not source-confirmed; structural invalidation instead** | HIGH |
| Numerical pending-order replacement threshold? | **Unresolved; do not invent** | HIGH |
| Trigger only one candle? | **No; 1/2/3-candle family confirmed** | HIGH |
| Trigger necessarily market entry? | **No; pending Limit model retained** | HIGH |
| 2X exact formula? | **Unresolved** | HIGH concept / LOW formula |
| TP1 preference? | **Source preference for TP1 confirmed; implementation unresolved** | HIGH |
| AB=CD exact four-point formula? | **No; only magnitude relationship is frozen** | HIGH |
| P-Gap generic 3-candle imbalance? | **Rejected as substitution** | HIGH |

## Structural invalidation vs SL implementation

The source clearly establishes an **invalidation condition** distinct from executable Entry. At 39:26 the teacher explains that returning to the invalidation area cancels the scenario. Around 55:02 the visual ordering is explicitly `SL → Enter → leg 2`.

For the deterministic engine:

- `entry_price` = strategy execution variable.
- `invalidation_anchor` = strategy-geometry variable.
- `stop_price` = execution representation of that invalidation only after source-confirmed placement semantics are known.
- `risk_fraction` (e.g. 1%) = risk-management input; it must not infer the invalidation anchor.
- `position_size` = derived from account risk and resulting stop distance.
- Spread/slippage/buffer adjustments, if ever approved, belong to execution/risk policy and must not be silently mixed into source geometry.

**Confirmed:** structural invalidation exists and is distinct from Entry.

**Unresolved:** exact OHLC anchor, wick-vs-body semantics, exact stop buffer/offset, and execution-specific adjustment.

Therefore the research engine must represent stop geometry as an explicit unresolved component rather than hard-code `low - N`, `high + N`, ATR distance, or a risk-derived distance.

## Entry geometry

Strongly supported abstraction:

`Spike → structural correction → relevant structural Low/High → pending Limit`

The visual sequence around 38:40–39:50 shows the pending Buy Limit reference becoming associated with the currently relevant higher-low while the stop remains below the deeper/base structural level. The transcript also permits order update as new candles form.

The phrase “first Low” at 38:38 does not freeze a universal immutable first-low formula because later visual/order-management evidence shows that the actionable reference can evolve with new higher lows. This remains a candidate interpretation, not a production rule.

## Trigger

The source confirms one-, two-, and three-candle constructions, with bar/key-bar confirmation appearing in teaching examples. Exact acceptance taxonomy remains unresolved. Production must not hard-code one classifier yet.

## 2X

2X is a source-confirmed second-position/reward-management concept, but no single numeric implementation is frozen. The source mentions entering the second position at half target and also demonstrates a second position with its own reward profile. These statements are preserved without inventing a universal formula.

## AB=CD

`Leg2Magnitude ≈ Leg1Magnitude` is source-confirmed. Exact A/B/C/D anchors and tolerance are unresolved. Entry must not be assumed to be C; Fibonacci percentages must not be substituted.

## P-Gap

P-Gap is a first-class source concept associated with valid breakout. Multiple source-valid constructions are shown, so a generic three-candle imbalance detector must not be substituted. Exact OHLC boundaries remain unresolved.

## Frozen boundary

### Source semantics that can be frozen

- SP2L = Spike → 2 Leg.
- Spike is directional candle-level structure.
- Breakout and follow-through matter.
- P-Gap is relevant to valid breakout.
- Correction is the entry phase.
- Canonical execution uses a pending Limit.
- Entry and structural invalidation are distinct.
- **Structural invalidation is not a risk-budget calculation.**
- **Risk budget determines position size after Entry and Stop Distance are known.**
- Leg 2 is a separate continuation objective.
- AB=CD expresses Leg-2 magnitude relative to Leg 1.
- TP1/TP2 and 2X are source concepts.
- Trigger exists as a 1/2/3-candle family.

### Still unresolved

- Exact P-Gap OHLC formula.
- Exact relevant Low/High algorithm.
- Exact Entry price anchor.
- Exact SL OHLC anchor.
- Wick vs body semantics.
- Stop buffer/offset, if any.
- Pending-order replacement threshold.
- Exact trigger taxonomy/acceptance criteria.
- Exact 2X formula.
- Exact A/B/C/D points.
- AB=CD tolerance.
- Exact TP1/TP2 formula.
- Canonical session filter.

## Gate decision

**SOURCE RESOLUTION: PARTIAL PASS — materially narrowed.**

**SYNTHETIC FIXTURES: REQUIRED FOR REMAINING GEOMETRY DISCRIMINATION.**

**FROZEN GEOMETRY: BLOCKED.**

**DEV / VAL / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION: LOCKED.**

## Required fixtures

- F8: first relevant Low vs evolving latest HL/LH.
- F9: Entry vs Start-of-Leg-2 with deliberately separated prices.
- F10: structural invalidation vs risk-budget stop; wick vs body and base-vs-relevant opposite swing.
- F11: dynamic pending-order update without an invented replacement threshold.
- F12: 1/2/3-candle trigger variants.
- F13: 2X half-target vs second-position risk/reward interpretations.
- F14: AB=CD competing A/B/C anchors.
- F15: mirrored bearish versions.

## Non-negotiable research rule

If fixtures cannot discriminate a unique source-consistent geometry, the correct outcome is **UNRESOLVED**, not parameter optimization and not a profitability-driven choice.
