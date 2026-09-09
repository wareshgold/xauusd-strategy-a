# SP2L Source Geometry Decision Matrix V2 — 2026-09-09

## Purpose

This document resolves what can and cannot be frozen from the authoritative SP2L video transcript and the already-recorded direct-frame inspection. It is a source-resolution artifact only. No historical performance result is used as evidence of source meaning.

## Primary evidence

- Authoritative video: Poorsamadi SP2L source video, YouTube `7HEC5mO3d3U`.
- Recovered transcript blob: Git blob `47f867385338738a23b2d06dc48e67b852127243`.
- Direct visual triangulation already recorded in `SP2L_VISUAL_GEOMETRY_TRIANGULATION_V3_2026-09-09.md`.

## Decision matrix

| Question | Source evidence | Candidate interpretation | Decision | Confidence |
|---|---|---|---|---|
| Is entry a pending order? | 38:53–39:11 explicitly describes placing a Limit before the next candle; 53:16 explicitly says pending Limit trigger; 54:29 explicitly refers to Buy Limit | Pending Limit vs market-close reclaim | **Pending Limit confirmed** | HIGH |
| Is Entry identical to Leg-2 start? | 53:43 says a later/deeper pullback reaches the start of Leg 2; 55:02 explicitly separates `SL`, `Enter`, and `leg 2` visually | Entry = Leg2Start vs separate structural references | **Do not equate them** | HIGH |
| Is Entry the original/base Spike low? | 38:38 says correction comes below the first Low and an order can be placed there; later frames show Buy Limit reference moving with developing higher-low structure | Fixed first low vs evolving relevant low | **Not universally proven; fixed-first-low is insufficient** | MED-HIGH |
| Is Entry the latest HL/LH? | Direct frames around 38:40–39:50 show Buy Limit moving upward to the currently relevant higher-low; transcript permits order update as new candles form | Dynamic relevant HL/LH | **Leading candidate for the demonstrated variant; not universal** | HIGH visual / MED-HIGH universal |
| Is SL the same level as Entry? | 39:26 says the return to the structural invalidation level cancels the scenario; later frames and 55:02 show separate SL and Entry levels | Same anchor vs separate structural levels | **Separate** | HIGH |
| Is SL a fixed distance from Entry? | 39:26–40:16 frames/transcript describe distance to structural stop and changing order placement as structure changes | Fixed-risk-distance vs structural invalidation | **Structural invalidation; fixed-distance stop not source-confirmed** | HIGH |
| Is pending-order replacement threshold numerical? | 39:48–40:16: teacher may delete/re-place when the new distance is materially different, but uses qualitative language | Fixed percentage/points vs qualitative materiality | **Threshold unresolved; do not invent one** | HIGH |
| Is trigger one candle only? | 53:16 explicitly gives one-, two-, or three-candle construction; 40:42 onward mentions confirmation and bar/key-bar examples | One-candle vs 1/2/3-candle family | **1/2/3-candle trigger family confirmed; exact acceptance rules unresolved** | HIGH |
| Is a trigger necessarily a market entry? | 38:53–39:11 establishes pre-positioned Limit; 53:16 calls the result a pending Limit trigger | Trigger as market execution vs setup/order trigger | **Trigger may activate pending Limit; do not substitute market reclaim** | HIGH |
| Is 2X a fixed geometric projection? | 38:05–38:08 and 41:26–41:53 discuss 2X as a second position with distinct reward; 22:43 describes entering when price reaches half target; 57:14 mentions 2X outcome | Fixed formula vs management concept | **Concept confirmed, exact formula unresolved** | HIGH concept / LOW formula |
| Is TP1 preferred? | 42:26–42:37 explicitly says teacher generally uses TP1; TP2 should be backtested | TP1 vs TP2 priority | **Source preference for TP1 confirmed; exact implementation remains research item** | HIGH |
| Is AB=CD a four-point candle formula? | 36:15–37:08 explicitly names AB=CD and says Leg 2 equals Leg 1; no unique A/B/C/D OHLC labels are supplied | Exact candle anchors vs magnitude relationship | **Magnitude relationship only** | HIGH |
| Is P-Gap a generic three-candle imbalance? | 31:43–32:21 distinguishes P-Gap from E-Gap/Common-Gap; 34:25–35:50 shows multiple source-valid constructions, including breakout-then-gap and low-sequence-then-gap | Generic imbalance vs source-specific P-Gap | **Generic imbalance substitution rejected** | HIGH |

## Entry geometry resolution

### Strongly supported abstraction

`Spike → structural correction → relevant structural Low/High → pending Limit`

The source teaches candle-by-candle structure, higher lows for bullish spikes and lower highs for bearish structures. The visual sequence around 38:40–39:50 shows the pending Buy Limit reference becoming associated with the currently relevant higher-low while the stop remains below the deeper/base structural level. The transcript at 39:48–40:16 also explicitly permits order deletion/replacement when a new candle changes the structural distance materially.

