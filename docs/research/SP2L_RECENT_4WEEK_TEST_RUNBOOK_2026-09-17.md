# SP2L Recent 4-Week Test Runbook — 2026-09-17

## Purpose

Acquire and audit the most recent four-week XAUUSD.ecn M1 sample using the same MT5 provenance as the existing stability work.

## Window

- Start UTC: `2026-08-21T00:00:00Z`
- End UTC: `2026-09-17T23:59:00Z`
- Symbol: `XAUUSD.ecn`
- Timeframe: `M1`
- Server: `OtetGroup-MT5`
- Provider: MetaTrader5 terminal API

## Important status boundary

The current native-MQL5 session observation is:

- Monday-Friday: `01:00` through `23:59` UTC
- Saturday/Sunday: no session returned

This is a current observation dated 2026-09-17. It is NOT historical proof for the entire four-week interval.

Therefore the script's acquisition audit is explicitly labeled `CURRENT_OBSERVATION_NOT_HISTORICALLY_VERIFIED`.

## User execution

From the repository root:

```powershell
git pull
python scripts/mt5_recent_4week_session_audit.py
```

The script writes:

- `artifacts/xauusd-ecn-m1-recent-4week-2026-08-21_2026-09-17.csv`
- `artifacts/xauusd-ecn-m1-recent-4week-2026-08-21_2026-09-17.audit.json`

Exit code:

- `0` = acquisition audit passes under the current observed calendar
- `2` = acquisition audit fails

## Safety rules

- No timestamp shifting.
- No interpolation.
- No forward filling.
- No synthetic candles.
- No inferred historical calendar changes.
- A failed audit must not be used as a published SP2L backtest dataset.
- A passing audit does not by itself establish historical session applicability.

## Next phase

Only after the artifact is inspected and provenance is accepted should the exact same frozen research configuration be run through the SP2L test harness. The four-week result is descriptive/stability evidence, not a canonical rule definition and not production authorization.
