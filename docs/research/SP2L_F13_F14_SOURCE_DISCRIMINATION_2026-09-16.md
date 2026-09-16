# SP2L F13/F14 — 2X and AB=CD Source Discrimination — 2026-09-16

## F13 — 2X

The source confirms 2X as a second-position / reward-management concept. Source evidence includes a second position associated with half-target language, while another teaching example demonstrates a second position with its own reward profile.

The current fixture correctly keeps competing interpretations numerically distinct, but this distinction is not itself a canonical formula.

### Status

- 2X concept: `SOURCE-CONFIRMED`
- Exact numeric formula: `UNRESOLVED`
- Half-target interpretation: observed source interpretation, not promoted to universal formula
- Second-position R-multiple interpretation: observed source interpretation, not promoted to universal formula

No optimization or backtest performance is permitted to choose between them.

## F14 — AB=CD

The source confirms the magnitude relationship that Leg 2 is expected to be approximately equal to Leg 1. It does not uniquely label the four candle-level anchors A/B/C/D with deterministic OHLC semantics, nor does it provide a universal tolerance.

The current fixture demonstrates that competing A/B/C constructions can produce distinct underlying anchor sets even when a simple target calculation happens to coincide.

### Status

- AB=CD magnitude relationship: `SOURCE-CONFIRMED`
- Exact A/B/C/D anchors: `UNRESOLVED`
- Entry=C assumption: prohibited
- Fibonacci substitution: prohibited
- Numerical tolerance: `UNRESOLVED`

## Gate impact

F13 and F14 remain useful research fixtures but neither permits Frozen Geometry to pass.

- Source Resolution: `PARTIAL PASS`
- Synthetic Fixtures: `PASS`
- Frozen Geometry: `BLOCKED`
- Untouched Validation: `LOCKED`
- Robustness/Stability: `LOCKED`
- Fresh Holdout: `LOCKED`
- Production: `OFF`

## Research rule

Where the source confirms a concept but not a unique deterministic formula, preserve the concept and explicitly leave the formula unresolved. Do not manufacture a canonical formula from profitability, convenience, or parameter search.
