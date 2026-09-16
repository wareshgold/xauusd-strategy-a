# SP2L Source-Discrimination Fixture Execution — 2026-09-16

## Scope

This pass creates deterministic fixtures for the remaining Entry / SL / 2X / Trigger / AB=CD ambiguities identified by Batch 6. The fixtures are discrimination infrastructure only; they do not define canonical Strategy A geometry.

## Fixture outcomes

| Fixture | Discrimination target | Current observation | Canonical status |
|---|---|---|---|
| F09 | Entry anchor vs Leg-2 start | Competing anchors remain representable and distinct | UNRESOLVED |
| F10 | Structural stop vs risk-budget / wick-body interpretation | Competing stop interpretations remain representable | UNRESOLVED |
| F11 | Pending Limit refresh | Refresh behavior can be modeled, but no mandatory threshold is encoded | UNRESOLVED |
| F12 | 1/2/3-candle + bar/key-bar family | All source-described forms remain represented without selecting one | PARTIAL |
| F13 | 2X half-target anchor | Entry-based and structural-anchor-based candidates are intentionally distinct | UNRESOLVED |
| F14 | AB=CD A/B/C/D anchors | Wick/body/structural-pivot candidates are intentionally distinct | UNRESOLVED |

## Guardrails

- No P-Gap OHLC formula was introduced.
- No AB=CD tolerance was introduced.
- No stop buffer was introduced.
- No Limit refresh threshold was introduced.
- No fill semantics were introduced.
- No production BUY/SELL logic was changed.
- Fixture outputs are not profitability evidence.

## Implementation

`research/fixtures/sp2l_source_discrimination_entry_sl_2x_trigger_abcd_v1.ts`

`tests/sp2l-source-discrimination-entry-sl-2x-trigger-abcd.test.ts`

The tests verify deterministic separation of competing interpretations and explicitly preserve unresolved status where source evidence does not uniquely identify an executable rule.

## Gate impact

Synthetic Fixture infrastructure advances, but Frozen Geometry remains BLOCKED. No untouched validation, robustness, fresh holdout, or production promotion is authorized by this pass.
