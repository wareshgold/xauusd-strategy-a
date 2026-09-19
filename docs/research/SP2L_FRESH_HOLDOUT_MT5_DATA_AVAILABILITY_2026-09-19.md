# SP2L Fresh Holdout — MT5 Weekend Data Availability Diagnostic — 2026-09-19

## Result

The untouched Fresh Holdout boundary remains:

**2026-09-19 00:00:00 UTC onward**

A new untouched Fresh Holdout availability check was executed locally on branch:

`research/sp2l-live-mt5-telegram-2026-09-19`

The runner requested only:

- Symbol: `XAUUSD.ecn`
- Timeframe: M1
- Start: **2026-09-19 00:00:00 UTC**
- End at this check: **2026-09-19 07:37:38 UTC**

Result:

- `MetaTrader5.copy_rates_range`: **0 bars**
- MT5 acquisition error: **null / no reported error**
- Status: **HOLDOUT_DATA_UNAVAILABLE**

The frozen configuration used by the runner remained:

- P-Gap = 1.0
- Spike Multiplier = 1.5
- Max SL = 10.0
- TP = 1.0R

## Prior acquisition evidence

Earlier on 2026-09-19, a `copy_rates_from` diagnostic requested 500 bars ending at 2026-09-19 06:08:20 UTC and returned:

- first: **2026-09-18 15:38:00 UTC**
- last: **2026-09-18 23:57:00 UTC**
- count: **500**
- `last_error`: `(1, 'Success')`

That sample did not cross the frozen holdout boundary.

## Calendar interpretation

2026-09-19 is a Saturday. The observed absence of post-boundary XAUUSD.ecn M1 bars is consistent with the terminal having no Saturday morning market data available.

This is an observed data-availability result, not evidence that Strategy A generated zero signals and not a holdout performance result.

## Gate disposition

- Fresh Holdout: **NOT RUN**
- Holdout data integrity: **PENDING / NO ELIGIBLE BARS YET**
- Frozen parameters: **UNCHANGED**
- Source/geometry rules: **UNCHANGED**
- Parameter tuning: **NONE**
- Post-result subperiod selection: **NONE**
- Production/live trading: **BLOCKED**

## Next valid action

Do not substitute 2026-09-18 or any earlier date into the Fresh Holdout.

Keep the frozen boundary at **2026-09-19 00:00:00 UTC**. Re-run the same single-configuration Fresh Holdout after new post-boundary XAUUSD.ecn M1 data becomes available. The holdout may accumulate from the frozen boundary onward without changing parameters or selecting a favorable sub-period.

The next check must continue to use the committed frozen runner:

`scripts/run-author-replica-mt5-fresh-holdout.py`

No parameter sweep, tuning, geometry reinterpretation, fill-rule change, or production execution is permitted as part of this gate.

## Reproducibility note

The latest local run produced:

`artifacts/SP2L_fresh_holdout_2026-09-19.json`

The structural integrity audit is recorded at `docs/research/SP2L_FRESH_HOLDOUT_INTEGRITY_AUDIT_2026-09-19.md`.

The artifact is a research-only availability result and does not authorize live trading.
