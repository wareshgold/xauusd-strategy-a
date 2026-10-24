# SP2L F16 — Round Level Source Resolution Audit — 2026-09-19

## Purpose
Source-first audit of the SP2L Round Level concept. The objective is to determine whether the primary material uniquely defines a deterministic interval/rounding algorithm and its role in Strategy A.

## Evidence reviewed
- `docs/research/SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`
- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`

## Source-confirmed findings

1. “Round level” is explicitly taught in the primary sequence.
2. The inspected primary-artifact sequence contains multiple worked spacing examples, including 250 point, 500 point, and 1000 point annotations.
3. Round Level is therefore a source-confirmed teaching concept, not an invented implementation feature.

## Still unresolved

- Whether 250, 500, and 1000 points are examples, selectable classes, or universal intervals.
- Exact meaning of “point” in the source versus broker/platform point size.
- Exact rounding function: nearest, floor, ceiling, or level construction from a reference price.
- Whether the level is used for entry selection, target selection, risk filtering, context, or another purpose.
- Whether the interval depends on symbol, timeframe, price regime, volatility, setup direction, or another condition.
- Whether bullish and bearish construction are identical mirrors.
- Whether Round Level is mandatory or optional.
- Interaction with AB=CD, P-Gap, Buy Limit, 2X, TP1/TP2, and SL.
- Exact boundary/touch semantics if price reaches a Round Level.

## Non-inferences

Do not canonicalize:
- 250, 500, or 1000 as the universal Round Level interval.
- Conventional psychological-price rounding.
- A fixed modulo/quantization formula.
- Any specific use of Round Level in signal generation or target construction.
- Any broker-specific point conversion.

## Gate impact

**F16: PARTIAL / UNRESOLVED.**

The concept and example values are source-confirmed, but no unique executable algorithm has been established.

**Frozen Geometry remains BLOCKED.**

No backtest or parameter selection is justified by this audit.

## Highest-value next evidence

The most useful source artifact would explicitly show one or more Round Level examples with the reference price, exact level calculation, unit definition, and stated purpose in the setup. A machine-readable author explanation would be sufficient if it unambiguously maps the examples to an algorithm.
