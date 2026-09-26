# SP2L Forward vs Backtest Forensic — Step 2

Date: 2026-09-26
Status: RESEARCH-ONLY

## Finding 1 — The three misses are NOT proven uptime misses

The Forward event log has no events in these windows:
- 2026-09-24 10:00–10:15 UTC
- 2026-09-24 11:45–12:05 UTC
- 2026-09-24 12:35–12:55 UTC

The log contains START records, but START is not proof that the polling loop remained alive.

The runner writes STOP only from the `finally` block. A forced process termination, crash, terminal disconnect, or stalled loop can therefore leave START without STOP.

For 10:07 specifically:
- START at 10:01:26 UTC
- no heartbeat, candidate, error, or data event until a later START at 10:11:42 UTC

Therefore the previous Step-1 wording "genuine uptime miss" is reclassified to:

**UNRESOLVED — START observed, continuous polling NOT proven.**

The same applies to 11:55 and 12:45.

## Finding 2 — The detector itself is unlikely to be the primary cause

Backtest and Forward import the same `scripts/sp2l_author_replica_detector.py`.

The detector uses:
`candles[-5], candles[-4], candles[-3], candles[-2]`

and returns the trigger timestamp from `candles[-2]`.

The Forward runner polls a 10-bar rolling window. A qualifying completed-bar pattern should therefore remain observable for the polling interval until the rolling window advances beyond the trigger.

Because the historical Backtest independently detects the three patterns, and because the geometry implementation is shared, there is currently no evidence for geometry drift.

## Finding 3 — Acquisition-path evidence remains unresolved

Backtest:
`mt5.copy_rates_range()`

Forward:
`mt5.copy_rates_from_pos()`

The repository has already observed a +3h-looking timestamp on the rolling path, while range retrieval is treated as UTC-aligned.

We must not normalize timestamps until the two APIs are captured simultaneously from the same terminal.

## Step 2 conclusion

We cannot currently say:

- "the detector missed the signals";
- "the Forward process was definitely running";
- "the MT5 rolling API did not contain the required bars".

What we can say is:

**The historical Backtest produces the patterns, while the Forward event log contains no telemetry proving what the rolling API returned during the corresponding windows.**

That is now the primary forensic gap.

## Step 3 required instrumentation

Add a research-only heartbeat/rolling snapshot to the Forward runner. Every polling cycle should record:

1. wall-clock UTC;
2. raw `time` values of all returned M1 bars;
3. interpreted UTC timestamps;
4. OHLC for the last 10 bars;
5. array order;
6. detector result and signal_time;
7. `mt5.last_error()`;
8. current tick bid/ask;
9. elapsed time since previous poll;
10. MT5 terminal/account connectivity state.

Additionally, log explicit `DATA_SNAPSHOT`, `DETECTOR_RESULT`, and `POLL_HEALTH` events.

This will let the next forward occurrence be reconciled deterministically instead of inferring uptime from START/STOP records.

**No SP2L geometry, P-Gap, SL, TP, session, or fill rule is changed by this step.**
