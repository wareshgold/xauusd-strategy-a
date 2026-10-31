# Strategy B event adapter field map (2026-10-24)

**Status: offline source inspection only. No bot was started; no MT5 connection, broker query, or runtime file access was performed.**

This document maps only fields and behavior visible in the checked-in Strategy B source copies. It is a research adapter plan, not proof of historical execution and not a canonical Strategy A specification.

## Exact source identity

| Component | Branch / file | Blob SHA |
|---|---|---|
| Strategy/setup source | `research/strategy-b-pythontraderbot-execution-20261022/scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py` | `ec275d3fef7ef372823a3626dba5f2718001c52d` |
| Execution adapter | `research/strategy-b-pythontraderbot-execution-20261022/scripts/strategy_b_pythontraderbot_live/Meta.py` | `5a145fd02c282950b169165eb8b888e904d1fe6a` |

## What the source establishes

The inspected `Meta.py` contains market-deal request paths using `mt5.order_send(request)`, with BUY requests using Ask and SELL requests using Bid in the inspected paths. It checks returned `retcode` values and may call `UpdateTPAfterFill` when execution-based TP is enabled. This confirms the implementation path only; it does not establish that a particular historical request was accepted, filled, or closed.

The inspected source relies on prints / returned MT5 result objects for execution diagnostics. It does not expose a durable normalized event-ledger writer or a broker deal-history export in these checked-in files. Do not assume that terminal output, Telegram notifications, or strategy candidates are complete immutable evidence.

## Field map and evidence limits

| Source evidence | Possible normalized use | Limit / required treatment |
|---|---|---|
| Strategy/setup calculation in `SP2L_Advanced_Bot_Optimized.py` | `SIGNAL_CANDIDATE` with source commit, exact source row/log reference, and input identity if available | Candidate/trigger is not order submission or fill |
| Market request in `Meta.py` | `ORDER_SUBMITTED` only if the request itself is preserved with an immutable reference | Source code alone is not evidence that a historical request was sent |
| `order_send` return / `retcode` / `comment` | Preserve raw response and map a response status only with the matching MT5 API enum/version | Accepted/placed response does not universally prove completed fill; keep submitted, placed, and executed states distinct |
| Request `symbol`, side/type, requested `price`, `volume`, SL/TP | Preserve as request fields | Requested price/volume are not necessarily execution price/volume |
| Actual broker deal ticket, timestamp, execution price, volume, entry/exit code | `ENTRY_FILL` / `EXIT_FILL` only after sourced from an immutable broker deal artifact and linked to the request/position | These are not established for historical trades by the checked-in source code |
| `UpdateTPAfterFill` prints: actual fill, slippage, SL, old/new TP, result comment | Diagnostic evidence if the exact output is captured and source-referenced | Print output is not a durable complete deal ledger; TP update request/result must remain distinct from confirmed broker position state |
| Telegram notification | Notification/observation record if captured with immutable artifact reference | Not a substitute for broker deal history; notification time is not automatically deal time |
| Candle OHLC / backtest simulation | Explicitly labeled `ohlc_proxy` or `derived_assessment` | Must never be upgraded to an actual broker fill or exit |

## Required Strategy B immutable evidence

Before building historical actual-fill rows, obtain a read-only export of broker deal history for the exact window, with at least:

- stable deal ticket/ID and order/position identifiers where available;
- broker-provided deal time in its original representation, plus a documented timezone basis;
- symbol, deal entry/type codes, execution price, executed volume;
- profit, commission, swap and any other applicable fees;
- a source export identity, export timestamp, and SHA-256 of the exact original bytes;
- an explicit linkage method from deals to the strategy/order where possible, including unmatched/ambiguous rows.

Redact account identifiers and credentials, but preserve stable deal/order/position IDs needed for within-dataset linkage. Do not rewrite the original export to normalize it; normalize a copy while retaining row references to the hashed original.

If broker deal history is unavailable, leave actual entry/exit evidence as `UNKNOWN` / `NOT_DETERMINABLE`. Do not reconstruct it from candle touches or the Strategy B notebook backtest.

## Deterministic adapter rules

1. Hash the exact immutable source bytes before parsing; preserve original row references.
2. Keep request price separate from actual deal price, requested volume separate from executed volume, and request/response time separate from broker deal time.
3. Preserve raw MT5 enum codes with the source/API version before mapping them to normalized event types.
4. Do not infer an exit from SL/TP geometry, candle highs/lows, or a notification.
5. Do not assign event ordering by file order when source sequence evidence is absent. Equal/unmapped times remain `AMBIGUOUS`.
6. Keep Strategy B's forming-M1 poll / market-deal profile distinct from RR2/TRAIL4's research pending-limit profile.
7. Missing data remains null with an explicit warning; do not manufacture a timestamp, volume, deal ID, or fill.

## Gate status

Historical paired replay remains **BLOCKED** until Strategy B has immutable broker deal evidence and the RR2/TRAIL4 source event snapshot is independently hashed and reviewed. Even with those artifacts, timestamp mapping, order/deal linkage, trailing update ordering, overlap, and common historical costs must be validated before performance statistics can be interpreted.
