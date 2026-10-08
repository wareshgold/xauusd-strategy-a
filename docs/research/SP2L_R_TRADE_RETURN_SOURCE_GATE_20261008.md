# SP2L R / Trade-Return Source Resolution Gate — 2026-10-08

## Purpose

This checkpoint resolves the current source boundary for converting immutable Forward Observed Evidence into canonical trade-return / R statistics.

Source meaning always outranks implementation convenience and backtest performance.

## Research path audited

The following repository evidence was inspected:

- `docs/strategy-a.md`
- `docs/research/SP2L_SOURCE_RESOLUTION_CLOSURE_REPORT_2026-09-20.md`
- `docs/research/SP2L_F10_STOP_ANCHOR_SOURCE_CEILING_20260926.md`
- `docs/research/SP2L_F10_STRUCTURAL_VS_RISK_STOP_DISCRIMINATION_2026-09-16.md`
- `docs/research/SP2L_F13_2X_SOURCE_RESOLUTION_20260926.md`
- `docs/research/SP2L_OFFICIAL_AUTHOR_EVIDENCE_DELTA_20260926.md`
- `docs/research/SP2L_BATCH38_AUTHOR_IMPLEMENTATION_CROSSWALK_2026-09-17.md`
- `docs/research/SP2L_EXTREME_R_ROOT_CAUSE_NOTE_2026-09-16.md`
- `docs/research/SP2L_PIP_ACCOUNTING_CONTRACT_20260927.md`
- `scripts/analyze-r-baseline-stress.mjs`
- `scripts/analyze-risk-integrity.mjs`
- `scripts/audit-baseline-extreme-r.mjs`
- `scripts/sp2l_forward_risk_guard.py`
- `scripts/sp2l_pip_contract.py`

## Findings

### 1. R is used by the research implementation

The repository contains research artifacts that represent R as a normalized reward/risk quantity and persisted trade records with `rMultiple`.

The extreme-R forensic audit independently reconstructs one 125.196882R observation from persisted Entry/SL/TP prices:

`risk = abs(entry - stopLoss)`

`reward = abs(tp1 - entry)`

`R = reward / risk`

This proves that the historical implementation arithmetic is deterministic for that record.

It does **not** prove that the underlying Entry or SL geometry is source-canonical.

### 2. The source explicitly separates structural invalidation from risk budget

The source-resolution records establish that SL is a structural invalidation concept and that the stop is placed behind the candle from which the spike originated.

However, the exact executable stop price remains unresolved:

- wick vs body vs open/close;
- exact OHLC field;
- buffer/spread treatment;
- exact invalidation event.

Therefore the denominator of a canonical R calculation is not yet source-completely specified.

### 3. Entry geometry is also not fully frozen

Source evidence confirms the trigger reference relationships, including previous-candle Low for bullish and previous-candle High for bearish cases.

But the exact executable entry price and fill semantics remain unresolved.

Therefore the numerator is not fully source-complete either when R is interpreted as realized trade return from canonical Entry/SL/TP geometry.

### 4. TP / AB=CD geometry remains unresolved

Source evidence confirms the SP2L two-leg concept and the expectation that Leg 2 matches Leg 1 in the demonstrated concept.

Exact A/B/C/D anchors, measurement convention, equality tolerance, and target-fill semantics remain unresolved.

A source-canonical R mapping cannot use implementation-defined TP geometry to close this gap.

### 5. Pip accounting is explicitly separate

The pip accounting contract states that pip reporting is an accounting/reporting convention and does not change setup detection, Entry, SL, TP, or exit logic.

Therefore:

- observed `pips_result` is valid telemetry;
- observed `net` is valid telemetry;
- neither is a substitute for a source-confirmed R mapping.

### 6. 2X does not close the R boundary

The official source confirms the 50%-of-Entry-to-SL placement relation for 2X, but sizing, lifecycle, fill semantics, and stop relationship remain unresolved.

2X therefore cannot be used to infer a canonical multi-position R aggregation rule.

## Gate decision

**R / Trade-Return Mapping: BLOCKED — SOURCE INCOMPLETE**

No canonical mapping is promoted.

The existing Forward statistical boundary remains correct:

`Forward Observed Evidence -> observed pips/net statistics`

but:

`Forward Observed Evidence -> canonical R statistics`

remains blocked until explicit source evidence uniquely determines the required trade-return semantics.

## Explicitly prohibited shortcuts

Do not derive canonical R by:

- dividing observed net by an inferred dollar risk;
- dividing pips by a guessed stop distance;
- using current implementation Entry/SL/TP geometry as if it were frozen;
- treating `riskDistance` from a research implementation as canonical;
- using 2X examples to infer universal sizing or aggregated R;
- selecting an R mapping because it improves backtest/forward performance.

## Required source evidence to reopen

A future source-resolution pass must find direct primary-author evidence that uniquely binds:

1. Entry price/activation price;
2. SL price boundary;
3. TP/Leg-2 completion price or explicit target rule;
4. whether R is defined from initial risk, realized structural risk, or another denominator;
5. treatment of partial/secondary positions such as 2X;
6. treatment of costs, if R is intended to be cost-aware;
7. ambiguous intrabar outcomes, if relevant to realized trade return.

Until those are source-confirmed, the correct state is **BLOCKED**, not guessed.

## Gate rollup after this audit

| Gate | Status |
|---|---|
| Source Resolution | PARTIAL |
| R / Trade-Return Mapping | **BLOCKED** |
| Frozen Geometry | BLOCKED |
| Untouched Validation | LOCKED |
| Robustness / Stability | LOCKED |
| Fresh Holdout | LOCKED |
| Forward Observed Evidence | AVAILABLE |
| Forward Observed Statistics | AVAILABLE for pips/net telemetry only |
| Canonical R Statistics | BLOCKED |
| Production | OFF |

## Engineering consequence

No Strategy A geometry, execution semantics, or production decision logic is changed by this checkpoint.

The existing fail-closed `ForwardStatisticalBoundary` remains the enforcement point. It must continue to require an explicit, source-resolved mapping before any Forward evidence can enter an R-based statistical result.

## Next parallel research tracks

1. Primary-source pass for exact Entry/SL/TP trade-return semantics.
2. Source audit of the worked numerical trade examples for any explicit risk/return calculation.
3. Separate audit of 2X risk aggregation semantics.
4. Keep Forward observed pips/net reporting running without converting it to canonical R.
