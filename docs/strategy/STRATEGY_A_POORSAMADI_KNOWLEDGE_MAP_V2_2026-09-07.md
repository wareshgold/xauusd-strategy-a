# Strategy A — Poorsamadi SP2L Knowledge Map V2

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** AUTHORITATIVE RESEARCH SYNC — source-first, non-production

## Purpose

This file is the current synchronization point for Poorsamadi SP2L research.

It exists to prevent implementation drift and accidental strategy invention.

The rule hierarchy is strict:

1. Raw Poorsamadi source is semantic authority.
2. Source-grounded statements may be marked `SOURCE-ESTABLISHED`.
3. A deterministic interpretation not uniquely specified by the source is `CANDIDATE`.
4. Missing geometry is `TBD`.
5. Historical performance may validate or reject a frozen candidate, but must never be used to decide what Poorsamadi meant.
6. Existing Strategy A code is implementation evidence only; it is not source authority.
7. Fresh Holdout remains locked until a fully frozen candidate survives DEV/VAL.

## Authoritative source set

Primary raw source:

- `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`

Corroborating source/research records:

- `docs/strategy/STRATEGY_A_POORSAMADI_SOURCE_LEDGER.md`
- `docs/research/PHASE_31_SP2L_SOURCE_EXCAVATION_V3.md`
- `docs/research/PHASE_31_SP2L_GEOMETRY_RESOLUTION_PROTOCOL.md`
- `docs/research/PHASE_32_SP2L_V2_SEMANTIC_STATE_AND_FIXTURES.md`
- `docs/research/PHASE_33_SP2L_G1_STRUCTURAL_REFERENCE_RESOLUTION.md`
- `docs/research/PHASE_33_G2_PENDING_LIMIT_RESOLUTION.md`
- `docs/research/PHASE_33_G3_STRUCTURAL_STOP_RESOLUTION.md`
- `docs/research/PHASE_34_SP2L_G4_SOURCE_ANCHOR_2026-09-07.md`
- `docs/research/PHASE_35_SP2L_G5_SOURCE_EVIDENCE_2026-09-07.md`
- `docs/research/PHASE_36_SP2L_G5_CANDIDATE_DISCRIMINATION_MATRIX_2026-09-07.md`
- `docs/research/PHASE_37_SP2L_G5_SOURCE_VISUAL_GATE_2026-09-07.md`

## Source-media recovery checkpoint — 2026-09-07

A fresh public-source audit was performed against the original Pour Samadi Telegram channel and the linked SP2L YouTube recording.

### What was verified

- The original Telegram source channel contains the SP2L recording post.
- The source post identifies a **1:09:16 SP2L recording** and links the YouTube video.
- The same source area also exposes a **1:09:15 720p version**.
- The public Telegram index exposes the lesson sequence and source-media metadata, including the SP2L sections covering spike types, P-GAP, combining 2L with Spike, order placement, 2X, levels/context, entry examples, and initial trades.
- The public web representation confirms the source media exists and is the correct lesson source.

### What was NOT recovered

The public web/Telegram representation did **not** expose the raw video bytes or chart pixels/OHLC coordinates needed to identify the exact visual A/B/C points for G4/G5. The YouTube page likewise did not expose a usable chart transcript/image layer for those coordinates.

Therefore:

- We did **not** pretend to inspect chart pixels that were unavailable.
- We did **not** promote any G4/G5 candidate based on coding convenience or historical performance.
- G4 exact Leg1 endpoints remain `TBD / VISUAL SOURCE REQUIRED`.
- G5 exact Leg2 projection origin remains `TBD / VISUAL SOURCE REQUIRED`.

### Source evidence already recovered from the text

- Around **36:59–37:08**, the source describes spike → correction → Leg2 and the approximate equality of Leg1 and Leg2.
- Around **1:02:41–1:03:32**, the source distinguishes a larger parent leg from nested 2-leg structures and describes the next leg after a deep correction.
- Around **1:04:00–1:04:32**, the teacher visually identifies where a deep leg starts, describes Leg1 as a segment between two chart locations, discusses order placement/activation, and derives TP1 from the Leg1 reference. The transcript does not encode the exact chart coordinates.
- At **37:22**, the user-provided source frame establishes the semantic fact that a level break and a gap can occur in the same transition/event. It does **not** establish a universal numerical gap formula, minimum gap size, wick/body rule, overlap threshold, or candle-count rule.

### Current G5 candidate boundary

The unresolved executable C/origin candidates remain explicitly separated:

1. `STRUCTURAL_HL_LH`
2. `OTHER_VISUAL_POINT`
3. `CORRECTION_EXTREME` only if future source visual evidence explicitly identifies that point

The following are **not canonical geometric C points** merely because they occur in execution:

- `ACTUAL_FILL`
- `PENDING_LIMIT`

The source phrase "Leg2 starts from the deep correction" must not be silently converted into `Leg2Origin = correction.low/high`, and a fill price must not be silently converted into the geometric C point.

### Gate status after media audit

