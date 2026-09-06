# Phase 13 — Post-Entry Recovery Event Audit

## Objective
Test one pre-defined, live-observable post-entry event rather than mining retrospective path features or selecting a fixed exit horizon.

## Event definition
For every canonical baseline trade, using bars `entryIndex+1..entryIndex+20`:

1. Find the first bar where cumulative MAE reaches the existing fixed state boundary `0.50R`.
2. Starting strictly after that adverse milestone, find the first candle whose **close returns through the entry price in the trade direction**:
   - BUY: `close >= entry`
   - SELL: `close <= entry`
3. This is `RECOVERY_AFTER_0_5R`.
4. If no MAE >= 0.50R occurs, classify `NO_ADVERSE_0_5R`.
5. If MAE >= 0.50R occurs but no later close recovery occurs inside H20, classify `NO_RECOVERY_H20`.
6. No intrabar order is inferred. Same-bar adverse/recovery cannot qualify because recovery begins strictly after the adverse milestone.

The 0.50R boundary is reused from the already frozen descriptive MAE state bands; no new threshold is searched.

## Population
- Canonical baseline pre-holdout trades only.
- DEV: entryIndex < 6000.
- VAL: 6000 <= entryIndex < 10000.
- Fresh holdout remains locked and is not read.
- Exclude AMBIGUOUS / non-finite outcomes.

## Required diagnostics
- Exact baseline replay/join integrity.
- Overall and DEV/VAL outcome statistics by event state.
- Five fixed chronological 2,000-candle windows, without selecting a best window.
- Event prevalence and recovery timing.
- Exceptional-winner dependence (`R >= 5`) and no-exceptional results.
- Direction × session descriptive breakdown where N permits.

## Decision criteria
This phase is descriptive until a live-observable event shows the same qualitative outcome separation across DEV, VAL, and multiple chronological windows, with no dependence on exceptional winners.

A positive result does **not** authorize a trading rule automatically. A rule candidate would require a separate ex-ante management specification and independent validation.

## Prohibited
- No threshold optimization.
- No best-window selection.
- No fixed-horizon exit selection.
- No fresh holdout access.
- No production detector changes.
- No BUY/SELL generation changes.
