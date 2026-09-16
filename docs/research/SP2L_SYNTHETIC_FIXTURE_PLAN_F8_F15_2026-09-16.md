# SP2L Synthetic Fixture Plan — F8–F15 — 2026-09-16

## Objective

Create deterministic synthetic fixtures that answer source-resolution questions without using profitability or backtest optimization to choose geometry.

## Fixture matrix

| Fixture | Question | Required discrimination | If not discriminated |
|---|---|---|---|
| F8 | First relevant Low/High vs evolving latest HL/LH | Source-consistent structural anchor | UNRESOLVED |
| F9 | Entry anchor vs Start-of-Leg-2 | Distinct entry and continuation anchors | UNRESOLVED |
| F10 | Structural invalidation vs risk-budget stop; wick/body; opposite swing | Structural invalidation semantics | UNRESOLVED |
| F11 | Pending Limit update | Whether source requires dynamic replacement | UNRESOLVED; no threshold invented |
| F12 | 1/2/3-candle trigger family | Source-consistent trigger taxonomy | UNRESOLVED |
| F13 | 2X interpretation | Half-target vs second-position R/R interpretation | UNRESOLVED |
| F14 | AB=CD anchors | Unique A/B/C/D interpretation | UNRESOLVED |
| F15 | Bearish mirror | Symmetry of source-confirmed rules | UNRESOLVED |

## Design rules

1. Every fixture must have a known expected observation, not a profitability target.
2. Fixtures must isolate one geometry ambiguity at a time where practical.
3. Use deliberately separated price levels so competing interpretations produce visibly different outputs.
4. Do not encode an invented P-Gap formula, tolerance, fill semantics, stop buffer, replacement threshold, or execution assumption.
5. A fixture that cannot uniquely discriminate source meaning remains `UNRESOLVED`.
6. Fixture tests must be deterministic and reproducible.
7. No fixture result authorizes production BUY/SELL generation.

## Backtest-engine audit companion

Before using baseline statistics as evidence, the audit should separately verify:

- candidate count;
- closed trade count;
- OPEN count;
- AMBIGUOUS count;
- SL/TP precedence;
- tiny-risk trades and extreme-R trades;
- no accidental division-by-zero or near-zero-risk amplification;
- metric denominators and exclusion policy.

The current engine explicitly marks a candle that touches SL and TP as `AMBIGUOUS`, and OPEN/AMBIGUOUS have null `rMultiple`; therefore those outcomes are excluded from the current closed-trade metrics. This behavior must be tested explicitly before metric interpretation.

## Gate

This plan is research/validation infrastructure only. It does not freeze any unresolved Strategy A geometry. Frozen Geometry remains BLOCKED until source evidence and discriminating fixtures support a unique rule.