```text
G1  structural reference        candidate / source semantic role confirmed
G2  pending limit               source mechanism confirmed / exact universal mapping candidate
G3  structural stop              source concept confirmed / exact universal level candidate
G4  Leg1 endpoints               SEMANTIC RESOLVED / EXECUTABLE TBD
G5  Leg2 origin                  SEMANTIC RESOLVED / EXECUTABLE TBD
G6  Leg2 equality                BLOCKED by unresolved G4/G5 tolerance
G7  execution semantics          RESEARCH-RESOLVED / dependent on G4/G5
Fresh Holdout                    LOCKED
Production SP2L                  BLOCKED
```

## Canonical semantic lifecycle — source-backed architecture

The currently supported semantic lifecycle is:

```text
CONTEXT / RANGE
  -> STRONG MOVE / BREAKOUT FAMILY
  -> FOLLOW-THROUGH / KEY-BAR BEHAVIOR
  -> SPIKE FAMILY
  -> STRUCTURAL LOW/HIGH SEQUENCE
  -> CORRECTION BEGINS
  -> PENDING LIMIT EXISTS BEFORE FILL
  -> PRICE TOUCH / FILL
  -> PREDEFINED STRUCTURAL INVALIDATION
  -> LEG 2 ATTEMPT IN SPIKE DIRECTION
  -> LEG 2 ~= LEG 1
  -> TP1
```

This lifecycle is architecture, not a complete executable strategy yet.

## Source-established semantic facts

### S1 — Candle-by-candle reading

Poorsamadi repeatedly requires candle-by-candle reasoning, including OHLC relationships, sequence, cycle and candle count. Future information cannot be used to retroactively define an earlier setup state.

**Status:** `SOURCE-ESTABLISHED`.

### S2 — Spike requires context, not merely momentum

The source describes spike/strong movement in relation to prior range/context, breakout/follow-through behavior, structural higher lows/lower highs and pressure-gap variants. Multiple sequence variants can express the same strong-move concept.

**Status:** `SOURCE-ESTABLISHED`; exact universal numeric grammar remains `TBD`.

### S3 — SP2L core relationship

After a spike, the source expects a correction followed by a second directional leg whose magnitude is approximately equal to Leg 1.

```text
abs(Leg2) ~= abs(Leg1)
```

**Status:** core relationship `SOURCE-ESTABLISHED`; endpoints and tolerance `TBD`.

### S4 — Pending-limit entry is canonical in demonstrated SP2L examples

The source allows the order to be placed during the correction and before the correction candle completes. A limit order can exist before fill.

Therefore the source-backed lifecycle is not a mandatory close-reclaim market-entry model.

**Status:** `SOURCE-ESTABLISHED`.

### S5 — Entry risk is known before activation

The demonstrated setup has a known entry-to-stop distance before the pending order activates. Order replacement/cancellation may depend on risk-distance changes, but the universal threshold is not numerically specified.

**Status:** concept `SOURCE-ESTABLISHED`; threshold `TBD`.

### S6 — Structural stop / invalidation

The stop is tied to scenario invalidation and should not be widened discretionarily after adverse movement.

**Status:** concept `SOURCE-ESTABLISHED`; universal exact structural level/buffer `TBD`.

### S7 — TP1 is the base SP2L exit candidate

The source demonstrates TP1 as the practical base target. TP2, Leg3 and 2X are distinct modules and must not be silently merged into the single-position baseline.

**Status:** `SOURCE-ESTABLISHED`.

## P0 geometry synchronization

### G1 — First structural low/high

Source confirms that structural higher lows / lower highs matter and that the first relevant low/high is used in correction/entry reasoning.

Current research candidate:

- Bullish: previous relevant candle low / higher-low reference.
- Bearish: previous relevant candle high / lower-high reference.

This is deterministic research geometry only.

**Status:** semantic role `SOURCE-ESTABLISHED`; universal algorithm `CANDIDATE / NOT SOURCE-CONFIRMED`.

### G2 — Pending-limit price

Source confirms pending-limit placement at a structural correction level in demonstrated examples.

Current research candidate:

- BUY LIMIT = selected bullish HL reference price.
- SELL LIMIT = selected bearish LH reference price.
- Activation = exact price touch/retest.

No tolerance has been invented.

**Status:** pending-limit mechanism `SOURCE-ESTABLISHED`; exact universal level mapping `CANDIDATE`.

### G3 — Structural stop

Source confirms structural invalidation and known risk before fill.

Current research candidate:

- Bullish structural SL candidate = spike-origin low.
- Bearish structural SL candidate = spike-origin high.

No historical buffer optimization is permitted.

**Status:** structural-stop concept `SOURCE-ESTABLISHED`; exact universal level `CANDIDATE`.

### G4 — Leg 1 endpoints

The source confirms Leg 1 and Leg 2 as distinct directional legs and repeatedly points visually from one chart location to another. The raw transcript does not encode those visual coordinates.

At approximately 36:59–37:08, the source confirms correction then Leg 2 equality.

At approximately 1:02:41–1:03:32, the source describes nested legs and a larger parent Leg1/Leg2 relationship.

