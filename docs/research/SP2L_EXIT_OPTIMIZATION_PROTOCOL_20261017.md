# SP2L Exit Optimization Protocol — Research Only
Date: 2026-10-17
Base: `research/factory-candidate-lab-20261010` at `5c9f6fe2167885d16a1367b54a8c49449d907274`
Status: protocol proposal; no strategy, execution, or canonical geometry changed.

## Objective

Build a reproducible research path to compare exit-management and optional trade-management variants for the user's currently tested SP2L / Strategy A implementation. The aim is not to maximize one historical backtest number; it is to determine whether any improvement is robust, statistically credible, operationally reproducible, and suitable for a separately approved forward test.

The current RR2/TRAIL4 forward implementation is the baseline to audit, not an assumption that it is optimal. Keep the baseline immutable and report all candidates against it.

## Hard boundaries

- Research and backtests must never place live orders, send production BUY/SELL decisions, or mutate MT5 configuration.
- Do not change source-defined entry/stop geometry, P-Gap, AB=CD anchors/tolerance, fill semantics, or pending-order semantics as part of exit optimization while any are unresolved.
- A backtest result cannot define canonical strategy rules. Label new filters and management methods as experimental hypotheses.
- Never tune on the fresh holdout. Keep development, validation, and fresh holdout data separated by time, with a recorded manifest and hashes.
- Preserve existing forward logs, journals, snapshots, local modifications, and untracked evidence. No cleanup/overwrite.
- Every candidate must be deterministic and replayable from frozen data, code commit, configuration, and manifest.

## Stage 0 — Freeze and audit the baseline

Before any parameter sweep:
1. Identify the exact code commit, config, symbol metadata, pip/point conversion, data source/timezone, spread/commission/swap assumptions, and forward-test date range.
2. Reconcile backtest trade/event semantics with the RR2/TRAIL4 runner: signal, pending order, actual fill, SL/TP modification, trailing update, partial/closed deal, expiry/cancellation, and final realized P&L.
3. Reproduce the baseline on the same frozen dataset. If it cannot be reproduced, stop optimization and resolve the discrepancy first.
4. Preserve baseline event logs and output hashes. Mark gaps and uncertain semantics explicitly.

## Stage 1 — Controlled exit-management matrix

Do not begin with a giant Cartesian product. Run a small, staged matrix, always including the untouched baseline.

### A. Baseline and fixed-target controls
- Current RR2/TRAIL4 configuration, exactly as implemented.
- RR1 and RR2 fixed-target controls only if the existing engine can represent them without changing entry/SL rules.
- No-trailing counterfactual as a diagnostic, not a presumed improvement.

### B. Trailing activation and distance
Treat activation threshold and trailing distance as separate parameters. Enumerate values only after confirming the unit contract from code and symbol metadata. For XAUUSD in the current Otet environment, the documented convention is 1 MT5 point = 0.01 price units; verify against the exact symbol metadata at each run rather than assuming this is portable.
- Activation threshold: use a coarse grid expressed in explicitly named units, including the baseline's exact behavior.
- Trail distance: use a separate coarse grid, including the baseline's exact distance.
- Trail step/update cadence: test only if the implementation has a well-defined, reproducible step/cadence parameter.
- Record whether the trailing update was accepted by MT5 simulation/engine, and distinguish desired SL from actually applied SL.
- Include no-trail and fixed-target controls to quantify the effect of trailing.

Do not preselect a “best” number of pips. Grid values must be declared in a versioned config before execution and translated unambiguously into price units.

### C. Exit/management hypotheses (one family at a time)
- Fixed RR target variants, if consistent with the currently implemented entry and SL.
- Trailing activation × trailing distance interactions, using staged/factorial screening rather than an unbounded sweep.
- Time-based exit / maximum holding time, as a clearly experimental hypothesis.
- Session/time-of-day segmentation as analysis first; only test as a filter after the data coverage and timezone contract are validated.
- Volatility regime / ATR-based management as a separate hypothesis; never silently replace the existing SL anchor.
- M15 MA50 filter (source note C05) only as an optional experimental filter after its exact calculation, input price, bar-close timing, and missing-data behavior are specified. Compare with no-filter control and report trade-count loss as well as performance.
- Spread/slippage stress and delayed execution scenarios as execution robustness tests, not profit-enhancing filters.

