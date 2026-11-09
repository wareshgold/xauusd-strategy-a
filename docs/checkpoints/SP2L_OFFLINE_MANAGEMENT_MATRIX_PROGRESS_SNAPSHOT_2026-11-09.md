# SP2L Offline Management Matrix — Progress Snapshot
Date: 2026-11-09
Status: PRE-IMPLEMENTATION SNAPSHOT — NO BACKTEST EXECUTED
Research-only; non-canonical; no production or forward-runner changes.

## Purpose
Prepare an isolated, fully offline management-matrix runner over one immutable V3 entry population. Add and test STEP_LOCK_NO_TP as a distinct management mode. Do not connect to MT5, inspect or change the live runner/dashboard, rebuild entries, or modify canonical entry logic.

## User-approved Step-Lock definition
- Milestones are measured in each trade's initial risk R.
- At +1R favorable excursion, move stop to entry (0R).
- At +2R, move stop to +1R.
- At +3R, move stop to +2R.
- Continue indefinitely: at +nR, stop locks +(n-1)R.
- No final TP.
- BUY and SELL must be symmetric.
- Stop updates derived from a completed M1 bar become active only on the next bar.
- The entry bar is excluded from exit replay.
- M1 gaps while open remain ambiguous; never fill gaps.
- If a bar touches both the currently active stop and a new milestone, OHLC cannot determine ordering; mark ambiguous rather than infer a favorable ordering.
- If one bar crosses multiple milestones, the update must be deterministic and conservative; exact rule must be specified/tested before the matrix run.

## Final management families to compare
A. FIXED_RR: fixed final TP, no trailing.
B. BREAK_EVEN: move SL to entry after configurable favorable R threshold, with optional fixed TP.
C. FIXED_DISTANCE_TRAILING: price-dollar activation × distance grid; separate from R trailing.
D. STEP_LOCK_NO_TP: user-approved rule above.
E. STEP_LOCK_WITH_TP: optional research comparator; same step-lock plus final TP.
F. BREAK_EVEN_TRAILING: break-even stage then R-based trailing.
G. FIXED_TP_TRAILING: fixed TP plus trailing; first exit condition wins subject to ambiguity rules.
H. NO_TARGET: original SL only, no TP and no trailing.

Fixed-distance trailing Discovery grid (price dollars):
- Activation: [0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6]
- Distance: [0.2, 0.3, 0.4, 0.5, 0.7, 1, 1.5, 2, 3, 4, 6]
- 110 combinations + separate no-trail control. Activation=0 semantics must be explicitly implemented as first eligible completed bar; do not pass zero to APIs that reject it or silently replace it.

## Frozen 30-day input (verified previously by user)
M1 CSV:
D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv
SHA256: B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285
Bars: 29,919
Coverage: 2026-09-24 07:57 UTC through 2026-10-23 23:57 UTC
Gaps: 21; missing minute slots: 12,802; largest gap: 2,942 minutes.
No gaps may be filled. A trade open across a gap is ambiguous.

Frozen entry CSV:
D:\Mirzaei\Private\1\xauusd-strategy-a-monthly-matrix-audit-worktree-20261024\artifacts\monthly_ohlc_activated_sensitivity_v3_20261024_162634_105\a_trail_0_40_activated_proxy_v3_trades.csv
SHA256: 39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1
Rows: 462
Schema:
strategy,variant,direction,setup_time_utc,entry_time_utc,entry_proxy,sl_initial,target,risk_price,exit_time_utc,exit_price,exit_reason,status,r_multiple
The prior user-side PowerShell verification reported EXISTS=True, ROWS=462 and exact SHA above.
Use this as a 30-day frozen entry population only. Do not call it a three-month population.

## Repository audit performed (GitHub read-only inspection)
Repository: wareshgold/xauusd-strategy-a
Base branch inspected: research/three-month-management-matrix-20261109
Base commit: ad8dcf9fbad4f3e83bdb4504ec0bea0097e32a67
Isolated work branch created: research/offline-step-lock-matrix-20261109
Branch starts at the exact base commit above. No files have yet been changed on this branch.

Inspected source:
- src/strategy_factory/v3_management_engine.py (blob 933d21c58908c3afce91fb5d37f10fb0396ab994)
- tests/test_v3_management_engine.py (blob 753328f8f81b3592bdd7f388fdc384a22dcb06f1)
- src/strategy_factory/frozen_entry_population.py (blob 7c892e537140582529ac882091ab697ef0f35c03)
- src/strategy_factory/v3_exit_engine.py (blob 75b65f3dbb28cadd7e13e8611b3c3b6e002868e9)
- scripts/run_sp2l_v3_xauusd_discovery_matrix.py

