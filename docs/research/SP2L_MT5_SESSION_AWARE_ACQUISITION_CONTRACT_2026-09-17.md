# SP2L MT5 Session-Aware Acquisition Contract — 2026-09-17

## Status

Research-only acquisition contract. No SP2L geometry, direction, entry, fill, or execution rule is defined here.

## Source evidence

Native MQL5 `SymbolInfoSessionQuote` / `SymbolInfoSessionTrade` diagnostic for `XAUUSD.ecn` on `OtetGroup-MT5` reported:

- Monday–Friday quote session: `01:00:00` → `00:00:00`
- Monday–Friday trade session: `01:00:00` → `00:00:00`
- Sunday: no session returned
- Saturday: no session returned
- Diagnostic timestamp: 2026-09-17

This evidence establishes the observed current session boundary. It does **not** establish that the same schedule applied historically in April/May/June 2026.

## Audit semantics

For a requested UTC M1 interval, expected timestamps are the intersection of the request with the observed session calendar:

- Monday–Friday: minutes from 01:00 inclusive through 23:59 inclusive.
- Saturday/Sunday: no expected market bars.
- A missing minute inside an expected session is an acquisition failure.
- A missing minute outside an expected session is an expected unavailable interval and must not be fabricated.
- No timestamp shifting, interpolation, forward filling, or synthetic candle creation is permitted.

## Historical safety gate

The current session metadata is a point-in-time observation. It must not be silently applied to historical April/May/June acquisition.

Historical acquisition may only be published as `AUDITED_PASS` after the session calendar used for that historical interval has independently been established or explicitly scoped as verified evidence.

## Required manifest fields

Session-aware artifacts must record:

- session calendar evidence identifier/date
- requested interval UTC
- expected active-bar count under that calendar
- returned bar count
- missing expected timestamps
- unexpected returned timestamps
- internal timestamp jumps
- audit status

Allowed statuses include `AUDITED_PASS`, `AUDITED_FAIL`, and `REJECTED_UNVERIFIABLE`.
