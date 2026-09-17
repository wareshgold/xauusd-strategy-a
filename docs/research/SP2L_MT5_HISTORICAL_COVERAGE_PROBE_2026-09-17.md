# SP2L MT5 Historical Coverage Probe — 2026-09-17

## Purpose

Determine which historical UTC M1 intervals are physically available from the same MT5 terminal/feed used by the existing non-overlap stability work, without silently treating current session metadata as historically valid.

This is a **data-coverage/provenance probe only**. It does not define or modify SP2L geometry, direction, entry, fill, stop, target, AB=CD, P-Gap, or lifecycle rules.

## Fixed source configuration

- Provider: MetaTrader5 terminal API
- Terminal: Otet Group MT5 Terminal
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Timestamp basis: UTC
- Acquisition API: `copy_rates_range`
- No timestamp shifting
- No interpolation
- No forward filling
- No synthetic candles

## Session-calendar status

Native MQL5 session metadata observed on 2026-09-17 reports Monday-Friday quote/trade session `01:00:00` through `00:00:00` UTC, with no returned Saturday/Sunday session.

That observation is **current point-in-time evidence only**. Historical applicability is `UNVERIFIED` until independently established for the historical interval being acquired.

## Probe windows

Run the exact session-aware audit against these non-overlapping UTC windows:

1. 2026-09-01T00:00:00Z → 2026-09-17T23:59:00Z — current-period availability and session-boundary behavior.
2. 2026-08-01T00:00:00Z → 2026-08-31T23:59:00Z — historical availability probe.
3. 2026-07-01T00:00:00Z → 2026-07-31T23:59:00Z — historical availability probe.
4. 2026-06-01T00:00:00Z → 2026-06-30T23:59:00Z — historical availability probe only; calendar applicability remains unverified.
5. 2026-05-01T00:00:00Z → 2026-05-31T23:59:00Z — historical availability probe only; calendar applicability remains unverified.
6. 2026-04-01T00:00:00Z → 2026-04-30T23:59:00Z — historical availability probe only; calendar applicability remains unverified.

## Classification

Each run must be classified separately:

- `AUDITED_PASS`: exact expected set under the supplied calendar, unique and chronological, with no invalid timestamp jumps.
- `AUDITED_FAIL`: the supplied calendar is being treated as applicable for the audit and the returned data violates its expected set/continuity contract.
- `REJECTED_UNVERIFIABLE`: raw availability may be observed, but the calendar used to judge historical completeness has not been independently established for that period.

For April/May/June, an `AUDITED_PASS` under the **current** calendar must **not** be promoted into the published historical dataset because the contract explicitly marks historical applicability unverified.

## Required artifact provenance

For every run retain:

- dataset ID
- exact requested interval UTC
- terminal/server/symbol/timeframe
- calendar ID and evidence date
- expected count
- returned count
- missing/unexpected timestamps
- timestamp jumps and invalid jumps
- retrieval timestamp
- artifact SHA-256
- audit status

## Promotion gate

Only data with an independently verified historical session calendar may enter the published historical stability/validation dataset.

A coverage probe may establish that data exists; it does **not** establish that the data is suitable for canonical backtesting.

## Next gate

After the probes, resolve historical session applicability before using April/May/June for Strategy A validation. Do not mix Twelve Data repository data with MT5 data in a single statistical sample unless a separate, explicit cross-provider equivalence/provenance contract is established.
