# SP2L Strategy A — Management Research Checkpoint
**Checkpoint date:** 2026-10-27  
**Purpose:** Resume the management comparison and data-provenance audit tomorrow.  
**Research branch:** `research/rr2-trail4-usd-activation-matrix-20261027`  
**Local worktree reported by user:** `D:\Mirzaei\Private\1\xauusd-strategy-a-rr2-trail4-usd-activation-matrix-20261027`

## Current state
- This checkpoint records research status only. It does not authorize a live-runner change, canonical rule, or production decision.
- No live settings or runner were changed as part of this session.
- The historical management comparison used XAUUSD.ecn M1 data from 2026-08-21 through 2026-09-18 (28,815 bars; 553 candidate signals).
- Source CSV previously identified: `D:\Mirzaei\Private\1\xauusd-strategy-a\data\mt5-acquisition\xauusd_ecn_m1_2026-08-21_2026-09-18.csv`
- Reported SHA256: `09FB33790E46539DF7EA072D0796A84F1136B242E32E28B365CCD2C604DD8CAE`

## Compared management scenarios
- RUNNER: `scenario=RUNNER`, `management_mode=RUNNER`, `activation_R=2.5`, `trail_distance_R=3.0`.
- BE: `scenario=BE_0.5R_LOCK_0.05`, `activation_R=0.5`, `lock_price=0.05`.
- Fairness check: 553/553 shared signals; no entry-price, initial-SL, or initial-risk-price differences; no duplicate signals.
- RUNNER: 551 decisive closed, 2 open/unresolved; gross $681.01; estimated spread cost $121.87; commission $27.55; estimated net $531.59.
- BE: 548 decisive closed; 5 ambiguous SL-and-TP-same-bar cases; gross $521.49; estimated spread cost $121.30; commission $27.40; estimated net $372.79.
- Estimated net difference: RUNNER +$158.80 for this sample only.
- Costs used a spread proxy from M1 data and $0.05 commission per completed trade. Swap, slippage, latency, and tick-level intrabar execution were not modeled. Ambiguous/open cases were not resolved as decisive closed trades. These are model estimates, not live-profit claims.

## Stability warning
- Weekly net: RUNNER was positive in 3/5 weeks; BE was positive in 5/5 weeks.
- Omitting week starting 2026-08-31 changes the comparison: RUNNER remainder $172.37 vs BE $282.47 (BE +$110.10).
- RUNNER's three strongest days contributed about $353.96, around 66.6% of its total estimated net.
- Trade-close sequence drawdown estimates: RUNNER $123.53; BE $33.66. These are not time-aware portfolio drawdowns for overlapping positions.
- Therefore RUNNER's higher cumulative estimated net is not sufficient evidence of robust superiority. No canonical selection is made.

## July data provenance investigation
- 33 copies of `xauusd-ecn-m1-2026-07.csv` were found across local worktrees.
- Three whole-file SHA256 prefixes were observed; row count and first/last timestamps match across versions.
- A per-column SHA256 comparison was then run for three representative versions. All eight column hashes matched across all three files:
  - timestamp `B87E40EC3C88`
  - open `4FF80DABAF2D`
  - high `237285B0B40E`
  - low `06AE1C20D547`
  - close `D8035EF5FCAF`
  - tick_volume `DF9D6F933D58`
  - spread `6692C70E7EB6`
  - real_volume `796DAA86AE27`
- Each representative version contained 31,483 data rows, with timestamps from `2026-07-01T01:00:00Z` to `2026-07-31T23:57:00Z`.
- This confirms matching values for the compared columns in the three representative versions, but does not yet explain the whole-file hash differences or prove that July has never influenced prior research/selection.

## Next steps — do not skip
1. Audit previous reports, scripts, manifests, and experiment notes to determine whether July data was used for parameter selection, rule decisions, or exploratory comparison.
2. Explain the three whole-file hash variants (e.g., raw-byte/line-ending/encoding differences) without modifying any source copy.
3. Check data quality and coverage for July, including gaps, duplicates, spread behavior, and timestamp semantics.
4. Only after provenance and configuration freeze, decide whether July is a valid time-separated evaluation set. Until then, label it **candidate historical out-of-period data**, not a confirmed Fresh Holdout.
5. Keep the live runner and all live parameters unchanged. Do not call the management comparison a validated edge.

## Governance
Follow: SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.

Source meaning outranks backtest performance. Unresolved geometry remains unresolved. No invented P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules. AI may assist research, engineering, validation, documentation, and analytics, but must not autonomously define canonical rules or production BUY/SELL decisions.
