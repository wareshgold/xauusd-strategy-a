# SP2L V3.1 RR4 / ACT40 — Working-State Evidence Snapshot

- Snapshot recorded (Tehran): 2026-11-03 10:55:16 +03:30
- Classification: DEMO / RESEARCH ONLY
- Strategy canonical status: `canonical=false`
- Version: `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101`
- Symbol: `XAUUSD.ecn`
- Configuration: P-Gap 1.0; spike multiplier 1.5; max SL distance 10; TP_R 4; trail 4 pips; trail distance 0.4; pending-limit research mode; 30-minute pending TTL.
- Active Runner worktree: `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-trailing-retry-20261103`
- Runner script SHA-256 observed in the operator's prior local snapshot: `1E50F4AC41A397BB0FFA7DA7A2A2678E7066FCB1634DFD7190DA4D219812DE49`
- Monitor: filesystem-only, bound through `SP2L_RUNNER_ROOT`; Tehran display uses UTC+03:30; no MT5 initialize/query/shutdown.

## Evidence observed

The V3.1 Event JSONL supplied for this review contained 16 events at the time of the operator's inspection. One complete position lifecycle was independently reconstructed:

1. SELL entry: 3916.60; initial SL: 3925.66; TP: 3880.06.
2. One trailing attempt was deferred with reason `CURRENT_QUOTE_OR_BROKER_DISTANCE`.
3. Retry updated SL from 3925.66 to 3915.59; MT5 retcode 10009 (`Request executed`).
4. A second update moved SL from 3915.59 to 3914.65; MT5 retcode 10009.
5. Subsequent position lifecycle events reflected both updated SL values.
6. The position exited by SL at 3914.67. Gross profit +1.93; commission -0.05; swap 0; net +1.88.
7. Telegram lifecycle notification returned HTTP 200 for the observed entry and exit.

The monitor was started at `http://127.0.0.1:8791` and its API returned the intended Runner data root. At startup verification, Runner PIDs before and after Monitor restart were identical (`11352,9088`); the Monitor process was PID `4672`. This verifies that the controlled Monitor restart did not restart the Runner at that time.

## Assessment and limits

**No defect was observed in the single supplied V3.1 trade lifecycle or in the Monitor root-binding check.** The observed order, fill, trailing modifications, stop-loss exit, net result, and Telegram acknowledgements were internally consistent.

This is not proof that the version is bug-free, nor a statistical validation of the strategy. The evidence covers one completed demo trade and a bounded event-log snapshot. It does not prove current broker inventory, future runtime stability, canonical Strategy A geometry, or a statistical trading edge. The dashboard deliberately does not query MT5 to avoid interfering with the Runner's terminal connection.

## Operational guardrails

- Do not stop, restart, edit, or redeploy the active Runner as part of Monitor work.
- Keep the Monitor filesystem-only and bind it to the explicit Runner root.
- Display event timestamps in Tehran time (UTC+03:30).
- Surface explicit errors, retries, deferred operations, and data-integrity problems with timestamp, event type, symbol, order/position/deal identifiers, retcode, comment, last error, attempt count, and retry state when present.
- Do not label a deferred/retried operation as a final failure unless a terminal failure is recorded.
- Keep all assessments research-only while `canonical=false`.
