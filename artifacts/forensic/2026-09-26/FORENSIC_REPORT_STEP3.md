# SP2L Forward Forensic Step 3 — Poll/Data Telemetry

Date: 2026-09-26  
Branch: `research/sp2l-f13-demo-forward-slfixed-2026-09-21`

## Purpose

Implement the Step 3 instrumentation identified in the Step 2 forensic report. This is research-only telemetry. It does not change SP2L geometry, P-Gap, SL, TP, session, fill, order lifecycle, or production status.

## Step 2 gap being addressed

Step 2 could not establish whether the Forward runner was continuously polling, what the rolling MT5 API returned during the historical windows, or whether the detector had the expected completed-bar window.

## Telemetry added

The forward runner now records, by `poll_id`:

- `DATA_SNAPSHOT`
  - wall-clock UTC
  - every returned M1 bar's raw MT5 `time`
  - an explicit UTC interpretation of that raw timestamp
  - OHLC and volume/spread fields
  - array index/order
  - returned bar count
  - `mt5.last_error()` captured immediately after `copy_rates_from_pos()`
- `DETECTOR_RESULT`
  - detector output for the exact snapshot
  - explicit detector window: `candles[-5]` through `candles[-2]`
  - signal-time source
- `POLL_HEALTH`
  - wall-clock UTC
  - poll processing elapsed time
  - inter-poll gap
  - current bid/ask and tick timestamps
  - MT5 terminal connectivity/trading flags
  - account login/trade mode

Telemetry is enabled by default and can be disabled with `SP2L_FORENSIC_STEP3_TELEMETRY=0`.

## Important interpretation rule

The `interpreted_utc` field is only an explicit interpretation of the raw epoch value for forensic comparison. It does **not** assert that MT5's returned timestamps have been proven UTC-aligned. Timestamp normalization remains unresolved until simultaneous comparison of the relevant MT5 acquisition APIs from the same terminal.

## Non-changes

- Shared detector geometry unchanged.
- No canonical Strategy A rule introduced.
- No P-Gap formula promotion.
- No SL/fill/order-lifecycle semantics promoted.
- No production BUY/SELL logic introduced.
- No retry or level-adjustment behavior changed.

## Next evidence step

Run the instrumented Forward runner against the same MT5 terminal and collect the Step 3 JSONL event stream. Then compare the exact raw rolling snapshots against the historical `copy_rates_range()` snapshots for the three previously unresolved windows.

