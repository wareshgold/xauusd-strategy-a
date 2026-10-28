# V4 Trade Artifact Semantics Audit

- **TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`
- **Reviewed artifact:** `research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv`
- **Review basis:** read-only local inspection reported on 2026-10-28; raw artifact was not edited by this review.
- **Disposition:** documentation-only clarification. Research decision remains **BLOCKED / NOT_PROVEN**.

## Row inventory

The CSV contains 4,027 data rows and combines three semantically different row types:

| Row type | Rows | Meaning |
|---|---:|---|
| `V3_RR2_TRAIL4_PROXY` | 1,407 | V3 research-proxy trade rows |
| `V4_TP1R_NO_TRAIL_HYPOTHESIS` | 1,310 | V4 hypothesis trade rows |
| Blank `variant`, `comparison_type=PAIRED_COMMON_SIGNAL` | 1,310 | Paired comparison records, not additional independent trades |

The paired records have blank setup/entry identifiers and blank standalone trade outcomes in the inspected examples. Their baseline/V4 exit fields describe the two variants' outcomes for a common signal. In the reported grouping, 1,268 paired records are `UNRESOLVED` and 42 are `PASS`. These rows must not be added to the two variant trade populations as independent trades.

## Integrity and outcome limitations

- All 2,717 variant trade rows have `manifest_integrity=FAIL`; the 1,310 paired rows have no value in that field. The three full-period source CSV hashes differ from the acquisition-manifest hashes, and historical session-calendar applicability remains unverified.
- The `net_R` field is blank in the inspected V4 trade rows. Commission, spread, swap and slippage were not applied; there is no net-of-costs edge estimate in this artifact.
- The audit summary reports 1,374 ambiguous same-bar paths and 13 censored records across the combined trade rows. Ambiguous and censored outcomes are not decisive completed trades.
- The baseline proxy has many ambiguous OHLC paths, so its small decisive sample cannot support a fair statistical comparison against V4.
- A row-level `PASS` label is not a strategy validation or promotion decision. The backtest matrix remains blocked.

## Publication and handling rule

Keep the raw trade CSV unchanged for traceability. Interpret its rows by `variant` and `comparison_type`; do not count `PAIRED_COMMON_SIGNAL` rows as extra trades. Do not silently filter integrity failures, ambiguous paths, censored rows, or blank outcomes. Any future derived analysis should be emitted as a separate, explicitly named artifact with its own code, inputs and hashes.

This audit does not establish canonical SP2L geometry, executable fill semantics, valid transaction costs, or a production edge. No strategy promotion is authorized.
