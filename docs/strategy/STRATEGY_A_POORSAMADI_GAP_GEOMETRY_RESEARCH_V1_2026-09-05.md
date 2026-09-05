# Strategy A — Poorsamadi Gap Geometry Research v1

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Status:** Research/codification only — no Strategy A production implementation changes

## 1. Purpose

This document incorporates the newly supplied Poorsamadi lesson on the effect of gap types at different chart locations. It resolves the semantic role of P-GAP versus exhaustion gap and identifies which parts can now be made deterministic without inventing missing rules.

The raw lesson remains the semantic authority. Numeric thresholds, exact candle-index formulas, and execution policies remain TBD unless explicitly supported by the lesson.

## 2. New source-established findings

### 2.1 Gap type is contextual, not purely geometric

The teacher explicitly rejects treating every visible gap as the same object. The relevant interpretation depends on:

- timeframe;
- trading session / time of day;
- market / symbol;
- market location;
- trend/cycle context;
- whether the movement is occurring at the beginning/continuation or exhaustion/end of a move.

Therefore a detector that labels a gap from candle geometry alone is insufficient for canonical semantic classification.

### 2.2 Pressure gap (P-GAP)

P-GAP is described as a pressure movement that helps push/break the market from a range or continuation structure. In the SP2L lesson, the teacher uses P-GAP as evidence associated with the spike branch.

Source-supported interpretation:

`range/context -> pressure movement / P-GAP -> directional continuation or breakout context`

However, the exact mathematical definition of P-GAP is not supplied in this lesson. No minimum gap size, candle-count rule, overlap percentage, or OHLC formula is promoted here.

### 2.3 Exhaustion gap

An exhaustion gap is explicitly distinguished from P-GAP. The lesson gives examples where a visually strong gap occurs late in a move, near an important level, and should be interpreted as exhaustion rather than pressure.

Source-supported consequence:

- a gap late in an already extended movement is not automatically bullish/bearish pressure evidence;
- when the contextual evidence identifies exhaustion, the teacher describes it as a potential reversal/exit signal rather than a continuation entry signal;
- therefore P-GAP evidence must be conditioned on market location and sequence, not merely gap appearance.

### 2.4 Gap at the end of a move

The teacher explicitly states that exhaustion gaps should occur at the end of the trend/movement. This is a semantic sequencing constraint, not yet a numeric detector.

Candidate state distinction:

- `PRESSURE_GAP`: supports directional/spike interpretation when it occurs in the appropriate structural context;
- `EXHAUSTION_GAP`: late-move gap at an important/extreme location, potentially supporting exit/reversal logic.

The system must not treat these as interchangeable evidence.

## 3. Session and location are mandatory context dimensions

The lesson repeatedly warns against taking a gap setup simply because a visually similar candle/gap appears at an arbitrary time or location.

The teacher gives a concrete example in which a move forms around a time when the relevant US market decision-makers are not active, and explicitly uses timing/session context to downgrade the interpretation.

This strengthens the earlier codification conclusion:

`gap geometry != complete signal`

The canonical state machine must carry contextual metadata before classifying a gap.

## 4. Interaction with SP2L

The SP2L source previously established that P-GAP can be part of the strong-movement/spike family and that several sequence variants exist. The new lesson reinforces that relationship but does not replace the earlier TBD grammar.

Canonical research model:

`RANGE/LOCATION -> BREAKOUT/STRONG MOVE -> FT -> P-GAP evidence (when present) -> SPIKE FAMILY`

Important: P-GAP is evidence within the spike family, not a universal requirement for every spike branch, because the earlier SP2L lesson describes multiple strong-movement variants and does not establish a universal P-GAP requirement.

## 5. What is now safe to codify

The following semantic rules are now stronger than before:

1. P-GAP and exhaustion gap are different concepts.
2. Gap interpretation depends on context.
3. P-GAP is continuation/pressure evidence in the appropriate structural context.
4. Exhaustion gap is late-move evidence and can support exit/reversal interpretation.
5. Time/session must be considered before interpreting a gap.
6. Market location must be considered before interpreting a gap.
7. A visible gap alone is not sufficient to create an SP2L signal.
8. P-GAP should remain a feature/branch discriminator until its exact geometry is sourced.

## 6. What remains explicitly TBD

The lesson does **not** establish:

- exact gap-size formula;
- whether gap is measured between bodies, wicks, or candle ranges;
- minimum gap size in points/ATR/ticks;
- exact number of candles required;
- exact non-overlap tolerance;
- exact P-GAP versus Common-GAP/E-GAP decision tree;
- exact session clock windows;
- exact location-distance threshold;
- exact exhaustion detector;
- exact reversal trigger after exhaustion gap;
- exact stop placement for exhaustion-gap trades.

These must not be fabricated from the transcript.

## 7. Consequence for current implementation

No production Strategy A code is changed by this document.

In particular, the existing SpikeDetector's fixed overlap/directional thresholds remain implementation assumptions and must not be re-labelled as Poorsamadi-canonical rules merely because the source discusses overlap and strength.

The current BreakoutDetector's prior-high/prior-low lookback also remains an implementation choice; the source supports the semantic concept of a close beyond a relevant level, but not this exact lookback algorithm.

## 8. Research gate

Before implementing a deterministic P-GAP detector, the following must be supplied or independently established through source recovery:

1. exact P-GAP geometry;
2. exact Common-GAP / E-GAP / exhaustion classification;
3. precise session/time context;
4. precise location rule;
5. deterministic execution/reversal rule;
6. test fixtures representing positive and negative examples.

Only then should the candidate detector be evaluated against historical data.

## 9. Relation to previous geometry work

This lesson materially resolves the **semantic role** of P-GAP but does not resolve the remaining SP2L price geometry:

- Leg1 endpoints: TBD;
- Leg2 projection origin: TBD;
- Leg2 tolerance: TBD;
- structural SL exact reference: TBD;
- touch versus close invalidation: TBD;
- same-candle execution ordering: TBD;
- exact limit-order replacement threshold: TBD.

Therefore the next research step remains Geometry Resolution rather than production implementation.

## 10. Source provenance

Input: user-supplied transcript, titled as the lesson on the effect of different gap types at every chart location, covering approximately 0:00–16:21.

Key source intervals used:

- 0:00–0:53 — distinction between exhaustion gap and pressure gap.
- 3:04–3:46 — time/session discipline.
- 4:00–5:36 — pressure versus exhaustion interpretation and stop-distance context.
- 6:08–7:51 — session context and transition from pressure to exhaustion.
- 8:17–9:48 — late-move exhaustion and reversal/exit behavior.
- 14:19–15:16 — exhaustion at the end of movement versus pressure gaps breaking a range.
- 15:44–16:13 — gap interpretation depends on session and market location; pressure gaps used for entry, exhaustion gaps for exit/reversal context.

## 11. Decision

**STATUS: SEMANTICALLY RESOLVED / GEOMETRICALLY INCOMPLETE**

This lesson closes a major P0 semantic gap around P-GAP versus exhaustion gap. It does not justify adding a guessed P-GAP formula to production.
