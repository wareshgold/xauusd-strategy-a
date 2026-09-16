# SP2L Fixture Execution Report — 2026-09-16

## Scope

F8–F15 synthetic fixtures have been instantiated as deterministic OHLC-level research tests. The suite is designed to expose competing interpretations, not to choose one by performance.

## Results recorded by construction

| Fixture | Observable separation | Canonical decision |
|---|---|---|
| F8 | First swing Low/High differs from latest swing | UNRESOLVED pending source discrimination |
| F9 | Entry price differs from Leg-2 start | SOURCE-DISCRIMINATED separation only |
| F10 | Structural invalidation differs from risk-budget stop | UNRESOLVED |
| F11 | Pending limit can be represented as a state transition without threshold | UNRESOLVED |
| F12 | 1/2/3 candle observations remain distinct | UNRESOLVED |
| F13 | Competing 2X target interpretations remain distinct | UNRESOLVED |
| F14 | Competing A/B/C constructions remain distinct | UNRESOLVED; no tolerance selected |
| F15 | Bearish OHLC mirror is deterministic | UNRESOLVED pending source discrimination |

## Important limitation

These are deterministic fixture constructions, not evidence that any unresolved interpretation is correct. The suite currently proves that the test harness can represent the ambiguities. Source evidence must still discriminate the canonical rule.

## Gate result

Synthetic fixture infrastructure: PASS.

Frozen Geometry: remains BLOCKED.

No profitability metric was used to select an interpretation.

Production BUY/SELL: OFF.
