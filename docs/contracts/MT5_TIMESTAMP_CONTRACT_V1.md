# MT5 Timestamp Contract v1

**Status:** FROZEN  
**Scope:** XAUUSD Strategy A / SP2L research acquisition layer  
**Canonical symbol:** `XAUUSD.ecn`  
**Canonical timeframe:** M1  
**Provider:** MetaTrader 5 Python Integration  
**Server observed:** `OtetGroup-MT5`

## 1. Purpose

This document freezes the timestamp semantics used by the Strategy A research acquisition layer. It resolves timestamp interpretation only. It does **not** resolve historical session calendars, missing-bar semantics, SP2L geometry, execution rules, P-Gap, AB=CD anchors/tolerance, or production trading decisions.

Source meaning outranks empirical backtest performance.

## 2. Canonical time basis

The canonical time basis is **UTC**.

For MT5 Python bar acquisition:

- acquisition query boundaries MUST be timezone-aware UTC datetimes, or explicit Unix epochs representing UTC boundaries;
- the returned MT5 bar field `r["time"]` is treated as the canonical Unix epoch for the bar open;
- conversion to a human-readable timestamp MUST use UTC;
- no manual broker/server/local-time offset is applied to `r["time"]`.

Canonical conversion:

```python
datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
```

## 3. Source evidence

MetaQuotes' official Python Integration documentation for `copy_rates_range` states that Python datetime objects use the local timezone while MetaTrader 5 stores tick and bar open time in UTC without a shift; it therefore instructs callers to create datetime objects in UTC and states that data received from the terminal has UTC time.

Official source:

- `copy_rates_range`: https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesrange_py
- `copy_rates_from`: https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrom_py
- MQL5 Python reading quotes guide: https://www.mql5.com/en/book/advanced/python/python_copyrates

The `copy_rates_range` documentation also defines the range contract as bars whose open time is `>= date_from` and `<= date_to`.

## 4. Empirical evidence for this environment

The project independently tested the raw MT5 epoch values on the actual research environment:

- terminal: `Otet Group MT5 Terminal`
- server: `OtetGroup-MT5`
- symbol: `XAUUSD.ecn`
- timeframe: M1

The historical raw-epoch boundary diagnostic for `2026-09-10T10:00:00Z` through `2026-09-10T10:04:00Z` returned:

- 5 bars;
- raw epochs exactly equal to the requested UTC Unix-epoch set;
- first raw epoch minus query-start epoch = `0`;
- last raw epoch minus query-end epoch = `0`;
- all consecutive raw steps = `60` seconds;
- returned raw set exactly matched the expected numeric set;
- MT5 last-error status = `Success`.

Diagnostic status was explicitly:

`HISTORICAL_RAW_EPOCH_BOUNDARY_TEST; NO_TIMESTAMP_CONVERSION; NO_SHIFT`

This empirical test is supporting environment evidence. The canonical semantic authority remains the official MetaQuotes documentation above.

## 5. Explicitly forbidden transformations

The acquisition layer MUST NOT apply any of the following to `r["time"]`:

- `-3h`
- `+3h`
- broker/server-time correction
- workstation/local-time correction
- DST correction
- any inferred timezone correction

Such a transformation would create a different timestamp from the source timestamp and is outside this frozen contract.

## 6. Compatibility exception: author-replica exporter

The research-only compatibility exporter contains a `+3h` adjustment to the **request/reference datetime** in order to reproduce the author's `Meta.GetRates` request behavior as closely as possible.

That compatibility behavior does **not** authorize or imply a `+3h` transformation of the returned `r["time"]` field.

Therefore:

```text
request/reference compatibility adjustment != bar timestamp correction
```

The compatibility exporter is not the canonical acquisition timestamp contract.

## 7. Separation from session/calendar semantics

Timestamp semantics and session availability are separate contracts.

A missing timestamp in a historical acquisition MUST NOT be interpreted as a timezone error merely because it is absent from the returned dataset.

Likewise, an observed gap MUST NOT be declared a real market/session closure until the historical session calendar has been independently resolved.

Current acquisition evidence has already shown that a retrieval ending on the current day can stop at the current available bar. Therefore, current-day truncation is not evidence of a historical session gap.

## 8. Provenance and reproducibility requirements

Every canonical acquisition artifact MUST preserve enough provenance to reproduce the timestamp interpretation, including:

- provider;
- terminal/server;
- symbol;
- timeframe;
- requested interval;
- retrieval timestamp;
- acquisition script/version or commit;
- artifact hash where applicable;
- audit status.

The acquisition layer MUST remain deterministic with respect to timestamp interpretation: the same raw MT5 epoch must map to the same UTC timestamp without context-dependent offset inference.

## 9. What this contract does and does not prove

### Proven

- MT5 Python acquisition uses UTC query semantics for the canonical acquisition path.
- MT5 bar-open timestamps are treated as UTC without a manual shift.
- The actual `OtetGroup-MT5 / XAUUSD.ecn / M1` environment has passed a historical raw-epoch boundary consistency test.

### Not proven by this contract

- completeness of the available historical dataset;
- the historically correct XAUUSD.ecn trading/session calendar;
- interpretation of every missing-bar interval as a session boundary;
- SP2L geometry or trigger semantics;
- execution/fill semantics;
- statistical edge or live-trading performance.

## 10. Frozen decision

**FROZEN:** `MT5 bar timestamp basis = UTC; no manual timestamp shift.`

Any future proposal to change this contract MUST provide new source evidence or a demonstrated defect in the current interpretation and MUST NOT silently alter existing research artifacts.

Existing datasets remain immutable research evidence; a changed contract, if ever justified, requires a new versioned contract and separately versioned/reacquired datasets.
