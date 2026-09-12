# SP2L G238 — P-Gap Synthetic Fixture Specification

**Date:** 2026-09-10  
**Gate:** SYNTHETIC FIXTURES / SOURCE RESOLUTION  
**Status:** `PASS_RESEARCH_SPEC_ONLY__FROZEN_GEOMETRY_BLOCKED`

## Objective

Convert the source-resolution uncertainty recorded in G234/G236/G237 into a deterministic synthetic-fixture matrix that can distinguish competing P-Gap interpretations without using historical performance to select the source meaning.

This document defines tests for candidate interpretations only. It does **not** promote any candidate into the canonical Strategy A production specification.

## Source anchor

The strongest current source-correlated candidate is the bullish three-candle endpoint relation:

`High[t-2] < Low[t]`

with the intervening candle corresponding to the directional/spike candle in the illustrated SP2L construction.

The source evidence remains insufficient to freeze wick/body semantics, equality treatment, minimum distance, or additional breakout/spike requirements.

## Fixture dimensions

Every fixture must make the relevant OHLC values explicit and must test exactly one disputed semantic dimension wherever possible.

### F1 — Strict full-extrema separation

Purpose: test the leading source-correlated hypothesis.

Input condition:

`High[t-2] < Low[t]`

Expected under H1: **P-Gap candidate = true**.

The intervening candle is directional/spike-like, but no additional condition is assumed by this fixture.

### F2 — Body-only separation with overlapping wicks

Purpose: distinguish full-extrema semantics from body-only semantics.

Construct candles such that:

- earlier candle body top < later candle body bottom;
- earlier wick reaches into the later candle's body/wick region;
- therefore full-extrema relation fails while body-only separation passes.

Expected:

- H1/full-extrema: **false**;
- body-only hypothesis: **true**.

No production conclusion may be drawn from the result.

### F3 — Exact-touch / equality

Purpose: resolve strict inequality versus equality/touch.

Construct:

`High[t-2] = Low[t]`

Expected outcomes must remain hypothesis-labelled:

- strict-gap H1: **false**;
- inclusive/touch hypothesis: **true**.

No tolerance may be introduced.

### F4 — Generic gap without breakout context

Purpose: determine whether a geometric gap alone is sufficient under each candidate.

Construct a valid positive separation while deliberately omitting any source-described breakout-context condition.

Expected:

- generic-gap hypothesis: **true**;
- breakout-context-required hypothesis: **false**.

This fixture prevents accidental promotion of the Gap-course Breakout Gap definition into SP2L P-Gap.

### F5 — Gap with source-described Breakout Gap context

Purpose: provide the positive control for a stricter breakout-context interpretation.

Construct a valid geometric gap and the source-described beginning-of-move / prior-high close context.

Expected:

- generic-gap hypothesis: **true**;
- breakout-context-required hypothesis: **true**.

This fixture does not establish that SP2L requires Breakout Gap semantics.

### F6 — Directional move without qualifying gap

Purpose: encode the source negative example reviewed in G235/G236.

Construct a clear directional/spike-like move where the candidate endpoint relation is not satisfied.

Expected:

- H1/full-extrema: **false**;
- body-only hypothesis: **false** unless the constructed bodies are explicitly separated;
- any hypothesis requiring a qualifying gap: **false**.

This is the primary negative control.

### F7 — Gap plus weak/non-spike intervening candle

Purpose: test whether the intervening candle itself is a required SP2L-specific spike condition.

Construct a valid endpoint separation but make the intervening candle deliberately non-directional/non-spike-like.

Expected:

- generic-gap hypothesis: **true**;
- gap-plus-spike hypothesis: **false**.

This distinguishes geometry from any future source-confirmed SP2L-specific condition.

### F8 — Gap plus clear spike/breakout sequence

Purpose: positive control for a potential SP2L-specific stricter interpretation.

Construct the same valid endpoint separation as F7 but with a clear directional intervening candle and source-compatible breakout context.

Expected:

- generic-gap hypothesis: **true**;
- gap-plus-spike hypothesis: **true**;
- gap-plus-breakout hypothesis: **true**.

## Required bearish mirror set

Each fixture F1–F8 must eventually have a bearish mirror. The bearish mirror must be expressed explicitly rather than inferred in implementation from a sign flip until source geometry is confirmed.

The likely geometric mirror is intentionally recorded only as a candidate. Do not freeze a formula such as `Low[t-2] > High[t]` without source confirmation.

## Fixture output contract

Each test result must report:

- fixture identifier;
- hypothesis identifier;
- input OHLC;
- expected boolean result;
- actual boolean result;
- PASS/FAIL;
- provenance/source note;
- whether the result is eligible for canonical promotion.

A fixture may PASS while the associated hypothesis remains **non-canonical**.

## Forbidden shortcuts

The fixture suite must not:

- choose the hypothesis with the best historical PnL;
- introduce an empirical minimum gap threshold;
- introduce an empirical AB=CD tolerance;
- map P-Gap to FVG, liquidity sweep, BOS/MSS, displacement, or retest terminology without source evidence;
- assume fill price, entry anchor, stop, or target from P-Gap geometry;
- silently use broker/feed-specific OHLC construction to resolve source semantics.

## Gate decision

**Synthetic Fixture Specification:** PASS.

**Source Resolution:** still OPEN/BLOCKED for final P-Gap geometry.

**Frozen Geometry:** BLOCKED.

**Historical DEV/VAL:** not authorized to select among source hypotheses.

**Fresh Holdout:** remains protected and untouched.

**Production:** not authorized.

## Next decision point

The fixture matrix is now sufficient to prevent implementation drift while source investigation continues. The next source-resolution task should seek an independent SP2L construction where the endpoint marks and candle wicks are simultaneously legible. If no stronger source evidence is found, the project should preserve H1 as the leading hypothesis and explicitly record the unresolved dimensions rather than manufacturing a freeze decision.