### Why the transcript phrase “first Low” does not freeze a universal first-low formula

At 38:38 the teacher says the correction comes below the “first low” and that the order can be placed there. In isolation this could support a fixed first-low anchor. However, the subsequent visual sequence and order-management explanation show that the actionable reference can evolve as new higher lows form. The safest source-aligned interpretation is therefore that “first low” is a teaching reference to the first relevant structural pullback in that demonstrated sequence, not proof of a universal immutable initial low for every Spike construction.

This remains a **candidate interpretation**, not a production rule.

## Structural invalidation resolution

The source clearly distinguishes the executable Entry from the invalidation. At 39:26 the teacher explains that if price returns to the invalidation area the scenario is invalidated. At 55:02 the visual ordering is explicitly `SL → Enter → Leg 2`. Therefore:

- Entry and SL must be separate state variables.
- SL must be derived from source structural invalidation, not from an arbitrary fixed multiple of risk distance.
- Wick/body selection remains unresolved.
- Any spread/buffer rule remains unresolved.

## Trigger resolution

The source confirms a family of candle-level trigger constructions rather than a single universal candle pattern:

- one-candle;
- two-candle;
- three-candle;
- bar/key-bar confirmation can additionally appear in the teaching examples.

The source does not provide a deterministic taxonomy saying exactly which of these is required in every setup. Therefore the production engine must not yet hard-code a single trigger classifier.

## 2X resolution

The source establishes 2X as a second-position / reward-management concept. It is not safe to reduce it to one universal formula from the transcript. Two pieces of source language coexist:

1. 22:43 describes entering the second position when price reaches half of the target.
2. 41:26–41:53 describes a second position with a different reward profile and gives a concrete example where the second position produces 3R relative to its own risk.

These are sufficient to preserve 2X as a source concept, but not sufficient to freeze one numeric implementation across all setups.

## A/B/C/D resolution

The source explicitly says AB=CD / 2Leg and expects Leg 2 to be approximately equal in magnitude to Leg 1. It does not explicitly label four unique candle OHLC points as A, B, C and D. Therefore:

- `Leg2Magnitude ≈ Leg1Magnitude` is source-confirmed.
- A/B/C/D exact anchors are unresolved.
- Entry must not be assumed to be C.
- No Fibonacci percentage may be substituted.
- No numerical tolerance may be invented.

## P-Gap resolution

P-Gap is a first-class source concept and is explicitly associated with valid breakout. The source shows more than one valid structural ordering: breakout followed by follow-through and P-Gap, or higher lows followed by P-Gap. Because these constructions are treated as conceptually equivalent in the source, a single generic three-candle imbalance detector would misrepresent the source. Exact OHLC boundaries remain unresolved.

## Frozen boundary after this matrix

### Can be frozen as source semantics

- SP2L = Spike → 2 Leg.
- Spike is a directional candle-level structure.
- Breakout and follow-through matter.
- P-Gap is relevant to valid breakout.
- Correction is the entry phase.
- Canonical execution uses a pending Limit.
- Entry and structural invalidation are distinct.
- Leg 2 is a separate continuation objective.
- AB=CD expresses Leg-2 magnitude relative to Leg 1.
- TP1/TP2 and 2X are source concepts.
- Trigger exists as a 1/2/3-candle family.

### Must remain unresolved

- Exact P-Gap OHLC formula.
- Exact relevant Low/High algorithm across all Spike variants.
- Exact Entry price anchor.
- Exact SL OHLC anchor.
- Wick vs body semantics.
- Pending-order replacement threshold.
- Exact trigger taxonomy/acceptance criteria.
- Exact 2X formula.
- Exact A/B/C/D points.
- AB=CD tolerance.
- Exact TP1/TP2 formula.
- Canonical session filter.

## Gate decision

**SOURCE RESOLUTION: PARTIAL PASS — materially narrowed.**

**SYNTHETIC FIXTURES: REQUIRED FOR DISCRIMINATION OF REMAINING GEOMETRY.**

**FROZEN GEOMETRY: BLOCKED.**

**DEV / VAL / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION: LOCKED.**

## Required next fixtures

- F8: First relevant Low vs evolving latest HL/LH.
- F9: Entry vs Start-of-Leg-2 with deliberately separated prices.
- F10: Structural SL wick vs body and base-vs-relevant opposite swing.
- F11: Dynamic pending-order update with no invented replacement threshold.
- F12: 1/2/3-candle trigger variants producing distinct candidate states.
- F13: 2X half-target interpretation vs second-position risk/reward interpretation.
- F14: AB=CD competing A/B/C anchor constructions.
- F15: Mirrored bearish versions of all structural fixtures.

## Non-negotiable research rule

If the next fixtures cannot discriminate a unique source-consistent geometry, the correct outcome is **UNRESOLVED**, not parameter optimization and not a profitability-driven choice.
