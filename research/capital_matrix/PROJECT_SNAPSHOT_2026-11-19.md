# Official Project Snapshot — SP2L Capital Management Study

**Snapshot date:** 2026-11-19  
**Status:** Research foundation implemented; full historical simulation not yet started.  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Branch:** `research/capital-management-matrix-20261119`  
**Draft PR:** [#422 — Capital management matrix foundation](https://github.com/wareshgold/xauusd-strategy-a/pull/422)  
**Scope:** Research only. This snapshot records the agreed plan and verified progress; it is not a performance result or trading recommendation.

## 1. Objective

Compare money-management and exit-management alternatives on the same frozen SP2L entry population. Select methods only after chronological validation, realistic execution-cost modelling, robustness checks, and a locked Fresh Holdout. Do not infer a winning method from the unit tests or from incomplete historical data.

## 2. Frozen experiment design

- Initial equity: **USD 1,000**.
- Risk fractions per trade: **0.25%, 0.50%, 0.75%, 1.00%**.
- Sizing modes:
  - **COMPOUND:** current equity × risk fraction.
  - **FIXED_BASE:** initial equity × risk fraction.
- Fixed TP targets: **1R, 1.5R, 2R, 3R, 4R**.
- Dual independent-position TP pairs: **1R/2R, 1R/3R, 1R/4R, 1.5R/3R, 2R/4R**.
- Dual legs each receive 50% of the aggregate risk budget; never allocate the full budget to both legs.
- Exact historical Runner benchmark: fixed 0.01 lot, TP 4R, trailing activation USD 0.40, trailing distance USD 0.40, SL anchor `SPIKE_CANDLE_EXTREME_RESEARCH`, maximum initial SL distance 10, pending-limit research mode.
- Risk-normalized Runner: same exit profile, tested at four risk fractions and both sizing modes.
- Primary matrix: **89 configurations** = 40 fixed-TP + 40 dual-TP + 1 exact fixed-volume Runner + 8 risk-normalized Runner.
- Separate diagnostic: fixed 0.01 + 0.01 dual volume; excluded from the 89 primary configurations and marked infeasible whenever aggregate risk exceeds the budget.

## 3. Sizing and execution invariants

- Calculate risk from actual broker contract metadata: tick size, tick value, stop distance, account currency, and volume constraints.
- Round volume down to the broker volume step. Never round up to force a trade.
- If minimum volume would breach the risk budget, mark the leg/configuration infeasible.
- Record actual risk after volume-step rounding; it may be lower than the requested budget.
- Apply spread, commission, swap, slippage, concurrency and broker execution assumptions consistently to every configuration.
- Avoid lookahead. Use identical entries, initial stops, chronology and cost assumptions across comparable configurations.
- Tick data is preferred to resolve intrabar trailing and SL/TP ordering. If only OHLC is available, use a declared conservative ambiguity policy and label the evidence weaker.

## 4. Chronological evaluation protocol

Use chronological partitions:
- Development: 60%.
- Validation: 20%.
- Fresh Holdout: 20%, locked until rules and configuration selection are frozen.

Do not tune against Fresh Holdout. Record immutable input, source, configuration and output hashes (SHA-256), run IDs and reproducibility metadata.

## 5. Required measurements

At minimum report gross/net P&L, profit factor, win rate, average win/loss, payoff ratio, expectancy in USD and R, average R, maximum drawdown, recovery factor, Sharpe/Sortino, longest losing streak, MAE/MFE, giveback, commissions, swap, slippage, exposure, trade count and risk-of-ruin assumptions.

Robustness work must include cost/spread/slippage stress, market regimes, rolling windows, concurrent aggregate risk, data-gap handling, and bootstrap/Monte Carlo with explicit assumptions.

Produce three separate rankings only after eligibility gates:
- Balanced.
- Capital Protection.
- Growth.

Balanced score weights currently specified: expectancy 25%, profit factor 20%, drawdown 25%, recovery 15%, stability 15%. Define and enforce eligibility gates before scoring; no single high-return metric can override unacceptable drawdown or instability.

## 6. Verified implementation and test status

Implemented on the research branch:
- Deterministic enumeration and stable IDs for the 89 primary configurations.
- Compound and fixed-base risk budgets.
- Contract-aware sizing and downward volume-step rounding.
- Equal aggregate-risk split across dual legs.
- Explicit infeasibility below broker minimum volume.
- Exact fixed-0.01 Runner reference representation.
- Focused offline unit tests and a dedicated GitHub Actions workflow.

**Latest user-run verification:** 8 unit tests passed; output was `Ran 8 tests ... OK`, `TEST_EXIT_CODE=0`.

The dual-leg sizing test intentionally expects actual risk below the requested aggregate budget when broker volume granularity requires rounding down. The unused remainder is correct risk-safe behavior, not a sizing defect.

**Important boundary:** these are unit tests of the foundation only. They do not validate historical trading performance. CI status is not asserted by this snapshot.

## 7. Historical evidence blockers

The full replay is blocked until the following are located, validated and SHA-pinned:
1. Preserved three-month M1 CSV.GZ with its audited SHA-256.
2. Frozen V3.1 entry CSV and manifest generated from that exact source.
3. Tick data sufficient for intrabar trailing/SL/TP ordering and cost calibration, or an explicitly approved lower-evidence OHLC policy.
4. Actual broker contract metadata and execution-cost assumptions.
5. SHA-256 values for every input, source file, configuration and output.

A pre-existing acquisition/population workflow was found on branch `research/three-month-management-matrix-20261109`, including `docs/SP2L_THREE_MONTH_MT5_EXPORT.md` and `docs/SP2L_V31_THREE_MONTH_ENTRY_POPULATION.md`. That documentation declares the expected M1 CSV.GZ SHA-256 as:

`daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402`

It declares 89,866 bars from `2026-08-10T01:00:00Z` through `2026-11-09T07:43:00Z`, with 66 timestamp gaps. These are documented source claims; the raw gzip bytes were not found in the inspected GitHub tree or Library search, so the hash has not yet been independently recomputed in this phase. Do not treat the source as available until the exact file is found and hashed.

Older monthly files and the 30-day M1/462-entry Discovery population are not substitutes for the three-month source. Prior monthly manifests include incomplete counts and unverified historical session-calendar applicability. Do not concatenate, relabel, interpolate or silently repair those files.

## 8. Next work — current position

1. **Completed:** verify the current branch/PR head and inspect the matrix implementation, tests and workflow as committed.
2. **Completed as a read-only repository/library audit:** locate the prior three-month acquisition/population documentation and record its declared source identity. The exact raw M1 gzip, frozen three-month entry CSV/manifest, Tick ALL corpus and broker evidence remain unlocated/unverified.
3. **Current next action:** search the Factory PC for the exact M1 SHA above and the three-month frozen-entry manifest; hash candidates before use. Record path, file size, date coverage, row/tick counts, gaps and SHA-256. Stop if the evidence cannot be bound to one frozen population.
4. Specify and test the offline replay contract: entry/initial-SL semantics, costs, position sizing, concurrent risk, trailing event ordering, intrabar ambiguity and gap policy.
5. Implement replay and metrics only after evidence and semantics are frozen; then test on fixtures and run Development/Validation.
6. Freeze candidate rules before opening Fresh Holdout; report all three rankings and robustness results with reproducible manifests.
7. Present findings for user review. No automatic promotion or canonical decision.

Supporting audit: `research/capital_matrix/EVIDENCE_INVENTORY_2026-11-19.md`.

## 9. Safety and non-goals

- Research-only; no live configuration changes.
- No MetaTrader5 imports, terminal connections, order APIs or live trade management.
- No modifications to the V3.1 forward Runner or its dashboard.
- No production BUY/SELL decisions and no canonical strategy decisions.
- No automatic promotion. Do not merge PR #422 without explicit user approval.
- Preserve existing local changes and user data; do not perform destructive Git or filesystem operations.

**Resume point:** read-only local search for the declared three-month M1 source SHA and frozen-entry artifacts. No MT5 connection or new acquisition is authorized by this snapshot.
