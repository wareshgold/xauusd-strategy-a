# RR4_ACT50_D40 Candidate Evidence Snapshot

**Record type:** observed research candidate snapshot  
**Captured:** 2026-11-01  
**Status:** `OBSERVED_NOT_REPRODUCED`  
**Research status:** `NOT_VALIDATED`  
**Canonical:** `false`

This record preserves the candidate and the evidence visible in the user's dashboard report. It is not a claim that the replay has been independently reproduced or statistically validated. No production decision is authorized by this record.

## 1. Candidate identity

| Field | Recorded value |
|---|---|
| Candidate label | `RR4_ACT50_D40` |
| Exit target | 4R |
| Trailing activation | 50 MT5 points |
| Trailing distance | 40 MT5 points |
| MT5 point used for interpretation | 0.01 price units |
| Activation in price units | 0.50 |
| Trailing distance in price units | 0.40 |
| Entry population size | 462 |
| Decisive outcomes shown | 461 |
| Unresolved/ambiguous count implied | 1 |
| Selection provenance | User-confirmed manual parameter selection |
| Entry logic / population | Unchanged frozen V3 activated-proxy population |

The user explicitly confirmed that RR=4, activation=50, and distance=40 were manually selected, not dashboard defaults.

## 2. Session and source provenance

| Field | Recorded value |
|---|---|
| Session ID | `4f77e39c5a51e8313bf7ba53ff26e2c8fa1106fbe6f4d444a8ba2be8e797efee` |
| M1 artifact ID | `0:20261024T075827Z/xauusd_ecn_m1_30d.csv` |
| Entry artifact ID | `1:frozen-entry-populations/frozen_entry_population_a_trail_0_40_activated_proxy_v3.csv` |
| M1 SHA-256 | `b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285` |
| Entry SHA-256 | `39ed87cd1f0be3e59b5f064b0bcf97a9787e5266df6e972aa07e5ea4d3608ab1` |
| Observed UTC window | `2026-09-24T07:57:00+00:00` to `2026-10-23T23:57:00+00:00` |
| Window source | `M1_CSV_OBSERVED_FIRST_LAST_ROWS` |
| MT5 point | `0.01` |
| Contract size | `100` |
| Volume | `0.01` |
| Engine revision | `V3-EXIT-ENGINE-1` |
| Session fingerprint recomputation | Exact match |
| Population status | `NOT_VALIDATED` |
| M1 metadata provenance | `CALLER_ASSERTED_CSV_IDENTITY_NO_EMBEDDED_SYMBOL_OR_WINDOW` |
| Symbol identity verified | `false` |

The session fingerprint was independently recomputed using the exact identity fields and canonical JSON serialization implemented by `V3ExitReplayEngine`:

```json
{"contract_size":100.0,"dataset_sha256":"b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285","engine_revision":"V3-EXIT-ENGINE-1","entry_population_sha256":"39ed87cd1f0be3e59b5f064b0bcf97a9787e5266df6e972aa07e5ea4d3608ab1","mt5_point":0.01,"volume":0.01}
```

SHA-256 of this canonical identity equals the recorded Session ID exactly. This verifies the Session's parameter identity, not the trade replay outputs.

The 462 rows are the frozen population `A_TRAIL_0.40_ACTIVATED_PROXY_V3`; they are not all V3 entries and do not establish canonical SP2L entry geometry. The M1 CSV has known reported gaps; gaps were not filled or classified. Same-bar SL/TP and M1 gap behavior remain ambiguous under the OHLC proxy.

## 3. Dashboard run identifiers observed

The supplied dashboard capture showed two separate completion notices:

- Section 02 point-based exit replay: `f7d4b4cb43736ddb3d8c76e081b49ea063ca606136bee71218497dc06ef74325`
- Section 02B management replay: `ab3659d7e92e3ffc9daed76f4ef4e663a055af185505fe2508082c090ce44b13`, displayed as `FIXED_RR_ca19ffa5`

The summary panel displayed variant `RR4_ACT50_D40`. The pasted capture does not include an explicit summary-to-run-ID binding or the normalized request spec for each run. Therefore this record does **not** assert which run ID generated every summary field. Resolve this association from the dashboard API/run record before treating the result as reproducible.

## 4. Summary as displayed

