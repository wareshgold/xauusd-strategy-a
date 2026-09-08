# SP2L P-Gap Hypothesis Discrimination Pack — 2026-09-08

## Status

RESEARCH ONLY. This document does not freeze P-Gap geometry and must not be imported by production Strategy A.

## Objective

Move from the frozen semantic contract to synthetic discrimination of competing P-Gap geometries without using historical profitability to decide source meaning.

## Source constraint

The source establishes that a valid breakout/Spike is associated with P-Gap and visually describes non-overlap/gap conditions. The available source material does not uniquely identify the OHLC boundaries, candle timing, equality/touch rule, or minimum gap size. Therefore the candidates below are explicitly hypotheses.

## Candidate families

### H1 — Adjacent wick gap

Bullish candidate: the current candle low is strictly above the immediately preceding candle high. Bearish is the exact directional mirror.

### H2 — Three-candle outer-wick gap

Bullish candidate: candle C low is strictly above candle A high across an A-B-C window. Bearish is the mirror. This is deliberately labelled a generic research construct, not "FVG = P-Gap".

### H3 — Adjacent body gap

Bullish candidate: current candle body-low is strictly above previous candle body-high. Bearish is the mirror.

### H4 — Three-candle outer-body gap

Bullish candidate: C body-low is strictly above A body-high. Bearish is the mirror.

## Discrimination fixtures

The fixture pack must contain cases where these hypotheses disagree:

1. wick-only separation with body overlap;
2. body-only separation with wick overlap;
3. three-candle outer separation without adjacent separation;
4. adjacent separation that is not present between A and C;
5. exact-touch boundary;
6. bearish mirrors of the above;
7. multi-candle sequence where more than one candle could be labelled the gap candle.

## Interpretation rule

A fixture can eliminate a candidate only when the source visual/transcript evidence clearly requires the candidate to classify differently. A fixture cannot select a candidate merely because it produces cleaner or more profitable historical signals.

## Explicit non-decisions

This pack does not decide:

- P-Gap = generic FVG;
- wick versus body convention;
- two-candle versus three-candle timing;
- strict versus inclusive touch;
- minimum gap size;
- breakout candle identity;
- entry price;
- SL price;
- AB=CD tolerance.

## Gate

SYNTHETIC FIXTURES: ACTIVE
FROZEN GEOMETRY: BLOCKED
DEV/VAL/HOLDOUT: LOCKED
PRODUCTION: UNCHANGED
