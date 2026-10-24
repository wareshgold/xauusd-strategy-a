# External SP2L Repository — Initial Source Review
Date: 2026-10-17
Source repository: https://github.com/AlirezaSadabadi/PythonTraderBot
Requested entry point: `code/SP2L/Meta.py`
Status: preliminary static review of public files; no code copied, no execution performed, no profitability claim.

## Files inspected

- `code/SP2L/Meta.py`
- `code/SP2L/SP2L_Bot.py`
- `code/SP2L/SP2L_Advanced_Bot.py`
- `code/SP2L/SP2L_Advanced_Bot_Optimized.py`
- `code/SP2L/SP2L2_Advanced_Backtest.ipynb`
- `code/SP2L/SP2L2_Optimized_BackTest.ipynb`
- repository README

## What stands out

### 1. Treat as a separate strategy implementation

The bot variants expose multiple independent choices: spike multiplier, P-Gap points, max SL distance, TP in R, EMA period/filter, trend structure, ADX/range, session windows, spread constraints, ATR, news blackout, and optional second entry. These are hypotheses/configuration options, not proof that the source-defined SP2L rules require those filters. Do not merge these assumptions into the current Strategy A or its forward-test record.

The advanced bot defaults shown in source include M1 data, spike multiplier 1.5, P-Gap 100 points, max SL 1000 points, TP 1R, EMA period 60, and optional trend/range/session filters. The optimized bot adds more controls, including optional alternate SL structure, EMA alignment, ATR, spread, ADX rising, and news filter. Each must be traced to the actual signal and execution code before inclusion in a research spec.

### 2. Units are an important source of false comparisons

Notebook output describes XAUUSD point=0.01, P-Gap 100 points = price distance 1.0, max SL 1000 points = price distance 10.0. This is internally consistent for that stated symbol metadata, but cannot be assumed to match another broker's symbol configuration. Any port must define point, digits, pip convention, contract size, tick value, and price normalization from the target symbol metadata and test fixtures.

### 3. Backtest output is not enough to establish an edge

The advanced notebook contains saved output reporting 89 trades, +27R, PF 1.871 and max drawdown -400 in its displayed run. The optimized notebook's saved output instead reports 133 trades, -15R, PF and other output requiring a full run audit. These are historical notebook outputs, not independently reproduced results. The displayed settings differ (notably second-entry use and several filters), and there is not yet a proven common dataset, date split, costs model, code revision, or execution parity to compare them fairly. Do not call either result validated or use them to select a production configuration.

Before comparison, recover the exact code cells, data provenance/date range, and fill/SL/TP logic; rerun from a clean deterministic manifest; then split chronologically into development, validation, and a truly untouched holdout.

### 4. Meta.py is execution infrastructure, not a full strategy specification

Observed behavior includes MT5 initialization, market/pending order placement, broker filling-mode probing, and an optional execution-based TP path that recalculates TP after a live position fill. A historical engine must model this explicitly rather than silently using the signal quote as the fill price.

Review risks / questions:
- Confirm whether order-send result codes are validated before downstream lifecycle actions; a non-null result is not necessarily a successful fill.
- Confirm matching logic for symbol + magic + ticket and whether a selected “latest” position can accidentally refer to a different concurrent trade.
- Confirm SL/TP modification retcodes and actual applied values, not just requested values.
- Audit the shared class-level TP cache and second-entry path (including the magic-number condition) for stale state, multiple positions, restart behavior, and ordering.
- Verify pending order expiry/cancellation, order-vs-position identifiers, fill timestamps, and duplicate-event protection.
- Verify timezone conversion and use of closed candles only; avoid look-ahead in indicator filters.
- Confirm the complete second-entry risk model. The notebook's optimized output shows the second-entry variant can materially change trade count and aggregate outcome; it is not automatically an improvement.
- Validate spread, slippage, commission, swap, stop/freeze levels, volume step, and rejected modifications using target-broker metadata.

These are audit questions, not asserted defects; they require line-by-line inspection and tests.

## Proposed isolated evaluation plan

1. Pin the external repository commit SHA and record file hashes and license metadata.
2. Build a source map: signal rules, entry order, SL, TP, trailing/management, second entry, time/session/indicator filters, and lifecycle.
3. Extract the notebook's actual executable cells and identify exact input data, date range, data-cleaning rules, and any embedded/saved output.
4. Create synthetic fixtures for candle boundaries, both directions, point conversions, pending fills, same-bar SL/TP ambiguity, gaps, spread/slippage, second-entry sequencing, and broker rejections.
5. Reproduce a simple baseline before testing optional filters.
6. Test one hypothesis family at a time, retain all tested variants, and report trade count, expectancy/R, PF, drawdown, costs sensitivity, chronological stability, and uncertainty.
7. Use untouched validation and fresh holdout only after the code/config and selection rule are frozen.
8. Keep this strategy's results separate from the user's current RR2/TRAIL4 forward-test data.

## Current decision

Do not port the external implementation to the current live runner. The next work should audit the current RR2/TRAIL4 baseline and data reproducibility first, while preserving this external implementation as a separate future candidate.
