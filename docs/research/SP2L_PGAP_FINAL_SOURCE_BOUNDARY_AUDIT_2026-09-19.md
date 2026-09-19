# SP2L P-Gap — Final Source Boundary Audit — 2026-09-19

## Purpose
Consolidate the existing P-Gap forensic passes and determine whether the current repository evidence permits an executable canonical P-Gap rule.

## Evidence consolidated
- Batch35: author-associated current SP2L material.
- Batch36: primary-artifact + legacy author-attributed candidate construction.
- Batch37: mirror/indexing negative resolution.
- Primary transcript: P-Gap / E-Gap distinction and valid-BO relationship.
- Frozen Geometry Gate audit.

## Source-confirmed boundary
The source confirms:
1. P-Gap is a distinct SP2L concept.
2. A valid SP2L breakout/spike is associated with P-Gap.
3. P-Gap is distinguished from E-Gap.
4. P-Gap is part of the validity chain for the demonstrated breakout.

## Candidate evidence
Legacy author-attributed material contains a bullish-oriented description comparing the high of the candle two bars before with the low of the current candle. This remains an author-attributed legacy candidate, not a source-complete current-SP2L specification.

## Unresolved executable fields
- exact current-SP2L candle indexing;
- bearish mirror;
- wick vs body vs other OHLC boundary;
- zero-width handling;
- minimum threshold/tolerance;
- which candle(s) within the spike qualify;
- whether P-Gap merely validates the spike or also determines an order/entry boundary.

## Decision
**P-Gap = UNRESOLVED for canonical executable geometry.**

The legacy bullish candidate is retained as a non-canonical research hypothesis only.

No normalization such as `High[2] > Low[0]` is promoted.

## Gate impact
Frozen Geometry remains **BLOCKED**. No backtest, optimization, or production logic changes are justified by this audit.
