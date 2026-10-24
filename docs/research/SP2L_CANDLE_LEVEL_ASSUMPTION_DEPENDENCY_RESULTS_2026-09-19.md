# SP2L Candle-Level Assumption Dependency Results — 2026-09-19

## Result

**Candle-level attribution evidence acquired and analyzed for all 38 archived research signals.**

Input artifact SHA-256:
`3a45f71e5cc58763df25852ff3619209f96926470200943164bfe29eef1e7e29`

Analysis report SHA-256:
`bc08281a732bc211c6c770c2aabccce9e7fdbd1baccadef61e9400d4c439c207`

## Integrity

- Expected signals: 38
- Mapped: 38
- Not found: 0
- Insufficient context: 0
- Preserved data gaps: 7
- Candle index continuity: PASS
- Signal timestamp alignment: PASS

## Attribution findings

| Component | Evidence status | Canonical status |
|---|---|---|
| P-Gap | 38/38 observable candidate measurements only | UNRESOLVED |
| Spike/body | Candle-level body/range measurements available | UNRESOLVED predicate |
| Trigger | 38/38 satisfy the analyzer's descriptive High/Low relationship | Source trigger semantics still unresolved |
| Swing/SL | 38/38 have measurable SL distances to context OHLC levels | Exact swing/anchor unresolved |
| AB=CD | Not attributable from artifact | UNRESOLVED |
| Pending lifecycle/fill | Not attributable from artifact | UNRESOLVED |
| TP/risk | Directly observable for archived research run | NOT CANONICAL |

The trigger result is descriptive only. The analyzer's relationship is not asserted to be the source's complete trigger rule and does not resolve touch/wick/close, indexing precedence, pending-order behavior, or fill semantics.

## Outcome distribution

- WIN: 27
- LOSS: 10
- AMBIGUOUS: 1

The outcome distribution is not used to promote or resolve any unresolved source rule.

## Interpretation

The candle-level artifact materially improves observability compared with the prior trade-level evidence inventory. It permits direct measurement of candle relationships for P-Gap candidates, spike/body characteristics, trigger relationships, and SL distances.

It does **not** establish the canonical P-Gap formula, exact trigger semantics, relevant swing rule, AB=CD anchors/tolerance, or pending-order lifecycle/fill semantics.

## Gate impact

- Source Resolution: PARTIAL
- Assumption Dependency Audit: **CANDLE-LEVEL EVIDENCE COMPLETE FOR THIS FROZEN WINDOW**
- Frozen Geometry: **BLOCKED**
- Parameter Robustness: POSITIVE RESEARCH EVIDENCE
- Parameter Stability: INCONCLUSIVE — NO PASS / NO FAIL
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Production: BLOCKED
- Live Trading: DISABLED

## Non-inference rule

No unresolved source rule is promoted because all 38 signals satisfy an observed descriptive relationship or because the research outcomes are positive.
