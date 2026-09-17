# SP2L Batch 35 — Official Source P-Gap / 2X Resolution — 2026-09-17

## Purpose

Resolve whether the author-associated SP2L source page exposes stronger source-level semantics for P-Gap, the second-leg trigger, entry, SL, and 2X than the prior forensic batches. Source meaning remains controlling; no implementation rule is promoted from secondary material or from backtest behavior.

## Source inspected

Author-associated SP2L page by Mohammad Ali Poursamadi:
`https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/`

The page is currently indexed by search, while direct page retrieval returned HTTP 403 during this pass. The indexed result contains the relevant source text and is treated as author-associated source evidence, with the retrieval limitation recorded here.

## Findings

### P-Gap / valid Spike

The source states that an important feature of a valid SP2L spike is the presence of a price gap (P-Gap) between the candles, and that a sharp movement without a gap is not considered valid in the strategy.

Resolution impact:

- F12: P-Gap as a validity condition is source-confirmed at concept level.
- P-Gap is not numerically specified by this page.
- No exact candle indexing, wick/body/OHLC selection, minimum gap size, epsilon/tolerance, or mirror construction is exposed.
- The prior related-source candidate construction must remain non-canonical.

Therefore: **P-Gap concept confirmed; exact SP2L P-Gap formula remains unresolved.**

### Second-leg trigger

The source states:

- Uptrend: wait for the corrective candle to reach the low of the previous candle.
- Downtrend: wait for the corrective candle to reach the high of the previous candle.
- Once the Second Leg is triggered, entry is taken in the direction of the spike.

Resolution impact:

- F9/F12 are strengthened at the trigger-concept level.
- Directional mirror is strengthened.
- The wording does not specify intrabar touch versus wick penetration versus close-based activation, nor broker/platform execution semantics.
- It does not define a unique multi-candle indexing algorithm beyond the stated previous-candle reference.

Therefore: **second-leg trigger concept is source-confirmed, but executable activation/fill semantics remain unresolved.**

### Entry / SL

The source states that after the Second Leg is triggered, entry is in the spike direction and SL is placed behind the candle from which the spike originated.

Resolution impact:

- Entry direction is source-confirmed.
- Origin-candle relationship for SL is source-confirmed.
- Exact price boundary remains unresolved: wick extreme, body boundary, candle low/high, buffer, spread handling, or other platform convention is not specified.

Therefore: **entry direction and SL-origin concept confirmed; exact executable price rule remains unresolved.**

### 2X / secondary entry

The source explicitly states that, in addition to the initial entry, a secondary entry can be added at **50% of the distance from the entry point to the stop-loss**, described as improving the average entry price and risk management.

Resolution impact:

- F13 is materially strengthened beyond prior secondary-source evidence.
- The 50%-distance relation is now author-associated source evidence and can be recorded as source-confirmed concept-level geometry.
- Still unresolved: exact meaning of the `2X` label in every chart context, whether the secondary entry is always placed, position sizing, whether 50% is measured from the initial executed entry or another reference, behavior when the initial entry is not filled, and exact order/fill semantics.

Therefore: **50%-of-entry-to-SL secondary-entry relation is source-confirmed; complete 2X execution/lifecycle semantics remain unresolved.**

## Non-promoted rules

This pass does not promote any of the following to canonical geometry:

- numeric P-Gap formula;
- exact P-Gap candle indexing;
- wick/body substitution;
- minimum P-Gap threshold;
- exact fill event (touch/wick/close/next-bar/broker);
- exact SL price boundary;
- automatic versus manual execution;
- 2X position sizing;
- 2X always-on versus conditional use;
- 2X pending-order lifecycle;
- AB=CD A/B/C/D anchors;
- AB=CD tolerance;
- universal Round Level interval.

## Gate impact

**Source Resolution: PARTIAL PASS — materially strengthened.**

**F9:** second-leg trigger concept source-confirmed; exact activation/fill semantics unresolved.

**F10:** origin-candle SL concept source-confirmed; exact price/invalidation semantics unresolved.

**F12:** P-Gap validity and second-leg trigger concept source-confirmed; exact executable taxonomy unresolved.

**F13:** 50%-of-entry-to-SL secondary-entry relation source-confirmed; full 2X execution/lifecycle semantics unresolved.

**F14:** unchanged — AB=CD concept remains source-confirmed; anchors/tolerance unresolved.

**Frozen Geometry: BLOCKED.**

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected and no production BUY/SELL logic was changed.