Findings:
1. v3_management_engine is pure replay code and supports FIXED_RR, NO_TARGET, BREAK_EVEN, TRAILING_R, BREAK_EVEN_TRAILING and TIME_EXIT. It does not support Step-Lock.
2. The existing management replay applies completed-bar stop updates to the next bar, excludes the entry bar, and marks M1 gaps ambiguous.
3. The existing V3 discovery script imports MetaTrader5 and calls mt5.initialize() even when an M1 artifact is supplied. It is NOT acceptable for the required fully offline runner.
4. frozen_entry_population loader verifies CSV SHA/schema, UTC timestamps, alignment, entry timestamps and positive risk, but needs an additional strict integrity gate: risk_price must equal abs(entry_proxy - sl_initial) within an explicit numeric tolerance, and BUY/SELL stop direction must be valid. Report failures; never repair or rewrite the frozen source.
5. Existing summary's "net_profit_usd" is gross realized P/L under current assumptions; spread, commission and slippage are not modeled. Label output gross USD, not net broker profit.
6. A separate three-month frozen population is not available from the 462-row 30-day CSV. A documented three-month M1 source was 89,866 bars, 2026-08-10T01:00Z through 2026-11-09T07:43Z, with 66 timestamp gaps; a separate audited three-month entry freeze is required before making three-month claims.

## Implementation plan on isolated branch
1. Extend v3_management_engine with STEP_LOCK_NO_TP and (if included) STEP_LOCK_WITH_TP; do not touch entry geometry or MT5/runner code.
2. Define conservative multi-milestone OHLC semantics. If a bar touches the current SL and any milestone, mark AMBIGUOUS. If multiple new milestones are crossed in one bar without touching current SL, lock the highest fully crossed milestone only after the bar closes; new stop becomes active next bar. Validate BUY/SELL symmetry.
3. Add unit tests: +1R=>0R, +2R=>+1R, +3R=>+2R, multi-level jump, same-bar stop/milestone ambiguity, gap ambiguity, entry-bar exclusion, SELL symmetry, no final TP, stop monotonicity, malformed risk/SL rejection.
4. Add an offline runner that has no MetaTrader5 import or API references; requires explicit M1 path/SHA, entry CSV path/SHA, symbol, point, contract size, volume and new output directory. Validate M1 and frozen population; verify exact 462 rows and known SHA for this 30-day run; no signal generation or entry rebuilding.
5. Implement fixed-distance grid in price dollars with explicit conversion using declared point, including a deliberate zero-activation mode. Do not silently default point/contract/volume.
6. Emit immutable timestamped per-trade CSV, summary CSV, manifest JSON and SHA256SUMS; exclusive-create outputs/no overwrite.
7. Run synthetic tests first. Then run actual frozen population only after all tests pass and input paths/SHA checks succeed. Report any unavailable local artifacts as a blocker; do not claim execution based on remote code review.

## Safety boundaries
- No MT5 import, initialize, shutdown, symbol selection, order/position/deal API.
- No runner/dashboard process access or changes.
- No modification of existing evidence or local dirty worktrees.
- No canonical or production promotion.
- No Fresh Holdout use for tuning. Freeze discovery candidates before any separate holdout evaluation.

## ## Implementation progress after the initial snapshot
- Added `src/strategy_factory/v3_step_lock_engine.py`: independent no-TP Step-Lock replay; strict frozen risk/SL validation (1e-6 price tolerance); BUY/SELL symmetry; gap and same-bar ambiguity handling; completed-bar updates active on next bar.
- Added `tests/test_v3_step_lock_engine.py`: seven synthetic unit tests covering progression, multi-milestone bars, same-bar ambiguity, SELL symmetry, entry-bar exclusion/no TP, gap ambiguity, and invalid risk/stop.
- Added `scripts/run_sp2l_v3_offline_step_lock.py`: standalone offline runner bound to the known 30-day M1 SHA and 462-row entry SHA; requires explicit point/contract-size/volume; rejects output overwrite; checks row count, coverage, gap count and frozen entry risk; writes trades, summary, manifest and SHA256SUMS. No MetaTrader5 import or broker API.
- Added fail-fast checks for exact M1 row count (29,919), 21 gaps, first/last UTC timestamps, 462 frozen entries and both expected SHA-256 values.
- Core logic sanity simulation was run in an isolated Python harness for six cases: step progression, multi-milestone bar, same-bar ambiguity, SELL symmetry, entry-bar exclusion, and gap ambiguity. All six produced the expected outcomes. This was not a full pytest run and does not validate the repository files or local data artifacts.
- GitHub Actions checks were not reported for the PR head; repository pytest suite has NOT been run.
- Opened draft PR #411 for isolated review/CI only: https://github.com/wareshgold/xauusd-strategy-a/pull/411. It targets `research/three-month-management-matrix-20261109`; it is not merged.

## Current exact checkpoint
- Work branch: `research/offline-step-lock-matrix-20261109`
- Latest branch HEAD: `17842c6e85d3de7c3699d0b1b4c7ab51478f34a7`
- Parent/base commit: `ad8dcf9fbad4f3e83bdb4504ec0bea0097e32a67`
- Draft PR: #411, open, not merged.
- Snapshot document is stored at this path in the work branch.
- Implementation status: Step-Lock engine, tests, and Step-Lock-only offline runner added; awaiting repository test execution and code review.
- Not completed: full multi-family matrix runner, local data-path verification, actual 462-trade replay, actual matrix.
- Backtest executed: NO.