Entry geometry, P-Gap formula, AB=CD anchors/tolerance, entry touch/penetration/close semantics, and stop anchor remain out of scope until source resolution freezes them.

## Stage 2 — Metrics and decision criteria

Report per candidate, plus distributions by direction/session/regime where sample sizes permit:
- Number of trades and excluded/ambiguous cases.
- Net expectancy in R/trade, total net R, profit factor, win rate, average win/loss, and exposure.
- Maximum drawdown in R and currency, drawdown duration, losing streak, and tail loss.
- MAE/MFE distributions and captured-MFE ratio where data supports it.
- Sensitivity to spread, commission, slippage, and execution delay.
- Bootstrap/confidence intervals for expectancy and profit factor where statistically appropriate.
- Performance by chronological subperiod; trade count and stability across subperiods.
- Candidate rank must not be based on win rate alone or the single best in-sample return.

Reject candidates that depend on tiny samples, one narrow date window, one isolated parameter value, unrealistic fills, or a fragile performance cliff. Prefer a broad stable region with modest performance over a sharp isolated optimum.

## Stage 3 — Validation gates

1. Development window: discover plausible ranges; record all tested variants, including failures.
2. Untouched validation window: test the frozen shortlist once. No parameter adjustment based on this result without returning to development and allocating a new validation window.
3. Robustness/stability: nearby parameter values, chronological folds, both directions, session/regime slices, costs and slippage stress.
4. Fresh holdout: only after code/config/selection rule are frozen and hashed. One registered evaluation; no repeated peeking.
5. Forward-test candidate: separately approved after all prior gates pass. Shadow/paper validation first where possible. Never automatically deploy the historical winner.

A pass threshold must be written before evaluating the validation/holdout results. If the sample is insufficient or intervals include no edge, report INCONCLUSIVE rather than PASS.

## Stage 4 — Factory implementation requirements

Implement a research-only experiment runner only after Stage 0 audit:
- Versioned matrix config; no hidden defaults.
- Immutable dataset manifest, code/config hashes, deterministic run IDs and per-run artifacts.
- One run per config; reproducibility check by rerunning a sample and comparing outputs.
- Strict train/validation/holdout time boundaries and leak checks.
- Isolated experiment journals; never append synthetic/test events to live runtime journals.
- Explicit baseline-vs-candidate report and machine-readable results.
- Production authority stays LOCKED; no order placement or Telegram trade claims from the research runner.
- Fail closed if data integrity, unresolved execution semantics, or manifest checks fail.

## Separate research lane: external PythonTraderBot SP2L implementation

Requested source: https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/Meta.py

Keep this implementation isolated from the current RR2/TRAIL4 strategy. First audit the source and its companion bot/backtest notebooks; do not copy it into the production runner or assume that same class/method names mean identical strategy rules.

Initial code-review observations from Meta.py:
- It directly imports and uses MetaTrader5 and includes order-placement/modification methods, so it is execution code, not a self-contained historical backtest specification.
- It has an optional execution-based TP path that recalculates TP after a real fill; this needs a deterministic historical-fill model before any meaningful backtest comparison.
- It caches a TP for a second entry via a magic-number condition; inspect the complete companion call path before interpreting its intended lifecycle.
- Pending-order placement, fill mode, quote source, spread, slippage, and broker constraints can affect results and need explicit modeling.
- Review companion `SP2L_Bot.py`, `SP2L_Advanced_Bot.py`, optimized bot, and backtest notebooks before concluding how entry, SL, trailing, and second-entry behavior are intended.

This is a code-review queue, not a verdict on the external strategy's profitability or correctness. Preserve attribution and license terms. Any external implementation must get its own frozen spec, fixtures, backtest adapter, and validation/holdout; never mix its results into the current strategy's sample.

## Immediate next action

Audit the current RR2/TRAIL4 runner/backtest implementation and available frozen XAUUSD data to establish the Stage 0 baseline contract. Do not launch parameter optimization until reproducibility, trade semantics, units, and data manifest are verified.
