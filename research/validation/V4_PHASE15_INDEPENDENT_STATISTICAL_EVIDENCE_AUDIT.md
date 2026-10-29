# V4 Phase 15 — Independent Statistical Evidence Audit

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `f992bd1a`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Date:** 2026-10-28

## Inputs (verified)
| Item | Path | SHA256 | Notes |
|---|---|---|---|
| Trade CSV (source of record) | `research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv` | `c3e5622af4aae480db7b36c8db7599ea9b91397cbb1408b0d6183da64bde3967` | 4028 lines total (4027 rows + header) |
| Phase 6 manifest | `research/manifests/V4_PHASE6_SIGNAL_AUDIT_MANIFEST.json` | `4fd34c0ac2ef84fbb13215453d2ba998393fa36c912a4b6707eeccf927cb8eb6` | Input/output hashes match; validation checks recorded |
| Phase 6 counts CSV | `research/backtests/V4_PHASE6_SIGNAL_COUNTS_20261028T000000Z.csv` | `6138937af3cf538afb7d7364d41017bf33150485b8d1a86897444e4a35209104` | Reproducible from trade CSV |
| Run summary | `research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_run_summary.json` | (referenced) | Contains integrity gates, split details, bootstrap intervals |
| Reports reviewed | `research/reports/V4_RESEARCH_EXECUTIVE_REPORT.md`, `research/validation/V4_STATISTICAL_VALIDATION.md`, `research/holdout/V4_HOLDOUT_REPORT.md` | — | Prior claims audited |

Related identity/blocker evidence: Phase 4/6/12/13/14 reports (all confirm `SIGNAL_IDENTITY_NOT_ESTABLISHED`).

## Row/variant decomposition (reproduced)
From trade CSV:
- Total rows: **4027**
- By variant: `V3_RR2_TRAIL4_PROXY` = **1407**, `V4_TP1R_NO_TRAIL_HYPOTHESIS` = **1310**, `''` (paired) = **1310**
- By split: `DEVELOPMENT` = 1622, `VALIDATION` = 1514, `FRESH_HOLDOUT_DIAGNOSTIC` = 891
- By comparison_type: `''` = 2717, `PAIRED_COMMON_SIGNAL` = 1310

This matches Phase 6 manifest expectations exactly (variant totals and total rows). Paired rows are comparison records (not independent variant trades).

## Descriptive gross metrics (reproduced where semantics clear)
Using `gross_R`, `ambiguous`, `censored` as recorded. "Decisive" = not ambiguous and not censored. All numbers below are **gross, before costs**.

### V4 (`V4_TP1R_NO_TRAIL_HYPOTHESIS`)
| Split | decisive n | wins/losses | gross profit/loss (R) | net R | PF | ambiguous | censored |
|---|---|---|---|---|---|---|---|
| DEVELOPMENT | 524 | 321/203 | +321.0 / -203.0 | +118.000 | 1.581281 | 2 | 3 |
| VALIDATION | 479 | 309/170 | +309.0 / -170.0 | +139.000 | 1.817647 | 6 | 6 |
| FRESH_HOLDOUT_DIAGNOSTIC (Sep) | 280 | 173/107 | +173.0 / -107.0 | +66.000 | 1.616822 | 6 | 4 |

### V3 proxy (`V3_RR2_TRAIL4_PROXY`)
| Split | decisive n | wins/losses | gross profit/loss (R) | net R | PF | ambiguous | censored |
|---|---|---|---|---|---|---|---|
| DEVELOPMENT | 17 | 0/17 | +0.0 / -17.0 | -17.000 | 0.000000 | 547 | 0 |
| VALIDATION | 15 | 0/15 | +0.0 / -15.0 | -15.000 | 0.000000 | 517 | 0 |
| FRESH_HOLDOUT_DIAGNOSTIC (Sep) | 15 | 0/15 | +0.0 / -15.0 | -15.000 | 0.000000 | 296 | 0 |

### Paired comparison records (`PAIRED_COMMON_SIGNAL`)
| Split | decisive n | wins/losses | gross profit/loss (R) | net R | PF | ambiguous | censored |
|---|---|---|---|---|---|---|---|
| DEVELOPMENT | 529 | 0/0 | +0.0 / -0.0 | 0.000 | inf | 0 | 0 |
| VALIDATION | 491 | 0/0 | +0.0 / -0.0 | 0.000 | inf | 0 | 0 |
| FRESH_HOLDOUT_DIAGNOSTIC (Sep) | 290 | 0/0 | +0.0 / -0.0 | 0.000 | inf | 0 | 0 |