At approximately 1:04:00–1:04:32, the source explicitly says the deep leg starts "from here" and that Leg 1 is "from here to here", but text alone cannot resolve the exact OHLC endpoints.

Candidate endpoint families remain separated:

1. structural low/high -> spike extreme;
2. breakout level -> spike extreme;
3. spike start -> spike end;
4. relevant candle open -> spike extreme;
5. structural point -> structural point.

**Status:** Leg1 semantic existence `SOURCE-ESTABLISHED`; exact A/B endpoints `TBD / VISUAL SOURCE REQUIRED`.

**Hard guardrail:** do not implement a canonical Leg1 calculator and do not select an endpoint formula by DEV/VAL performance before visual source resolution.

### G5 — Leg 2 projection origin

The source establishes that Leg 2 occurs after a correction and is measured as the next directional leg. The example around 1:03:19 explicitly describes the next leg from the deep correction, but the transcript still does not encode a unique machine-readable OHLC coordinate for the exact C point.

Candidate origins remain separated:

1. correction extreme;
2. actual limit fill;
3. structural reference;
4. source-defined visual chart point.

**Status:** "Leg2 begins after correction" `SOURCE-ESTABLISHED`; exact projection origin `TBD / VISUAL SOURCE REQUIRED`.

**Hard guardrail:** do not promote correction extreme, fill, or structural reference merely because one backtests better.

### G6 — Leg 2 equality

```text
abs(Leg2) ~= abs(Leg1)
```

The equality relationship is source-established, but no universal numerical tolerance is specified in the preserved transcript.

**Status:** relation `SOURCE-ESTABLISHED`; tolerance `TBD`.

No arbitrary ±5%, ±10%, ±20% band may be presented as Poorsamadi's rule.

### G7 — Execution semantics

The source establishes pending order, fill, predefined stop and target behavior, but historical OHLC simulation still requires explicit deterministic policy for:

- limit touch/fill;
- stop touch;
- TP touch;
- same-candle entry + SL;
- same-candle entry + TP;
- spread/slippage;
- order creation and fill within the same candle.

These are simulator policies, not teacher semantics unless directly source-supported.

**Status:** lifecycle concepts `SOURCE-ESTABLISHED`; simulator ordering policy `TBD / RESEARCH POLICY`.

## Known conflict with current production Strategy A

The current Strategy A close-reclaim entry implementation is not proven canonical SP2L and must not be used as source authority.

Likewise, current production LegProjection endpoint choices must not be treated as Poorsamadi geometry.

Production Strategy A remains untouched while SP2L V2 research is unresolved.

## What is currently safe to implement in research-only code

Safe:

- semantic state machine;
- explicit context -> impulse -> FT -> spike -> correction -> pending -> fill lifecycle;
- explicit TBD/candidate fields;
- deterministic synthetic fixtures for already frozen candidate definitions;
- rejection of close-reclaim as the only canonical entry mechanism;
- separate 2X module boundary;
- provenance/audit records for source-media recovery attempts;
- side-by-side measurement of explicitly supplied A/B/C candidates without selecting a canonical candidate.

Not safe yet:

- canonical Leg1 endpoint calculator;
- canonical Leg2 projection origin;
- fitted Leg2 equality tolerance;
- guessed P-GAP geometry;
- guessed order-replacement threshold;
- Fresh Holdout evaluation of unfrozen semantics;
- production/live BUY/SELL wiring from SP2L V2.

## Required next evidence

Highest-value evidence remains the actual chart visual source for:

- 36:59–37:22;
- 1:02:41–1:03:32;
- 1:04:00–1:04:32.

The public source audit confirmed the media exists but did not expose the chart pixels/OHLC coordinates through the accessible web representation.

Until those coordinates are source-resolved, G4 and G5 stay `TBD`.

## Research progression gate

```text
SOURCE RESOLUTION
  -> deterministic synthetic fixtures
  -> frozen candidate geometry
  -> chronological DEV
  -> untouched VAL
  -> robustness / stability checks
  -> only then Fresh Holdout
  -> only after validation consider production/live signal integration
```

## Non-negotiable anti-invention rules

- Never use historical PnL to infer what Poorsamadi meant.
- Never silently convert a candidate into a source fact.
- Never use future candles to define an earlier state.
- Never optimize against VAL/Fresh.
- Never unlock Fresh Holdout while core geometry remains unfrozen.
- Never let AI arbitrarily generate BUY/SELL decisions.
- Keep production Strategy A unchanged until SP2L V2 is semantically and statistically validated.

## Current decision

**SYNC COMPLETE THROUGH G5 SOURCE + MEDIA AUDIT.**

We are aligned with the preserved Poorsamadi source as far as the accessible source text/media metadata allows.

The original source media was located and verified, but its public representation did not expose the chart pixels needed to freeze the exact G4/G5 geometry. Therefore we deliberately preserve the unresolved boundary instead of guessing.

G4 Leg1 exact endpoints and G5 exact projection origin remain intentionally unresolved.

The correct next action is source/visual resolution, not strategy optimization.
