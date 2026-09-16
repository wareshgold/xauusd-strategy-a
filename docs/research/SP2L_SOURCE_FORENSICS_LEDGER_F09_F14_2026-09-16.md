# SP2L Source Forensics Ledger — F09–F14 — 2026-09-16

## Purpose

Record the source-primary transcript forensics pass against the six geometry fields from Batch 6. This ledger separates direct source evidence from unresolved implementation semantics and does not promote unresolved geometry to production.

## Primary source recovered

Authoritative transcript blob:

`47f867385338738a23b2d06dc48e67b852127243`

The transcript is the SP2L training-video source and contains the previously referenced timestamps directly. This corrects the earlier search-state note that the raw transcript was not exposed: the raw source is present as a Git blob and is now directly inspected.

## F09 — Entry anchor vs Leg-2 start

**Status: PARTIALLY DISCRIMINATED — exact executable anchor still unresolved.**

Direct transcript evidence:

- 36:59–37:08: after Spike, correction is expected and Leg 2 is expected to equal Leg 1.
- 38:18: the demonstrated trend is a chain of higher lows.
- 38:38: when the next candle begins correction by moving below the first low, an order can be placed manually or as a predefined Limit.
- 39:11: the Buy Limit can be placed inside the initial three-candle structure without waiting for another candle.
- 39:26: the referenced level is also the level whose return invalidates the scenario.
- 40:07: if the newly formed structure leaves a materially smaller distance, the teacher says the order can be moved upward; if the distance is not large, he keeps the order and pulls it upward. This is execution evidence for an evolving structural reference.

Existing visual triangulation at 38:40–39:50 shows the pending Buy Limit moving to the most recent completed higher-low while SL remains below the deeper/base structural low.

Safe research abstraction:

`Spike → evolving higher-low structure → relevant structural low → pending Limit → correction`

Not yet safe to freeze:

`Entry = universal latest swing low`

or any universal mapping of Entry to the Leg-2 origin. The transcript does not uniquely define the candle/OHLC semantics of the "first low" and later evolving low.

## F10 — Stop-loss anchor / invalidation

**Status: PARTIALLY DISCRIMINATED — structural invalidation confirmed; exact OHLC anchor unresolved.**

Direct transcript evidence at 39:26 says that if price returns to the referenced invalidation area, the scenario is cancelled. At 41:18 the activated position is described with an SL. Existing visual evidence separately shows Entry and SL levels, and the broader source decision matrix records `SL → Enter → Leg 2` ordering in the demonstrated sequence.

Therefore:

- structural invalidation is distinct from risk budget;
- Entry and invalidation are distinct levels;
- no risk-derived stop distance may replace structural invalidation.

Still unresolved: exact wick/body/pivot OHLC anchor, buffer/offset, and execution-specific treatment.

## F11 — Pending Limit refresh

**Status: SOURCE-CONFIRMED BEHAVIOR / MANDATORY CONDITION UNRESOLVED.**

Direct transcript evidence:

- 39:48: after another candle forms, the existing order can be deleted and a new order placed according to the changed distance to SL.
- 40:07: the teacher explicitly contrasts a large distance, where a new order is placed with new sizing, against a small distance, where the existing order is retained and moved upward.

This materially strengthens F11. The source establishes a conditional refresh decision, but does not provide a deterministic numerical threshold for "large enough" versus "not large enough". Therefore no numeric replacement threshold is introduced.

## F12 — Trigger family / precedence

**Status: PARTIALLY DISCRIMINATED.**

Direct transcript evidence:

- 33:37–33:51: the strategy treats the relevant trend structure in three-candle and follow-through/key-bar constructions; it is not a universal four-candle requirement.
- 40:42: a signal/entry confirmation variant is described.
- 40:57–41:03: both bar and key-bar confirmation variants are explicitly mentioned.
- 53:16: the source again explicitly says one-candle, two-candle, and three-candle structures can produce the Limit trigger.

Therefore the fixed-three-candle trigger assumption is rejected. The remaining unresolved field is the deterministic classifier/precedence/acceptance rule among the source-described trigger family.

## F13 — 2X execution semantics

**Status: SOURCE-CONFIRMED CONCEPT / PARTIALLY DISCRIMINATED FORMULA.**

Direct transcript evidence:

- 22:43: the teacher explicitly says that when price reaches half of the target, he enters the additional short position.
- 38:05: the first pullback entry is followed by a later 2X entry.
- 41:26: 2X is an optional second position.
- 41:37–41:53: the teacher gives a worked reward comparison: the primary position is described as 1R to its target, while the later 2X position can produce 3R over its own entry-to-target distance; with equal nominal dollar risk, the example is described as $100 on the first and $300 on the second.
- 57:14: a later example describes 2X together with a 4% gain versus 2% risk.

