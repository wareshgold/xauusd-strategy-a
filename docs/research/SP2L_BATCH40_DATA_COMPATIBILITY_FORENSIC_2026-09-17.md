# SP2L Batch 40 — Author Replica Data Compatibility Forensic

Date: 2026-09-17

## Objective

Determine whether the zero-signal result from the author-implementation replica can legitimately be interpreted as a geometry mismatch, or whether the input data/feed differs materially from the author's own backtest environment.

## Decisive finding

The author's advanced backtest obtains its XAUUSD M1 data through MetaTrader 5:

- `Meta.GetRates(symbol='XAUUSD', number_of_data=10000, timeFrame=mt5.TIMEFRAME_M1)`
- `Meta.GetRates` delegates to `mt5.copy_rates_from(...)`.
- The returned MT5 rates are converted into a pandas DataFrame and indexed by the broker/terminal-provided timestamp.
- `BROKER_POINT` is read from `mt5.symbol_info(symbol).point` and is used to convert `PGAP_POINTS=100` into `P_GAP_PRICE`.

This is materially different from the current project replica dataset, whose committed historical artifact is identified by the research backtest as a TwelveData XAUUSD 1-minute dataset. Therefore the current zero-signal result is **not a controlled replication of the author's 93-signal run**.

## Evidence chain

### Author implementation

The author's `SP2L2_Advanced_Backtest.ipynb` uses XAUUSD M1, 10,000 data points, `PGAP_POINTS=100`, and derives the price gap from the MT5 broker point. The inspected executed output reports 93 signals and 92 completed trades under that environment.

### Author data acquisition

The author's `code/SP2L/Meta.py` defines `GetRates` using `mt5.copy_rates_from(symbol, timeFrame, fromDate, number_of_data)`. When no explicit date is supplied, the function uses the current UTC time plus a terminal-offset adjustment before requesting the latest bars. This means the exact 10,000-bar sample is dependent on the MT5 terminal's broker feed and the execution time.

### Current project replica

The research replica currently reads `data/historical/xauusd-1min.json` from the project repository and applies the author's observable four-candle logic. The current diagnostic run therefore tests the author geometry against a different historical-feed artifact rather than reproducing the author's original MT5 sample.

## Consequence

The zero-signal outcome must be classified as:

**REPLICATION INCONCLUSIVE — DATA/FEED COMPATIBILITY NOT CONTROLLED**

It must not be classified as:

- author implementation disproven;
- P-Gap threshold disproven;
- spike multiplier disproven;
- canonical SP2L geometry disproven.

## Additional implementation evidence

The author's older live `SP2L_Bot.py` also obtains M1 data through the same `Meta.GetRates`/MT5 path and uses `pGapSize=1`, with the basic four-candle indexing family. Its live entry uses broker-side `ask` for BUY and `bid` for SELL rather than treating a historical candle low/high as a literal executable fill. This further demonstrates that feed and execution environment are part of a faithful implementation replication and should not be conflated with canonical source geometry.

The advanced implementation separately contains a deterministic backtest representation. Its reported 93-signal result therefore remains an **author implementation result tied to that notebook/data environment**, not a source-confirmed Strategy A benchmark that can be assumed reproducible on another feed.

## Required next experiment

### Experiment A — controlled data acquisition

Obtain an MT5 XAUUSD M1 sample using the author's exact acquisition family and preserve:

- broker/server identity;
- symbol;
- point/digits;
- timezone/timestamp convention;
- exact 10,000-bar range;
- OHLC values;
- acquisition timestamp;
- source artifact hash.

Then run the **unchanged author replica** against that sample.

### Experiment B — controlled cross-feed comparison

If an MT5-equivalent sample cannot be obtained, run the unchanged replica over multiple available XAUUSD M1 datasets while preserving all configuration values. Compare only diagnostic signal counts and condition-stage survival; do not tune thresholds to maximize performance.

### Experiment C — implementation parity

If an MT5-equivalent sample reproduces approximately 93 signals, compare signal timestamps and OHLC windows one-by-one against the notebook output if those rows can be recovered. Only discrepancies that survive data equivalence should be investigated as implementation differences.

## Gate status

- Source Resolution: **PARTIAL PASS**
- Author implementation crosswalk: **STRENGTHENED**
- Data compatibility for replication: **BLOCKED / NOT CONTROLLED**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**

## Canonicalization rule

No P-Gap threshold, spike multiplier, filter, entry rule, or execution rule is changed as a result of this batch. The purpose of this batch is to prevent a feed mismatch from being mistaken for a geometry failure.
