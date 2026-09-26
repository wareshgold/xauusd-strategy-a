# SP2L Forward vs Backtest Forensic Report — 2026-09-26

## Scope

Research-only reconciliation of XAUUSD.ecn M1 Forward vs MT5 historical Backtest artifacts published under `artifacts/forensic/2026-09-26/`.

No canonical Strategy A rule is changed by this report.

## Step 1 — Signal-set reconciliation

Backtest artifact:
- period: 2026-09-24 00:00 UTC through 2026-09-25 23:59:59 UTC
- research session: London open -> New York close
- 13 signals

Forward author-replica events:
- 18 unique XAUUSD candidates in the published event file
- 9 candidates exactly match the Backtest signal timestamp + direction + entry/SL/TP
- 4 Backtest candidates have no Forward candidate
- 9 Forward candidates are outside the Backtest period/session universe

The 9 Forward-only candidates are explained by the Forward runner being active outside the Backtest eligibility universe:
- 2026-09-21/22 candidates are outside the Backtest date range.
- 2026-09-25 03:42, 03:59, 05:45 and 06:28 UTC are outside the London-open -> New-York-close research session.

Therefore the earlier statement that the two paths merely had '13 vs 13' is not sufficient. The current evidence is 9 exact matches + 4 Backtest-only candidates within the requested comparison period.

## Step 2 — The four Backtest-only candidates

| Trigger UTC | Direction | Entry | Forward status |
|---|---:|---:|---|
| 2026-09-24 08:48 | BUY | 4284.00 | no runner uptime at trigger |
| 2026-09-24 10:07 | BUY | 4280.71 | genuine uptime miss; unresolved |
| 2026-09-24 11:55 | SELL | 4263.12 | genuine uptime miss; unresolved |
| 2026-09-24 12:45 | SELL | 4253.37 | genuine uptime miss; unresolved |

The published Forward lifecycle events show the runner was not started until 2026-09-24 09:18 UTC, so the 08:48 candidate is a known coverage miss.

The runner was active during the other three trigger windows:
- 10:07 UTC: a START occurred at 10:01:26 UTC and the next STOP was after 10:11 UTC.
- 11:55 UTC: the runner was active from 11:30:27 UTC until after 12:11 UTC.
- 12:45 UTC: the runner was active from 12:14:19 UTC and remained active past 12:45 UTC.

Those three are therefore real forward-detection misses, not merely downtime.

## Step 3 — Timestamp path finding

The Forward runner currently obtains its rolling bars with:

`mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, count)`

The historical Backtest obtains bars with `mt5.copy_rates_range(...)`.

The repository's own Backtest source records a direct observation that `copy_rates_from_pos()` showed a '+3h-looking current-bar timestamp', while `copy_rates_range()` returned UTC-aligned historical edges and intentionally applies no broker offset.

The Forward event evidence shows the same symptom: for example, the event was logged around 2026-09-24 10:32 UTC while its trigger_time is 2026-09-24 13:31 UTC. The same signal geometry (SELL 4248.92 / SL 4249.28 / TP 4248.56) is present in the Backtest at trigger_time 13:31 UTC.

Important: this is an observed acquisition-path discrepancy, not proof that MetaTrader's documented API semantics are universally +3h. Official MQL5 documentation states that bar timestamps returned by the Python integration are UTC. The repo-specific +3h observation therefore needs to be resolved empirically for this terminal before any timestamp normalization is declared canonical.

## Step 4 — Current statistical interpretation

The 13-signal Backtest sample has:
- 1 WIN
- 5 LOSS
- 7 AMBIGUOUS
- 6 decisive outcomes
- net -4R

This is a research diagnostic only. It cannot yet be used to conclude that the Strategy A/SP2L system is intrinsically loss-making because:
1. only 6 outcomes are decisive;
2. Forward and Backtest signal sets are not yet fully reconciled;
3. the Forward execution lifecycle is research-only and non-canonical;
4. the acquisition paths differ (`copy_rates_from_pos` vs `copy_rates_range`).

## Next required forensic step

Capture a synchronized rolling-bar snapshot using the same MT5 terminal at the three genuine uptime misses (10:07, 11:55, 12:45 UTC) and compare the last 6 bars against the Backtest range data.

The snapshot must record:
- raw `time` integer for every bar;
- UTC interpretation;
- OHLC/tick_volume;
- array order;
- latest/current bar identity;
- detector result;
- source method (`copy_rates_from_pos` and `copy_rates_range`) if both are available at the same wall-clock moment.

Do not change SP2L geometry until this comparison is complete.
