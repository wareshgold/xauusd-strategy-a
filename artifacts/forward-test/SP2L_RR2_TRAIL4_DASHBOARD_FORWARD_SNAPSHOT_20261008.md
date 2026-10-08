# SP2L RR2/TRAIL4 Forward Snapshot — 2026-10-08

## Purpose

Official observational snapshot of the active SP2L RR2/TRAIL4 demo forward session after Dashboard open/closed trade visibility was verified.

This snapshot records runtime/evidence state only. It does not define or freeze new canonical Strategy A geometry, execution semantics, or production rules.

## Repository / Dashboard

- Repository: `wareshgold/xauusd-strategy-a`
- Dashboard commit: `615430716e3457eda0ad5a57872010d87971fd97`
- Dashboard feature: read-only MT5 open positions and closed trades for Strategy A magic `26092201`
- Closed-trade window: last 24 hours
- Dashboard auto-refresh: 5 seconds
- Dashboard verification: PASS

## Active Forward Profile

- Worktree: `xauusd-strategy-a-rr2-trail4`
- Runner version: `SP2L_V3_XAUUSD_RR2_TRAIL4_20261001`
- Runner observed HEAD: `46ddf7f5cc9610975d26a60faa06f3b30db81d59`
- Runner PID observed: `12332`
- Symbol: `XAUUSD.ecn`
- TP_R: `2.0`
- TRAIL_PIPS: `4.0`
- TRAIL_DISTANCE_PRICE: `0.4`
- 2X: OFF
- Canonical: false
- Session policy: ALL_MARKET_HOURS

## Dashboard Runtime Verification

- Runner: alive
- Watchdog: not running
- Execution mode reported by live runner: LIVE-DEMO
- MT5 terminal: connected
- Account: DEMO
- Open Strategy A trades at capture: none
- Closed Strategy A trades shown: 8 within last 24h

## Verified Trailing Observation

Position `63000619`:

- Direction: BUY
- Entry: `4126.63`
- Original SL: `4121.83`
- TP: `4136.50`
- Trail update event: `2026-10-08T08:08:03.509655+00:00`
- Completed bar high: `4128.01`
- Completed bar low: `4126.13`
- New SL: `4127.61`
- Trail distance price: `0.40`
- Success: `true`
- MT5 retcode: `10009`
- Broker comment: `Request executed`

A subsequent POSITION_LIFECYCLE event at `2026-10-08T08:08:05.518401+00:00` reported current price `4127.86`, SL `4127.61`, and floating profit `1.23`, confirming the updated SL was visible in subsequent position state.

The dashboard later showed position `63000619` closed at `4127.51` with net `+0.83 USD`.

## Closed Trades Observed in Dashboard

| Position | Direction | Entry | Exit | Net USD |
|---|---|---:|---:|---:|
| 63000619 | BUY | 4126.63 | 4127.51 | +0.83 |
| 62995153 | BUY | 4124.89 | 4122.48 | -2.46 |
| 62970254 | BUY | 4115.24 | 4110.19 | -5.10 |
| 62968187 | BUY | 4112.00 | 4111.29 | -0.76 |
| 62938852 | BUY | 4097.75 | 4097.85 | +0.05 |
| 62937927 | SELL | 4094.64 | 4097.67 | -3.08 |
| 62929902 | BUY | 4092.95 | 4087.76 | -5.24 |
| 62889422 | SELL | 4121.64 | 4123.76 | -2.17 |

## Scope / Integrity Notes

- Dashboard is read-only and does not place orders.
- No active RR2/TRAIL4 runner restart or stop was performed for this snapshot.
- No cleanup/reset/stash/mass commit of local research artifacts was performed.
- The known MT5 history server-time behavior remains an implementation/reconciliation issue in the older runner telemetry path; Dashboard history reads use the broker/server-clock-compatible query.
- This snapshot is observational evidence and is not a canonical Strategy A rule decision.
- Forward observation should continue unchanged after this snapshot.
