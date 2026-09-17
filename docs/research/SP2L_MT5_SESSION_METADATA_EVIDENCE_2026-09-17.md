# SP2L MT5 Session Metadata Evidence — 2026-09-17

## Purpose

Record the native MQL5 session metadata observed for `XAUUSD.ecn` on the same MT5 terminal/server used by the SP2L acquisition diagnostics.

## Environment

- Terminal: Otet Group MT5 Terminal
- Company: Otet Group Ltd.
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- Diagnostic: `scripts/mt5_mql5_symbol_session_metadata.mq5`
- Observation timestamp: 2026-09-17 12:20 UTC (Experts log)

## Observed schedule

For Monday through Friday, both QUOTE and TRADE expose one session:

- `from=01:00:00`
- `to=00:00:00`

The native MQL5 session API therefore reports a session beginning at 01:00 and ending at 00:00, i.e. the session endpoint reaches the next UTC day boundary. Saturday exposes no session. Sunday exposes no session at index 0.

The probe terminates with `error=4307` after the first session for each weekday, which is treated only as the end of the available session enumeration by this diagnostic; no additional session is inferred.

## Relation to observed M1 availability gaps

Earlier M1 diagnostics on this exact terminal/server/symbol repeatedly observed a missing interval around 00:00–01:00 UTC on trading weekdays, including:

- 2026-09-15: missing 23:59–01:00 transition interval corresponding to the observed 00:00–00:59 UTC absence.
- 2026-09-16: missing 00:00–00:59 UTC.

The native MQL5 session metadata independently reports weekday sessions from 01:00:00 to 00:00:00. This is consistent with the observed daily 00:00–01:00 UTC availability boundary.

## Status

**SESSION BOUNDARY: SOURCE-CONFIRMED FOR THIS MT5 ENVIRONMENT**

This evidence confirms the broker/terminal session schedule exposed by native MQL5 for `XAUUSD.ecn` and explains the recurring daily UTC boundary observed by the acquisition diagnostics.

It does **not** define or modify any SP2L geometry, P-Gap formula, spike rule, AB=CD rule, entry/exit semantics, fill semantics, or production execution rule.

It also does not justify filling, shifting, interpolating, or fabricating bars across the unavailable interval. Acquisition and continuity audits must continue to treat those timestamps as unavailable.

## Reproducibility

The diagnostic source is versioned in the repository. The observed output was copied from the MT5 Experts log after successful compilation and execution of the native MQL5 diagnostic.

No historical bars were modified by this diagnostic.
