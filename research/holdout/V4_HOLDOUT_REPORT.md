# V4 Fresh Holdout Report — Diagnostic Only

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Predeclared period:** available September 2026 MT5 XAUUSD.ecn M1, from 2026-09-01 up to the dataset's documented last available day 2026-09-17.  
**Result status:** `BLOCKED / NOT_VALIDATED`; **not confirmatory** and **not used for parameter selection**.

The split was declared in `research/design/V4_DESIGN_FREEZE.md` before the replay. The diagnostic did run both frozen baseline proxy and V4 hypothesis on the same bar rows and settings. The input file contains 17,069 rows, from 2026-09-01 01:00 UTC to 2026-09-17 12:01 UTC, with 12 timestamp gaps over 60 seconds and the acquisition manifest labels its audit `AUDITED_FAIL`, expected active bars 17,940 and session-calendar historical applicability `UNVERIFIED`.

- Declared CSV SHA256: `3b7212dc43f844807da120d89e6cbae9f63def4943fefdb003c54d630467cc2b`.
- Actual CSV SHA256: `1bb2dcdc163e13fa08487c5d7a68905325e9be50104a57aedbe0bbde7055f1d4`.
- Hash mismatch: integrity gate `FAIL`; data row is `BLOCKED`.
- Shared diagnostic signal keys: 290; baseline-only: 21; V4-only: 0.
- Baseline proxy: 15 decisive trades, 296 ambiguous outcomes, gross expectancy -1R/decisive trade; insufficient and structurally biased because most same-M1 paths are ambiguous.
- V4 proxy: 280 decisive trades, 6 ambiguous, 4 censored, gross expectancy +0.2357R, gross PF 1.617; day-cluster bootstrap interval for mean daily gross R [2.769, 7.615].
- Costs and actual fill prices are absent; net-after-cost results are `NOT_TESTED`.

These statistics are retained for audit completeness only. The baseline denominator is too small; OHLC entries are theoretical trigger-extreme fills, and manifest/hash integrity fails. Therefore September does not validate an edge and must not be represented as a successful holdout. No settings were changed after this diagnostic. Any future change to rules/parameters requires a new untouched holdout.