**Reproducibility:** The V4 gross R/PF values above match the claims in Executive Report and Statistical Validation (e.g. July month/week aggregate in DEVELOPMENT gives +118R/1.581; Validation +139/1.818; Sept holdout +66/1.617). Denominators and classifications match as documented.

## Claim-by-claim audit
| Claim | Status | Evidence/Notes |
|---|---|---|
| Row counts/variant/split decomposition | **REPRODUCIBLE** | Verified from trade CSV against Phase 6 manifest. |
| V4 gross R/PF by split | **REPRODUCIBLE (descriptive)** | Computed from `gross_R`, `ambiguous`, `censored`. Matches reported figures. |
| V3 proxy gross R | **REPRODUCIBLE but structurally limited** | Only 15 decisive trades/month and 2 in week; 296-547 ambiguous per split. Expectancy -1R due to many same-bar ambiguous paths. Not adequate for paired inference. |
| Paired comparison records as proof of edge | **NOT SUPPORTABLE** | Paired rows are comparison records; in CSV they show 0 gross R and are key-dependent (identity not source-authenticated). Cannot prove source-identical signals. |
| Net-after-costs performance | **NOT_REPRODUCIBLE_FROM_CURRENT_EVIDENCE** | Costs (commission/spread/swap/slippage) absent from decisive outcomes; CSV spread units not resolved to price-cost conversion. Marked `NOT_TESTED`/missing. |
| Executable fill semantics | **NOT_EVIDENCED** | Theoretical trigger-bar extreme fills (`OPTIMISTIC_TRIGGER_BAR_LOW_HIGH_NOT_EXECUTABLE`), same-bar SL+TP ambiguity, SL-first conventions in some implementations noted; no tick/limit/market execution validation. |
| September as confirmatory holdout | **NOT_VALIDATED (diagnostic only)** | Predeclared but dataset fails hash verification (`declared` vs `actual` mismatch), session calendar applicability `UNVERIFIED`, gaps present. Marked `BLOCKED / NOT_VALIDATED`. No parameter tuning observed, but integrity fails. |
| Statistical significance/CI implying edge | **NOT SUPPORTABLE AS PROOF** | Bootstrap CIs reported are conditional on assumptions (data quality, fills, costs); cannot repair missing source identity or prove executable edge. |
| Canonical SP2L geometry/P-Gap/AB=CD | **UNRESOLVED** | Source identity/geometry remain unresolved per prior phases; performance not proof of canonical rules. |

## Discrepancies / notes
- Baseline proxy has extremely high ambiguous rate (same-bar stop/TP/trailing paths) making paired inference underpowered (15 decisive/month). This is a known model limitation.
- Paired rows have `gross_R` zero in the recorded comparison structure - they document pairing, not realized PnL deltas in this CSV layout.
- All data runs show `integrity: FAIL` / hash mismatches vs acquisition manifests; session calendar applicability `UNVERIFIED`. No rows interpolated.
- Split boundaries: DEVELOPMENT contains week+month aggregates as labeled in artifacts; audit treats by split as recorded.

## Verdict
- **Statistical reproducibility (descriptive):** Largely reproducible for row counts and gross V4/V3 descriptive stats from recorded artifacts.
- **Statistical proof of edge/executability:** Not supported. Missing costs, unvalidated fills, data integrity issues, inadequate baseline sample, and unresolved signal identity block inference.
- **Required verdicts unchanged:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`. Statistical reproducibility is not source authentication and not proof of live-trading edge.

## Next actionable blocker
1. **Data provenance**: Reconcile immutable M1 files with acquisition manifests; resolve session calendar applicability.
2. **Execution model**: Establish executable fill semantics (tick/limit/market) and conservative broker costs (spread/commission/swap/slippage); recompute net-after-costs.
3. **Baseline adequacy**: Improve baseline path resolution or obtain adequate decisive baseline sample for paired comparison.
4. **Source identity/geometry**: Resolve canonical signal identity from primary source or accept permanent limitation; do not infer from matching rates.
5. **Untouched holdout**: After fixes, reserve new untouched holdout (September currently blocked by integrity).