This is stronger than concept-only evidence. The source confirms that 2X is a later optional position associated with approximately half-target placement in the demonstrated sequence and gives an explicit reward example. However, it still does not uniquely define a universal price equation, sizing rule, stop rule, or whether "half target" is measured from Entry, structural anchor, or another source-defined point.

Canonical action: keep formula unresolved; preserve the source example as a discrimination fixture.

## F14 — AB=CD anchors and tolerance

**Status: CONCEPT CONFIRMED / ANCHORS AND TOLERANCE UNRESOLVED.**

Direct transcript evidence:

- 36:15: SPIKE-2LEG is explicitly linked to the 2Leg / AB=CD concept.
- 36:31–36:46: the speaker contrasts generic internet-style A/B/C/Fibonacci treatment with working at candle level.
- 36:59–37:08: after Spike and correction, Leg 2 is expected to equal Leg 1 and the target is at completion of Leg 2.
- 37:57: the same Leg-1/Leg-2 equal-size expectation is repeated.
- 1:02:41–1:03:19: a later worked example explicitly identifies a Leg 1, then a Leg 2, and discusses an embedded 2Leg inside the larger leg structure.

This confirms the magnitude relationship and the hierarchical nature of the demonstrated legs. It does not uniquely label A/B/C/D as specific candle wicks, bodies, pivots, or entry price, and gives no numeric tolerance.

Safe research representation:

`Leg2Magnitude ≈ Leg1Magnitude`

Unsafe without further source evidence:

`A/B/C/D = assumed swing/entry points`, fixed Fibonacci projection, or invented equality tolerance.

## Cross-field findings

1. **Entry is a pending Limit concept, not an obligatory market-close entry.**
2. **The demonstrated bullish sequence uses evolving structural lows; visual evidence favors the current/relevant higher-low as the pending reference.**
3. **Structural invalidation is separate from risk management.**
4. **Pending-order refresh is explicitly discussed, with a qualitative distance-based decision but no numeric threshold.**
5. **Trigger is a family (1/2/3 candle plus bar/key-bar variants), not a frozen single candle classifier.**
6. **2X has a direct half-target example and worked R comparison, but no universal executable equation.**
7. **AB=CD is explicitly the Leg-2 magnitude relationship, but exact anchors/tolerance remain open.**

## Canonical gate decision

| Field | Updated source status | Canonical action |
|---|---|---|
| F09 Entry anchor | Partial; dynamic/relevant structural low strongly supported in demonstrated bullish variant | **DO NOT FREEZE UNIVERSALLY** |
| F10 SL | Structural invalidation confirmed; exact OHLC unresolved | **DO NOT FREEZE EXACT ANCHOR** |
| F11 Refresh | Conditional refresh confirmed; threshold qualitative | **DO NOT INVENT THRESHOLD** |
| F12 Trigger | 1/2/3 + bar/key-bar family confirmed | **DO NOT FREEZE CLASSIFIER/PRECEDENCE** |
| F13 2X | Half-target example + worked R comparison confirmed | **DO NOT FREEZE UNIVERSAL FORMULA** |
| F14 AB=CD | Leg2 ≈ Leg1 confirmed | **DO NOT FREEZE A/B/C/D OR TOLERANCE** |

## Required next discrimination

1. Use the exact transcript timestamps above to map visual chart coordinates from the authoritative source video.
2. F09/F10: determine whether the visible Buy Limit and SL can be tied to named candle OHLC elements consistently across the worked examples.
3. F11: search later examples for any explicit numerical or structural rule distinguishing "keep/move" from "replace/new sizing".
4. F13: reconstruct the 22:43 and 41:37–41:53 examples from source visuals and determine exactly what the half-target reference is measured from.
5. F14: inspect the 36:15–37:08 and 1:02:41–1:03:19 visuals for explicit A/B/C/D labels or measurable endpoints.
6. F12/F15: map every explicit trigger variant to a worked setup and test whether a precedence rule is stated.

## Gate

Source Resolution: 🟡 PARTIAL — materially strengthened.

Synthetic Fixtures: 🟢 ADVANCED.

Frozen Geometry: 🔴 BLOCKED until exact canonical geometry is uniquely source-discriminated.

Untouched Validation: 🔒 LOCKED.

Robustness/Stability: 🔒 LOCKED.

Fresh Holdout: 🔒 LOCKED.

Production: 🔴 OFF.

## Non-negotiables

- No invented P-Gap formula.
- No invented AB=CD anchors or tolerance.
- No invented 2X formula.
- No invented fill semantics.
- No invented stop buffer.
- No invented refresh threshold.
- No profitability-based geometry selection.
- No production BUY/SELL logic.
