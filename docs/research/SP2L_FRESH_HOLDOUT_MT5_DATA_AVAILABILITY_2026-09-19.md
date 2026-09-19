# SP2L Fresh Holdout — MT5 Weekend Data Availability Diagnostic — 2026-09-19

## Result

The untouched Fresh Holdout boundary remains:

**2026-09-19 00:00:00 UTC onward**

Two acquisition paths were tested locally against `XAUUSD.ecn` M1 for the morning of 2026-09-19:

- `copy_rates_range`: 0 bars; MT5 error state reported success.
- `copy_rates_from`: 500 bars returned when requesting 500 bars ending at 2026-09-19 06:08:20 UTC.

The returned `copy_rates_from` sample was:

- first: **2026-09-18 15:38:00 UTC**
- last: **2026-09-18 23:57:00 UTC**
- count: **500**
- `last_error`: `(1, 'Success')`

Therefore the returned history did **not** cross the frozen holdout boundary.

## Calendar interpretation

2026-09-19 is a Saturday. The observed last available M1 bar at 2026-09-18 23:57 UTC is consistent with the MT5 terminal having no XAUUSD.ecn M1 bars available for the Saturday morning request.

This is an observed data-availability result, not evidence that Strategy A generated zero signals.

## Gate disposition

- Fresh Holdout: **NOT RUN**
- Holdout data integrity: **PENDING / NO ELIGIBLE BARS YET**
- Frozen parameters: **UNCHANGED**
- Source/geometry rules: **UNCHANGED**
- Parameter tuning: **NONE**
- Production/live trading: **BLOCKED**

## Next valid action

Do not substitute 2026-09-18 or any earlier date into the Fresh Holdout.

Keep the frozen boundary at **2026-09-19 00:00:00 UTC** and re-run the single-configuration Fresh Holdout only after new post-boundary XAUUSD.ecn M1 data becomes available. The holdout may then accumulate from the frozen boundary onward without changing parameters or selecting a favorable sub-period.

## Reproducibility note

This diagnostic was performed from branch:

`research/sp2l-live-mt5-telegram-2026-09-19`

The diagnostic does not authorize live trading and does not alter the frozen validation configuration.