| Metric | Dashboard value |
|---|---:|
| Signals | 462 |
| Decisive | 461 |
| Net R | +154.964 |
| Gross profit USD | 725.760 |
| Gross loss USD | 282.620 |
| Gross net USD | +443.140 |
| Profit factor | 2.652 |
| Max drawdown R | 6.728 |
| Variant | `RR4_ACT50_D40` |
| Rows | 462 |
| Cache entries | 36 |
| Validation | `NOT_VALIDATED` |

### Profit-factor basis

Code inspection of `src/strategy_factory/v3_exit_engine.py::summarize` confirms that `profit_factor` is calculated in **R units**:

`gross_profit_r / gross_loss_r`

The displayed gross-profit and gross-loss USD figures imply a separate USD ratio:

`725.760 / 282.620 = 2.568...`

That USD ratio is not expected to equal the reported R-based PF of `2.652`, because each trade can have a different initial risk in price/USD terms. This is a difference in metric basis, not by itself an arithmetic defect. For future reports, label the existing metric explicitly as **PF (R-based)** and, if useful, report **PF (USD-based)** separately. The displayed `2.652` remains an observed R-based value, not a validated result.

## 5. Spread sensitivity as displayed

The dashboard reported assumed spread-only scenarios:

| Assumed spread | Cost per decisive trade | Estimated gross net after assumed spread |
|---:|---:|---:|
| 20 MT5 points | $0.20 | $350.94 |
| 23 MT5 points | $0.23 | $337.11 |
| 30 MT5 points | $0.30 | $304.84 |

These totals use 461 decisive trades (not all 462 signals). They are scenario deductions, not historical execution P&L. Commission and slippage are excluded. The displayed spread is not established as a fixed historical spread and must not be treated as one.

## 6. Reproduction and forensics requirements

The following are required before this candidate can be marked reproducible:

1. Retrieve the exact run record and normalized parameter specification for `RR4_ACT50_D40`.
2. Update to the dashboard evidence-export revision (PR #385) and download the complete replay JSON, preserving the session request/manifest, normalized run spec, variant ID, trade-row SHA-256, and all 462 trade rows.
3. Re-run against the exact session fingerprint and verify identical per-trade outcomes, aggregate metrics, and output hash.
4. Produce a trade-level contribution analysis: top 1/5/10 trade contribution, win/loss distribution, R quantiles, holding-time distribution, exit-reason counts, unresolved/gap-exposed counts, and concentration of gross profit.
6. Confirm contract size, volume, MT5 point, and engine revision from the session's persisted manifest rather than relying on a UI default or a separate terminal observation.

No trade-level rows were included in the supplied dashboard text. The dashboard evidence-export enhancement is being added separately in PR #385; until that revision is deployed and its JSON export is supplied, no trade concentration, distribution, or independent replay claim is made here.

## 7. Robustness protocol (not yet run)

Keep the entry population, M1 artifact, session metadata, initial SL, and engine revision fixed. Treat all parameter combinations as exploratory development, not validation.

Suggested local neighborhood around the user-selected candidate:

- RR: `3.0, 3.5, 4.0, 4.5, 5.0`
- Activation: `40, 45, 50, 55, 60` MT5 points
- Distance: `30, 35, 40, 45, 50` MT5 points

This is a 125-cell grid. Record every attempted cell, including failures and ambiguous/open outcomes; do not select only profitable cells. Report the full response surface, neighboring-cell stability, paired trade-level deltas against `RR4_ACT50_D40`, and sensitivity to unresolved bars/gaps. Avoid repeated tuning on this same window after the grid; it has already influenced candidate selection and is not a fresh holdout.

Before launching the full grid, validate one repeat of the anchor and a small set of boundary/synthetic cases. Any change in engine semantics requires a new engine revision and a new evidence record.

## 8. Explicit limitations and governance

- OHLC M1 proxy only; no tick fills.
- M1 gaps and same-bar SL/TP remain ambiguous.
- No spread, commission, slippage, swap, or broker execution semantics are applied to the replay.
- Spread sensitivity is assumed cost-only analysis, not actual execution accounting.
- Symbol identity is not verified by the CSV.
- No source-confirmed SP2L geometry or canonical exit rule is established.
- This candidate is research-only, non-canonical, and `NOT_VALIDATED`.
- The current sample has been used for parameter selection; it cannot serve as an untouched fresh holdout.
- No production BUY/SELL decisions or live-trading authorization follow from this record.

## 9. Code provenance

The snapshot branch was created from PR #382 head:

- Branch base: `research/v3-management-matrix-20261101`
- Base commit: `01858bb815c6f1d83d3028804be79710082d439b`
- PR #382 remains draft and stacked on PR #381; do not merge independently.

