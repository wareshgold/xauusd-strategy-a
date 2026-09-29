# V2 Forward Runner Heartbeat Checkpoint — 2026-09-29

## Scope

Research-only observability improvement for the clean V2 XAUUSD forward runner.

This change does **not** alter Strategy A geometry, signal population, fill semantics, execution rules, or canonical status.

## GitHub

Branch: `research/sp2l-legacy-mirror-backtest-20260929`

Commits:
- `0568d3e45bcb6dd7ead22d5da1a8163fb7ab7968` — add heartbeat telemetry implementation
- `cb44b8740771f4b07314ac1e34921017d5f6e728` — wire heartbeat into forward loop

## Behavior

The forward runner now emits a JSONL `HEARTBEAT` event every 60 seconds by default.

Override interval with:

`SP2L_HEARTBEAT_SECONDS=<seconds>`

Set to `0` to disable heartbeat emission.

Each heartbeat records:
- process PID and uptime
- MT5 connected / trade-allowed status
- MT5 trade mode
- last observed M1 bar per configured symbol
- active MT5 pending orders and positions for configured symbols
- V2 forward-ledger status counts
- state seen/notified counts
- `canonical=false`

Events are written to:

`artifacts/forward-test/SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl`

and also printed to the runner stdout.

## Operator check

After pulling and restarting the clean V2 runner, an operator can verify liveness without a dashboard by watching the event file for new `HEARTBEAT` records.

A healthy idle process should continue producing heartbeat records even when no new signal is detected.

## Research boundary

Heartbeat telemetry is infrastructure only. It is not evidence for promoting any geometry, lifecycle, fill, or execution semantics to canonical Strategy A.
