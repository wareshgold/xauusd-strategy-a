# SP2L Batch 31 — Worked-Trade Chart/History Timeline Forensic

## Purpose

Reconstruct the strongest observable temporal relationship between the worked XAUUSD chart views and the account/history tables around the May 12 worked example, without inferring a canonical fill or lifecycle rule.

## Observed timeline evidence

### Chart context

- The worked chart is explicitly annotated `SP2L`, `EMA60`, and `M1` in the later execution section.
- The chart x-axis visibly covers May 12 intraday time labels in the worked example.
- Around the execution screenshots, the chart contains the same price region as the account records, including levels around 3213–3238.

### Account state

The account-position screenshot shows simultaneous XAUUSD sell positions with:

- 3229.08 / SL 3237.73 / TP 3213.30
- 3223.84 / SL 3235.50 / TP 3213.37
- 3228.88 / SL 3235.50 / TP 3213.37
- 3232.41 / SL 3237.80 / TP 0.00

This establishes that multiple sell positions were represented simultaneously in the worked account state.

### History timestamps

The readable worked-history table shows a tight cluster of records:

- 3229.08: timestamp `2025.05.12 12:56:02`, close/current value `3213.37`
- 3223.84: timestamp `2025.05.12 12:56:02`, close/current value `3213.37`
- 3228.88: timestamp `2025.05.12 12:56:02`, close/current value `3213.37`
- 3232.41: timestamp `2025.05.12 12:56:24`, close/current value `3214.11`
- 3232.41: timestamp `2025.05.12 12:56:58`, close/current value `3214.72`
- 3232.41: timestamp `2025.05.12 12:57:06`, close/current value `3215.80`
- a separate row around `3269.88` has no visible SL/TP and a later price around `3261.74` at `2025.05.12 04:14:28`.

## What can be established

1. The account screenshots and chart screenshots are from the same worked XAUUSD teaching context.
2. The history contains a clustered set of records at the same prices shown in the account-position screenshot.
3. The first three displayed positions share the same recorded timestamp and the same TP outcome, which is consistent with clustered execution/closure activity.
4. The later 3232.41 rows show subsequent recorded prices at 12:56:24, 12:56:58, and 12:57:06.
5. This is stronger temporal evidence than an isolated screenshot because multiple records can be ordered chronologically.

## What cannot be established

The available frames do **not** provide an event-level mapping from a specific chart candle to a specific history row. In particular, they do not prove:

- whether the displayed history `Time` column is open time, close time, or another platform event timestamp;
- the exact chart candle corresponding to each history timestamp;
- whether the three 12:56:02 rows were separate fills, simultaneous fills, manual scaling, or another account action;
- whether the 3232.41 sequence represents repeated fills, repeated closes, partial management, or separate position records;
- whether a pending Buy Limit preceded any specific history row;
- whether activation was by touch, wick penetration, bar close, next-bar confirmation, or another execution condition;
- whether the execution was automatic or manually managed;
- broker spread, bid/ask, slippage, or intrabar ordering semantics.

## F9/F11 impact

**F9 — activation/fill:** strengthened from generic executed-position evidence to a temporally ordered worked-history cluster, but exact activation/fill semantics remain unresolved.

**F11 — order lifecycle:** strengthened because multiple chronological account records are visible, but pending → fill → management causality, replacement, cancellation, expiry, and precedence remain unresolved.

No canonical execution rule is promoted.

## Gate

- Source Resolution: **PARTIAL PASS — temporal evidence strengthened**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

No backtest variant or production implementation was changed.
