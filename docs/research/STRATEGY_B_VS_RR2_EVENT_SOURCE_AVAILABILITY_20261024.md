# Event source-availability audit — Strategy B vs RR2/TRAIL4 (2026-10-24)

**Status: source-artifact audit only. Event capture is incomplete; replay remains BLOCKED.**

This audit inspects the checked-in Strategy B source copy and the RR2/TRAIL4 runner/config from their identified research branches. It does not run either system, connect to MT5, read or alter live state, or infer missing events.

## Exact source identities

| Component | Branch / source | Identity |
|---|---|---|
| Strategy B source copy | `research/strategy-b-pythontraderbot-execution-20261022/scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py` | Blob SHA `ec275d3fef7ef372823a3626dba5f2718001c52d`; 2,268 lines inspected |
| RR2/TRAIL4 runner | `fix/rr2-trail4-pending-lifecycle-safe-20261011/scripts/run_sp2l_v3_xauusd_forward_test.py` | Blob SHA `fdfe34ed15eadf38fa0d24d4a80781357d72328d` |
| Event ledger contract | [proposed contract](./REPLAY_EVENT_LEDGER_CONTRACT_20261024.md) | Research-only schema proposal |
| Synthetic event tests | `tests/test_replay_event_ledger_contract_fixtures.py` | Deterministic synthetic cases only |

## Strategy B source copy: observed availability

The inspected file contains strategy/setup calculations, pending setup state, and a helper for querying second-entry order/position state. It does not expose a durable normalized event-ledger writer or an explicit `ENTRY_FILL` / `EXIT_FILL` record in this file.

The only `mt5.order_send(request)` occurrence found in this file is in `cancel_second_pending_order` around line 1457; the request uses `TRADE_ACTION_REMOVE` to remove a second-entry pending order. This observation must **not** be generalized to every possible wrapper/adapter outside this file.

Consequences:

- A candidate/trigger derived from this file is not proof of a market deal.
- This file alone is insufficient to reconstruct actual entry/exit deal IDs, execution timestamps, fill price/volume, commission/swap, or source event ordering.
- The broader Strategy B source audit describes a market-deal execution path, but the replay implementation must identify and pin the exact execution adapter/artifact that produces broker requests and actual deal evidence. Do not fill this gap with a candle-touch proxy without explicitly labeling and approving it.
- Until that adapter or immutable broker-history artifact is available and source-identified, event rows for actual fills/exits must remain `UNKNOWN` / `NOT_DETERMINABLE`.

## RR2/TRAIL4 runner: observed event logging

The inspected runner wraps the V3 lifecycle monitor and writes named events through `runner.log_event`. Event names observed in the inspected file include:

- `TRAIL_UPDATE` (around line 93): includes position, direction, proposed stop context, distance, success flag, and retcode. A request/attempt should be distinguished from a broker-confirmed change; the `success` and retcode fields matter.
- `PENDING_ORDER_TTL_SKIPPED` (around line 217): records a pending-expiry clock-unavailable condition.
- `PENDING_ORDER_LIFECYCLE` (around line 263): records order state and identifiers where available.
- `POSITION_LIFECYCLE` (around line 310): snapshots position identifier, direction/type, volume, open/current prices, SL/TP and profit.
- `POSITION_HISTORY_QUERY_FAILED` / `POSITION_SNAPSHOT_QUERY_FAILED` (around lines 365/284/331): diagnostic failures, not trade exits.
- `TELEGRAM_DEAL_LIFECYCLE` (around line 404): records deal/order/position identifiers, entry/reason, exit price, profit, commission, and swap.
- `POSITION_RECONCILIATION_GAP` and `SESSION_CUTOFF_DEFERRED` are also emitted in specific conditions.

This is useful lifecycle evidence, but it is not automatically a complete event ledger. The normalized adapter must inspect the base runner's `log_event` envelope and preserve its original event time, event file hash, source row reference, source sequence/order token if any, and timezone mapping status. Do not assume these fields exist simply because the wrapper logs named events.

## Availability matrix

| Required fact | Strategy B inspected file | RR2/TRAIL4 inspected runner | Current disposition |
|---|---|---|---|
| Candidate/setup | Strategy/setup logic present | Runner consumes source/config candidates | Preserve as candidate only; not a fill |
| Order submission/rejection | No complete entry-deal lifecycle in this file; external adapter/source artifact needed | Pending-order lifecycle events exist, but inspect base runner event envelope for completeness | Source-specific; no universal assumption |
| Actual entry fill | Not established by this file alone | Deal lifecycle path reads MT5 history deals | Require actual deal/source artifact; missing = `UNKNOWN` |
| SL update request vs confirmation | Not established here | `TRAIL_UPDATE` records success/retcode; request and confirmed state must remain distinguishable | Do not treat attempted update as confirmed |
| Actual exit fill | Not established by this file alone | Deal history lifecycle can carry deal/exit price/profit/costs | Require deal evidence and event references |
| Original timezone / UTC mapping | Not established by this file alone | Must inspect base event logger output and timestamp source | Preserve original timestamp; UTC unknown unless evidenced |
| Stable same-time sequence | Not established by this file alone | No sequence guarantee established by this wrapper inspection | Equal-time events without source sequence remain `AMBIGUOUS` |
| Costs | Not established here | Deal lifecycle includes profit, commission, swap | Verify completeness and accounting convention before net metrics |

## Next evidence gate

1. Identify the exact Strategy B execution wrapper/adapter and immutable deal-history artifact, with source commit/blob hash.
2. Inspect the base RR2/TRAIL4 event logger envelope and an existing immutable event sample without changing it; determine timestamp, timezone, sequence, and hash/provenance fields.
3. Define read-only adapters that map only evidenced source events into the proposed ledger; never synthesize missing fills/exits.
4. Add schema validation for required nullable fields and source-profile differences before any replay implementation.
5. Keep the paired comparison blocked until timestamp mapping, fill/exit evidence, trailing ordering, overlap, and common costs are supportable.

No live code, forward-test configuration, MT5 state, runtime, event logs, or historical evidence was changed.
