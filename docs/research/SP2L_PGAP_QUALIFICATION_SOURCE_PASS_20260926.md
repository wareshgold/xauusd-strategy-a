# SP2L P-Gap Qualification Source Pass — 2026-09-26

## Objective

Targeted source pass after the P-Gap source-ceiling checkpoint. The question was whether newly available public material binds the SP2L P-Gap concept to a unique executable candle-role formula.

## New primary/official evidence

The official author SP2L page states that a valid SP2L Spike has a price gap (P-Gap) between candles and that a sharp movement without a gap is not considered valid. It also states that the SL is behind the candle from which the spike originated, and describes the second-leg correction/entry relationship.

The page confirms the semantic dependency:

valid SP2L Spike -> P-Gap required

It does not expose a unique OHLC index equation for P-Gap.

## Existing primary transcript reconciliation

The preserved primary SP2L transcript remains the stronger source for structural ordering. It explicitly describes multiple P-Gap constructions, including:
- breakout first, then higher lows, then P-Gap;
- higher lows first, then P-Gap;
- delayed formation of the gap on a following candle.

Therefore a single universal fixed index cannot be promoted merely from the official page's statement that a P-Gap exists between candles.

## Generic Gap evidence

The separate gap lesson supports a generic bullish gap construction based on separation between a prior High and current Low. This is useful as generic gap evidence, but the source does not explicitly bind that generic construction as the universal SP2L Pressure-Gap executable formula.

## Third-party implementation evidence

A public third-party SP2L indicator description was found that uses a three-candle gap construction and spike filters. It is not author-primary evidence and is therefore recorded only as corroborating external implementation evidence. It cannot close the canonical source gate.

## Decision

The targeted pass does not close the executable P-Gap blocker.

### Status

- P-Gap semantic identity: SOURCE-CONFIRMED
- P-Gap required for valid SP2L Spike: SOURCE-CONFIRMED
- Generic gap primitive: SOURCE-CONFIRMED in generic-gap material
- Adjacent non-overlap primitive: SOURCE-DISCRIMINATED
- Exact SP2L P-Gap candle roles/index: UNRESOLVED
- Complete P-Gap qualification: UNRESOLVED
- Frozen Geometry: BLOCKED

## Stopping rule

No additional backtest, parameter optimization, or third-party implementation comparison should be used to choose among unresolved P-Gap interpretations.

Only genuinely new author-primary evidence that binds candle roles and qualification may reopen this gate.
