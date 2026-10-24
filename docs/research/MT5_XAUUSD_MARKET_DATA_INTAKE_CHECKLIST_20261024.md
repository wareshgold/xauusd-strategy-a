# MT5 XAUUSD Market-Data Intake Checklist — 2026-10-24

## Purpose

Capture a reproducible market-data snapshot for offline Strategy B vs RR2/TRAIL4 research. This is a data-integrity checklist only; it does not define strategy geometry, fill semantics, execution rules, or canonical Strategy A behavior.

## What a one-month MT5 download can unblock

A one-month XAUUSD M1 export can help establish a shared candle dataset for the comparison, check timestamp coverage/gaps, and reproduce candle-based diagnostics over the same time window.

It **does not by itself** establish historical strategy fills, broker-confirmed deal identity, exact entry/exit timestamps, executed volume, commission/swap, or parity between the two runners. Those require immutable runner event snapshots and broker deal-history exports for the relevant account(s), where available.

If the trailing implementation depends on intrabar price order, M1 OHLC alone may not resolve whether SL/TP/trailing levels were reached first. Tick data is preferable where available, but tick data must not be treated as a substitute for actual broker deal history.

## Recommended export package

When the user is ready to download, preserve a new immutable package; never overwrite a prior export.

1. **Symbol identity**
   - Record the exact MT5 symbol, e.g. `XAUUSD.ecn` if that is the symbol shown by the terminal.
   - Record broker/server name, terminal/build, export time (UTC), timeframe, and exact requested start/end boundaries.
   - Do not silently merge `XAUUSD`, `XAUUSD.ecn`, or other broker-specific symbols.

2. **Market bars**
   - Export at least one full month of M1 bars with timestamp, open, high, low, close, and tick volume/real volume if exposed.
   - Include a little buffer before/after the intended replay interval, then retain the exact requested interval separately in the manifest.
   - If feasible, export tick data for the same interval as a separate file; do not replace or modify the M1 file.
   - Keep the original downloaded file exactly as exported. Do not manually edit timestamps or decimal precision.

3. **Timestamp evidence**
   - Record whether exported timestamps are broker-server time or UTC; do not assume either.
   - Preserve an example timestamp as displayed by MT5 and the matching terminal/server clock evidence.
   - Document any conversion rule and DST ambiguity separately; never silently shift bars to make signals match.

4. **Manifest and integrity**
   - Record original filename, byte size, SHA-256, symbol, timeframe, source server, terminal build, export method, requested interval, observed first/last timestamps, and export timestamp.
   - Hash the raw file before normalization. Write any normalized derivative to a new path and record its own hash and the explicit mapping.
   - Preserve missing-minute/gap counts and duplicate/out-of-window rows as audit findings rather than silently dropping them.

5. **Execution evidence (separate package)**
   - Export broker deal history for the Strategy B and RR2/TRAIL4 execution account(s), where accessible, as separate original files.
   - Required fields if the platform/export supports them: deal ticket/ID, order ID, position ID, original execution time, symbol, buy/sell and entry/exit codes, execution price, executed volume, profit, commission, swap, and fees.
   - Preserve the source account/server identity in a private manifest. Redact credentials and account secrets; never commit passwords, tokens, or unredacted account identifiers to a public repository.
   - Keep each runner's original event JSONL/log snapshot immutable and hash it separately.

## Research gate

Before paired replay:
- verify symbol and interval compatibility;
- inspect first/last timestamps, gaps, duplicates, and server-time/UTC mapping;
- pin exact source/config commit and file hashes for each runner;
- exact-ID join normalized event records to broker deal records; never join solely by timestamp proximity or OHLC;
- account for unmatched/ambiguous rows and missing fields;
- state explicitly whether the available data can support M1 replay, tick-level sequencing, and/or actual-fill accounting.

A green schema check or a matching candle timestamp is not proof of execution truth or profitability. All outputs remain research-only pending source-rule resolution and the project's full validation workflow.
