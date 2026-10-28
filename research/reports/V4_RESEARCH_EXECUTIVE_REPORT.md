# V4 Research Executive Report

- **TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z` (nominal identifier; actual replay `2026-10-28T06:48:03.585069+00:00`)
- **Independent worktree:** `D:\Mirzaei\Private\1\xauusd-strategy-v4-research-20261028`
- **Branch / base HEAD:** `research/strategy-v4-xauusd-20261028` / `dac76b09da01f022d745f51328ee703f6fb59851`
- **Decision:** **NOT_PROVEN** — diagnostic OHLC replay, not executable or costed.
- **Generated:** `2026-10-28T07:06:23.005336+00:00`
- **Design freeze evidence:** design artifact filesystem timestamp `2026-10-28T06:45:54.634758+00:00` precedes the replay timestamp; the ID's `120000Z` segment is nominal only.

## Work completed

Read-only source/runtime/history review of the specified RR2/TRAIL4 checkout and captured snapshot; rule register; offline synthetic fixture tests; one frozen V4 TP=1R/no-trailing hypothesis compared with a V3 RR2/TRAIL4 research proxy on the same bar data; coverage, validation and holdout diagnostics. No runner or MT5 process was stopped, restarted, attached to or modified; no live API query or order was issued.

- `python -m pytest -q tests/test_v4_research_fixtures.py`: **13 passed, 0 failed**, exit 0.
- Fixture inventory: **22 rows**: 16 PASS, 0 FAIL and 6 rows explicitly describing behavior not executed or integration-blocked. This is not a 22-test passing suite.
- Backtest matrix: **8 rows**, status counts `{'PASS': 0, 'FAIL': 0, 'BLOCKED': 8, 'UNRESOLVED': 0, 'NOT_TESTED': 0}`; all paired rows are blocked for inference.
- Coverage CSV: 9 entries (7 top-level groups BLOCKED, holdout BLOCKED, MT5 history UNRESOLVED).
- XLSX validated: 4 sheets; Backtest Matrix 8 rows, Trade Results 4,027 data rows, Dataset Coverage 4 rows, Requirements 9 rows (7 top-level groups plus holdout and MT5 history).

## Gross diagnostic comparison (not evidence of edge)

| Period | V3 decisive / ambiguous | V4 decisive / ambiguous / censored | V4 gross net R / PF |
|---|---:|---:|---:|
| development_week_2026-07-06_12 | 2 / 106 | 100 / 0 / 1 | 24.00 / 1.632 |
| development_month_2026-07 | 15 / 441 | 424 / 2 / 2 | 94.00 / 1.570 |
| validation_month_2026-08 | 15 / 517 | 479 / 6 / 6 | 139.00 / 1.818 |
| fresh_holdout_available_2026-09 | 15 / 296 | 280 / 6 / 4 | 66.00 / 1.617 |

All July/August/September CSV hashes differ from the acquisition-manifest hashes; historical session-calendar applicability is unverified. Trigger-extreme OHLC entries are theoretical, costs are absent, and baseline decisive counts are only 2 in the week and 15 per month amid hundreds of ambiguous paths. These metrics and bootstrap intervals are diagnostics only. September was run once on a predeclared split but is **BLOCKED / NOT_VALIDATED**, not a valid confirmatory holdout.

## MT5 and runner findings

Runner and helper disk hashes match the supplied observations. The captured history log includes `history_orders_get(ticket)` invalid-parameter errors for all six named IDs; later lifecycle progress does not identify their cause. Root cause, loaded in-memory helper version and unsuppressed API call count remain **UNRESOLVED**. No live-terminal reproduction was attempted.

## Required next evidence

1. Reconcile immutable M1 files with acquisition manifests and historical session calendars.
2. Establish executable tick/fill semantics and conservative broker costs.
3. Resolve canonical SP2L/P-Gap/AB=CD rules from authoritative sources; current values remain research hypotheses/code observations.
4. Improve baseline path resolution and sample adequacy; do not infer from ambiguous OHLC outcomes.
5. After any tuning, reserve a new untouched holdout.

## Key artifacts

- [Rule register](../source_audit/V4_SOURCE_RULE_REGISTER.csv)
- [Fixture results](../source_audit/V4_SYNTHETIC_FIXTURE_RESULTS.csv)
- [Runtime/history audit](../runtime_audit/V4_RUNTIME_AND_HISTORY_AUDIT.md)
- [Baseline manifest](../baseline/V4_BASELINE_MANIFEST.json)
- [Design freeze](../design/V4_DESIGN_FREEZE.md)
- [Backtest matrix CSV](../backtests/V4_BACKTEST_MATRIX.csv) and [XLSX](../matrix/V4_BACKTEST_MATRIX.xlsx)
- [Coverage matrix](../matrix/V4_REQUIREMENT_COVERAGE_MATRIX.csv)
- [Statistical validation](../validation/V4_STATISTICAL_VALIDATION.md)
- [Holdout diagnostic](../holdout/V4_HOLDOUT_REPORT.md)
- [Blockers](../validation/V4_BLOCKERS_AND_UNRESOLVED.md)
- [Reproducibility manifest](../manifests/V4_REPRODUCIBILITY_MANIFEST.json)
- [ChatGPT handoff](FREEBUFF_HANDOFF_TO_CHATGPT.txt)
