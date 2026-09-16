# SP2L Batch 26 — P-Gap Source-Resolution Pass — 2026-09-16

## Purpose

Resolve the **P-Gap** blocker using source-first evidence, without promoting an implementation hypothesis to canonical geometry.

This pass combines:

1. the user-supplied primary SP2L training artifact already forensically inspected;
2. the author-associated SP2L training index;
3. an older Poursamadi price-action course excerpt that explicitly defines `P_GAP` as **Pressure gap**.

The source meaning remains higher priority than any backtest result.

## Evidence A — current primary SP2L artifact

The primary SP2L training video contains an explicit teaching annotation around ~38:00:

> `Valid BO = P-Gap`

This establishes that P-Gap is directly part of the taught SP2L breakout-validation concept.

However, the inspected primary frames do **not** expose a deterministic numeric construction for P-Gap. In particular, the artifact does not yet establish:

- exact candle indexing;
- which OHLC fields define the two gap boundaries;
- whether the gap is wick-to-wick, body-to-body, or another construction;
- whether the gap must be strictly positive or may be zero/toleranced;
- minimum gap size, if any;
- bullish/bearish mirror semantics;
- whether P-Gap is itself the breakout condition or a classification of a valid breakout;
- whether P-Gap must occur inside the Spike, at a specific Spike boundary, or at the breakout level;
- execution timing relative to the P-Gap event.

**Primary-artifact status: concept confirmed; exact formula unresolved.**

## Evidence B — author-associated SP2L training index

The author-associated training index for the 1:09:16 SP2L video explicitly lists a section titled **"مروری بر مفهوم P-Gap"** (review of the P-Gap concept), alongside Spike, 2L, order placement, and 2X. This independently confirms that P-Gap is a named component of the SP2L training material.

It does not expose the formula itself.

## Evidence C — related Poursamadi price-action source

A searchable excerpt from an older Poursamadi price-action course labels:

- `P_GAP` = **Pressure gap**;
- and states, in the gap section, to inspect the distance between the **high of two candles before** and the **low of the current candle**, with a gap existing when a distance is present.

This is materially useful because it supplies a concrete candidate construction that is consistent with the terminology `P_GAP = Pressure gap`.

But it is **not sufficient to freeze SP2L P-Gap geometry** for three reasons:

1. the excerpt is from a broader/older price-action course, not the current SP2L primary training artifact;
2. the excerpt is not a complete SP2L execution specification;
3. the available text does not establish the full bullish/bearish mirror, tolerance, indexing convention, or exact role of the gap inside the SP2L breakout chain.

Therefore this evidence is recorded as a **source-aligned candidate construction**, not a canonical rule.

## Candidate construction ledger

| Candidate | Evidence | Canonical? | Freeze impact |
|---|---|---:|---|
| P-Gap exists when there is a distance between High[2] and Low[0] in the cited price-action context | Related Poursamadi course excerpt | No | Still BLOCKED |
| P-Gap is the validity condition for the SP2L breakout | Current primary SP2L artifact: `Valid BO = P-Gap` | Concept only | Still BLOCKED |
| P-Gap exact OHLC formula / tolerance / mirror | No source-complete evidence yet | No | BLOCKED |

`High[2]` / `Low[0]` notation above is a research normalization of the cited wording, **not a source-defined indexing convention**. It must not be implemented as canonical geometry.

## Falsification boundary

Do **not** introduce any of the following from this pass:

- a numeric P-Gap threshold;
- a body/wick substitution;
- a zero-gap epsilon;
- a minimum-point filter;
- a bullish formula plus an assumed bearish mirror;
- a specific breakout close/touch rule;
- an entry/fill rule derived from P-Gap;
- a production BUY/SELL decision rule.

Backtest performance must not be used to choose among these unresolved interpretations.

## Resolution

**P-Gap: SOURCE-CONFIRMED CONCEPT + RELATED-SOURCE CANDIDATE CONSTRUCTION / EXACT SP2L FORMULA UNRESOLVED.**

This is progress in source resolution, but it is **not** a Frozen Geometry pass.

## Gate impact

- Source Resolution: **PARTIAL PASS — P-Gap evidence strengthened**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

## Sources

- Current author-associated SP2L training index: https://t.me/s/tradingclub13
- Author SP2L strategy page: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/
- Related Poursamadi price-action course excerpt containing `P_GAP: Pressure gap` and the High[2]/Low[0] wording: https://www.scribd.com/document/666358452/%D8%AC%D8%B2%D9%88%D9%87-%DA%A9%D8%A7%D9%85%D9%84-%D8%A7%D8%B3%D8%AA%D8%A7%D8%AF-%D9%85%D8%AD%D9%85%D8%AF%D8%B9%D9%84%DB%8C-%D9%BE%D9%88%D8%B1%D8%B5%D9%85%D8%AF%DB%8C-%D9%88%DB%8C%D8%B1%D8%A7%DB%8C%D8%B4-%D8%B4%D8%AF%D9%87
