# Strategy A — Poorsamadi SP2L Geometry Research v1

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-geometry`  
**Status:** Research/codification only — no production Strategy A changes

## Objective

Resolve the geometric meaning of the SP2L sequence before touching production code.

Target sequence:

`SPIKE → FIRST STRUCTURAL LOW/HIGH → CORRECTION → PENDING LIMIT → FILL → STRUCTURAL SL → LEG1 → LEG2≈LEG1 → TP1`

The source explicitly describes a pending/limit order when correction begins, a structural level around the first low/high, a known stop distance, and a second leg expected to match the first leg. The source does **not** yet provide enough information to silently choose all numerical endpoints.

## 1. First structural low/high

### Source evidence

The bullish examples describe successive higher lows (`L, L, L`) as the recognizable strong movement. When the next candle begins correcting and moves below the first low, that first low becomes the important reference for the pending order. The bearish case is symmetric.

### Current semantic interpretation

For bullish SP2L:

`L1 < L2 < L3 ...`

where `L1` is the first structural low belonging to the recognized spike sequence.

For bearish:

`H1 > H2 > H3 ...`

where `H1` is the first structural high.

### Still unresolved

- exact swing/structural-low algorithm;
- whether a low is defined by one candle or a local multi-candle pivot;
- minimum number of structural points;
- whether the first structural point must occur after breakout/FT;
- exact relationship between P-GAP and the first structural point.

**Status: SOURCE-STRONG CONCEPT / ALGORITHM TBD.**

## 2. Correction start

The source describes correction as the next movement beginning to go below the first bullish low (or above the corresponding bearish high). This is the event that permits a limit order to be prepared.

Important distinction:

`correction begins` ≠ `entry is filled`

The order can exist before the market reaches the limit price.

**Status: SOURCE-STRONG.**

## 3. Pending limit entry

### Source evidence

The source explicitly says that once the next candle starts correcting below the first low, an order can be manually or by limit order placed in advance. The examples also describe placing the limit around the structural level and knowing the stop distance before activation.

### Consequence for current implementation

The current Strategy A implementation that waits for a completed candle to close back beyond the correction extreme is not source-canonical. It is an implementation assumption.

### Deterministic target to resolve

For bullish:

`LIMIT_ENTRY = source-defined structural retracement level around L1`

For bearish:

`LIMIT_ENTRY = source-defined structural retracement level around H1`

The exact price relation remains TBD. It must not be guessed from the current close-reclaim implementation.

**Status: SOURCE-ESTABLISHED EVENT / EXACT PRICE TBD.**

## 4. Structural stop

The source states that the limit entry gives a known distance to the stop and repeatedly shows the stop around the structural reference.

Likely semantic relationship:

Bullish:
`SL < structural entry/reference`

Bearish:
`SL > structural entry/reference`

But the exact offset, whether SL is exactly at the first low/high, and whether any buffer is used are not established numerically.

**Status: SOURCE-STRONG / EXACT STOP GEOMETRY TBD.**

## 5. Intrabar execution semantics

The source's wording is price-level/order based rather than candle-close based: a limit order can be waiting and becomes active when price reaches it.

Therefore a future implementation should distinguish:

1. order creation;
2. limit touch/fill;
3. stop touch;
4. target touch.

This is materially different from a close-only execution model.

### Same-candle ambiguity

If a candle can both touch entry and later touch SL/TP, OHLC alone may not establish the exact sequence. A conservative deterministic policy must be defined before backtesting the geometry.

**Status: EXECUTION POLICY TBD.**

## 6. Leg1 endpoints

### Source-established concept

The source defines SP2L around a first directional leg and expects a correction followed by a second leg of approximately equal magnitude.

### What cannot yet be claimed

The current code defines Leg1 using:

`first.open → last.close`

This is not established by the source.

Possible candidate endpoint models include:

- first structural low/high → spike extreme;
- spike start → spike end;
- first relevant candle open → spike extreme;
- structural-point-to-structural-point.

These are **research candidates only**.

### Research requirement

Every candidate must be evaluated against source examples and then tested chronologically. Do not choose the endpoint because it produces the best backtest.

**Status: CORE CONCEPT SOURCE-ESTABLISHED / ENDPOINTS TBD.**

## 7. Leg2 projection origin

The source expects Leg2 to begin after correction and reach a magnitude comparable to Leg1. The transcript does not give a sufficiently explicit universal formula for whether projection starts from:

- correction extreme;
- actual limit-entry price;
- fill price;
- another structural point.

Current code projects from correction extreme. This is therefore an implementation assumption until source evidence resolves it.

**Status: TBD.**

## 8. Leg2 equality

Semantic rule:

`abs(Leg2) ≈ abs(Leg1)`

The equality tolerance is not provided.

Do not introduce a percentage such as ±10% or ±20% merely because it is common in AB=CD implementations. Any tolerance must either be source-supported or explicitly introduced as a research hypothesis and frozen before OOS testing.

**Status: SOURCE-ESTABLISHED CONCEPT / TOLERANCE TBD.**

## 9. TP1

The source repeatedly frames TP1 as the practical primary target. TP2 exists, but the material describes TP1 as the normal/base target and warns against unnecessarily extending targets.

Therefore the current research model should preserve:

`TP1 = Leg2 completion target`

while keeping TP2/Leg3/2X as separate research modules rather than silently mixing them into the base signal.

**Status: SOURCE-STRONG.**

## 10. Order replacement / risk filter

The source describes deleting/replacing a pending order if later price development makes the stop distance too large, then potentially placing a new order.

The concept is source-established, but the numerical maximum acceptable risk/stop distance is not given.

This should become a separate risk-engine rule, not part of the geometric definition until quantified.

**Status: SOURCE-ESTABLISHED BEHAVIOR / THRESHOLD TBD.**

## 11. What is now resolved

- P-GAP and exhaustion gap are distinct.
- P-GAP belongs to pressure/strong-movement context, not as a standalone signal.
- spike can be represented by multiple source-described strong-movement variants.
- higher-low/lower-high structure is a valid semantic representation of strong movement.
- the first structural low/high is a key correction/entry reference.
- correction begins before fill.
- entry is semantically a pending limit rather than a mandatory close-reclaim.
- stop distance is known before fill.
- Leg2 is expected to approximate Leg1.
- TP1 is the practical base target.

## 12. What remains open

### P0 — must resolve before production codification

1. Exact first structural low/high algorithm.
2. Exact limit-entry price.
3. Exact structural SL price.
4. Exact Leg1 endpoints.
5. Exact Leg2 projection origin.
6. Intrabar fill/SL/TP and same-candle ordering policy.

### P1 — can follow immediately after P0

7. Leg2 equality tolerance.
8. Order replacement/risk-distance threshold.
9. Exact P-GAP geometry.
10. Exact range definition.
11. Exact breakout level algorithm.
12. Exact FT no-return/non-overlap predicate.

## 13. Work estimate

This geometry pass reduces the remaining work substantially, but the system is **not yet ready for production Strategy A modification**.

Current roadmap estimate:

- Geometry semantic resolution: **~1 major pass remaining** after obtaining/locating the relevant source examples.
- Deterministic codification specification: **~1 pass**.
- Research implementation + historical fixtures: **~1–2 passes**.
- DEV/VAL validation and robustness checks: **several research runs**.
- Fresh holdout replication: **only after the hypothesis survives DEV/VAL**.
- Production implementation: **last stage, after validation**.

This is a research estimate, not a promise of a fixed number of commits.

## 14. Guardrail

No current production detector is being rewritten from this document.

The purpose is to identify exactly where source meaning is strong enough to codify and where additional source evidence or research is required.

## 15. Source anchors

The strongest geometry evidence currently available is around the source discussion of:

- breakout + FT + P-GAP variants;
- Leg1/Leg2 expectation;
- first higher-low / first-low correction;
- pending limit order;
- known stop distance;
- TP1 and practical target selection.

The raw source remains authoritative. Existing code remains implementation evidence, not teacher-intent evidence.
