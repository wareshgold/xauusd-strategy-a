# SP2L Batch 26 — P-Gap Source-Resolution Pass — 2026-09-16

## Purpose

Resolve the **P-Gap** blocker using source-first evidence, without promoting an implementation hypothesis to canonical geometry.

This pass combines:

1. the user-supplied primary SP2L training artifact already forensically inspected;
2. the author-associated SP2L training index;
3. an older Poursamadi price-action course excerpt that labels `P_GAP` as **Pressure gap** and separately describes a generic gap-detection relationship.

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

A searchable excerpt from an older Poursamadi price-action course provides two separate pieces of evidence:

- its glossary labels `P_GAP` as **Pressure gap**;
- in the broader gap section, it says to inspect the distance between the **high of two candles before** and the **low of the current candle**, with a gap existing when a distance is present.

The second statement is a **generic gap-detection description in the broader price-action material**. It is not explicitly stated there as the complete formula for `P_GAP` / Pressure gap.

This distinction matters. The material also describes Pressure gap separately as a gap occurring after a period of roughly 10–30 candles when buying pressure pauses and then a bullish trend bar appears, suggesting continuation. Therefore the available excerpt does **not** justify equating the generic High[2]/Low[0] gap test with the complete P-Gap definition.

The older source is still useful as terminology/context evidence, but it does not freeze SP2L P-Gap geometry.

## Candidate construction ledger

| Candidate | Evidence | Canonical? | Freeze impact |
|---|---|---:|---|
| Generic gap check involving High of two candles before vs Low of current candle | Related Poursamadi price-action excerpt | No | Still BLOCKED |
| `P_GAP` = Pressure gap | Related source glossary | No executable formula | Still BLOCKED |
| P-Gap is the validity condition for the SP2L breakout | Current primary SP2L artifact: `Valid BO = P-Gap` | Concept only | Still BLOCKED |
| Complete P-Gap OHLC formula / tolerance / mirror / role | No source-complete evidence yet | No | BLOCKED |

`High[2]` / `Low[0]` notation above is only a research normalization of the cited wording, **not a source-defined indexing convention** and not a proposed SP2L formula.

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

**P-Gap: SOURCE-CONFIRMED CONCEPT + RELATED-SOURCE TERMINOLOGY/CONTEXT EVIDENCE / EXACT SP2L FORMULA UNRESOLVED.**

The High[2]/Low[0] relationship remains an observed generic-gap clue only; it is **not** promoted to a P-Gap formula.

This is progress in source resolution, but it is **not** a Frozen Geometry pass.

## Gate impact

- Source Resolution: **PARTIAL PASS — P-Gap evidence strengthened, formula still unresolved**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

## Sources

- Current author-associated SP2L training index: https://t.me/s/tradingclub13
- Author SP2L strategy page: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/
- Related Poursamadi price-action course excerpt: https://www.scribd.com/document/666358452/%D8%AC%D8%B2%D9%88%D9%87-%DA%A9%D8%A7%D9%85%D9%84-%D8%A7%D8%B3%D8%AA%D8%A7%D8%AF-%D9%85%D8%AD%D9%85%D8%AF%D8%B9%D9%84%DB%8C-%D9%BE%D9%88%D8%B1%D8%B5%D9%85%D8%AF%DB%8C-%D9%88%DB%8C%D8%B1%D8%A7%DB%8C%D8%B4-%D8%B4%D8%AF%D9%87
