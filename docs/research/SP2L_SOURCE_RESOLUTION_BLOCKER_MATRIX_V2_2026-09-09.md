# SP2L Source Resolution Blocker Matrix V2 — 2026-09-09

## Gate status

- SOURCE RESOLUTION: **PARTIAL PASS**
- SYNTHETIC FIXTURES: **PASS / ONGOING**
- FROZEN GEOMETRY: **BLOCKED**
- DEV: **LOCKED**
- UNTOUCHED VALIDATION: **LOCKED**
- ROBUSTNESS / STABILITY: **LOCKED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **LOCKED**

## Blockers

| ID | Area | Current source-safe conclusion | Remaining blocker | Severity |
|---|---|---|---|---|
| B1 | P-Gap | First-class source concept; valid BO associated with P-Gap; generic imbalance rejected | Exact OHLC/candle construction | CRITICAL |
| B2 | Entry | Pending Limit; relevant structural Low/High abstraction | Universal exact Entry anchor and wick/body semantics | CRITICAL |
| B3 | SL | Structural invalidation distinct from Entry | Exact OHLC anchor, wick/body, buffer | CRITICAL |
| B4 | Trigger | 1/2/3-candle and key-bar family observed | Exact acceptance and timing | CRITICAL |
| B5 | AB=CD | Leg-2 magnitude tied to Leg-1 magnitude | Exact A/B/C/D anchors and tolerance | CRITICAL |
| B6 | Leg2/TP | Leg 2 is separate continuation objective; TP1 preferred in teaching example | Exact executable projection and TP1/TP2 formulas | CRITICAL |
| B7 | Pending update | Order may be refreshed when structure/risk distance materially changes | Exact deterministic replacement threshold/timing | HIGH |
| B8 | Bearish mirror | Structural mirror is plausible and fixture-tested | Direct source geometry coverage across bearish examples | MEDIUM |
| B9 | Session | Good-hours/New York discussed | Canonical filter not established | MEDIUM |

## Latest fixture package

F18-F20 combined discrimination fixture and test:
- `research/fixtures/sp2l_f18_f20_geometry_discrimination_v1.py`
- `research/fixtures/test_sp2l_f18_f20_geometry_discrimination_v1.py`
- `docs/research/SP2L_F18_F20_SOURCE_TRIANGULATION_2026-09-09.md`

## Promotion rule

No blocker is cleared by backtest profitability. A blocker is cleared only by source evidence that uniquely determines the required geometry, or by an explicitly documented source-compatible rule that remains invariant across all relevant source examples.
