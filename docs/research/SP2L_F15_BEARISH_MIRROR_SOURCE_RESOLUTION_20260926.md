# SP2L F15 Bearish Mirror Source Resolution — 2026-09-26

## Scope

This checkpoint tests whether the primary SP2L material independently supports the bearish/downward construction as a source-grounded mirror, without inventing a bullish-to-bearish OHLC mapping.

## Primary evidence

The primary transcript contains an explicit bearish example around 1:02:41–1:04:00.

- 1:02:41: the author describes a sequence of lower highs in the direction of the prior trend.
- 1:02:52: he explicitly identifies a first leg and a second leg in the broader bearish scenario.
- 1:03:03: he describes a nested 2Leg inside that move and says that leg completed its 2Leg and the TP was reached.
- 1:03:19: he describes the main scenario as one leg followed by another leg after a deep correction.
- 1:03:54: repeated lower highs with upward corrections are described as entry points for the decline.
- 1:04:00: he refers to waiting for a deeper leg/correction before acting.

This is direct source evidence that the two-leg concept is used in a bearish/downward construction, not merely an inferred mathematical mirror.

## Source-confirmed boundary

The source supports:

1. A bearish/downward SP2L construction exists.
2. Lower highs and corrective upward moves can form the directional structure of that bearish example.
3. The broader bearish move can be decomposed into Leg1 -> Correction -> Leg2.
4. A nested 2Leg can occur inside a larger leg.
5. TP completion is associated with completion of the relevant second leg in the example.

## Still unresolved

The source pass does not freeze a complete bearish executable contract:

- exact bearish P-Gap candle roles and indexing;
- exact bearish trigger candle;
- exact bearish entry anchor;
- exact bearish stop anchor;
- exact bearish fill/touch/close semantics;
- exact A/B/C/D OHLC semantics;
- exact equality/tolerance for bearish Leg1 = Leg2;
- exact precedence between nested and outer legs;
- exact 2X bearish lifecycle;
- exact sizing/execution rules.

Therefore the bearish side is source-consistent and directly illustrated, but it is not independently frozen as a complete executable mirror.

## Discrimination fixtures

- F15-001: clean bearish Leg1 -> Correction -> Leg2.
- F15-002: lower-high sequence with shallow correction.
- F15-003: lower-high sequence with deep correction.
- F15-004: nested bearish 2Leg inside outer Leg1.
- F15-005: competing bearish P-Gap candle mappings.
- F15-006: bearish trigger touch vs penetration vs close.
- F15-007: bearish stop-anchor alternatives.
- F15-008: bearish AB=CD anchor/tolerance alternatives.

Fixtures expose unresolved source questions; they do not select rules by backtest performance.

## Gate

F15 concept: SOURCE-CONFIRMED / DIRECTLY ILLUSTRATED.

F15 complete executable mirror: UNRESOLVED.

F15 exact OHLC geometry: UNRESOLVED.

Frozen Geometry: BLOCKED.

Untouched Validation: LOCKED.

Fresh Holdout: LOCKED.

Production: OFF.

## Reopen / escalation condition

Reopen F15 only if new primary evidence binds one or more currently unresolved bearish execution semantics. The existence of a bearish example alone must not be converted into an assumed exact bullish mirror.

## Non-negotiable boundary

Do not derive bearish formulas by simply negating or reversing current research code. Do not use backtest performance to decide bearish geometry.