# SP2L MT5 MCP Read-Only Integration Checkpoint — 2026-09-22

## Scope

This checkpoint records empirical validation of the MetaTrader 5 Native MCP read-only path on branch `research/sp2l-f13-demo-forward-slfixed-2026-09-21`.

No canonical Strategy A geometry, signal semantics, execution semantics, or production decision logic was changed.

## Validated read-only capabilities

### Market Watch
- 20/20 successful sequential calls.
- Median latency: 5.67 ms.
- P95 latency: 9.59 ms.
- Maximum observed: 26.61 ms.

### M1 Chart History
- 20/20 successful sequential calls.
- Median latency: 5.84 ms.
- P95 latency: 7.12 ms.
- Maximum observed: 9.02 ms.

### Account Information
- 20/20 successful sequential calls.
- Median latency: 5.35 ms.
- P95 latency: 8.63 ms.
- Maximum observed: 8.74 ms.

### Open Positions
- 20/20 successful sequential calls.
- Median latency: 5.36 ms.
- P95 latency: 7.48 ms.
- Maximum observed: 8.07 ms.

### Account + Open Positions
- 20/20 successful cycles.
- Median latency: 11.93 ms.
- P95 latency: 14.36 ms.
- Maximum observed: 14.37 ms.

### Terminal / Expert Journal
- `get_terminal_journal`: successful.
- `get_expert_journal`: successful.
- Terminal journal returned 100 records with `truncated=true` in the one-hour diagnostic window, confirming journal access and observable MCP activity.
- Expert journal returned zero records in the tested window; this is an empty result, not a tool failure.

### Trading History
- `get_trading_history_positions`: successful.
- `get_trading_history_orders`: successful.
- Orders/deals/positions for XAUUSD.ecn were empty in the tested one-hour window; this is an empty history result, not a failure.

## Time handling

MCP reported:
- UTC time: 2026-09-22T12:04:23Z
- Terminal local time: 2026-09-22T15:34:23
- Reported local UTC offset: 0 minutes

Journal queries were issued using the terminal-local time required by the MCP schema. Trading-history queries used ISO UTC time.

The MCP terminal-local clock must not be assumed to equal the user's application/UI timezone.

## Safety boundary

The following trading tools were not called:
- trade_send_market_order
- trade_send_pending_order
- trade_modify_sl_tp
- trade_delete_order
- trade_close_single_position
- trade_close_by_position

Therefore this checkpoint provides no validation of MCP-based order execution.

## Architecture decision

Preferred architecture remains:

SP2L Deterministic Engine
-> local Python MT5 API
-> execution / live monitoring
-> MT5

MT5 Native MCP
-> read-only bridge
-> account state
-> positions/orders
-> OHLC history
-> journal/history audit
-> diagnostics/monitoring

NVIDIA AI
-> research / analytics / diagnostics
-> not execution
-> not canonical BUY/SELL

## Research integrity

This checkpoint does not promote any research rule to canonical status and does not modify Strategy A geometry.

The forward-test runner is not changed by this checkpoint.

## Next investigation

The next architecture investigation may evaluate whether MCP read-only data can be used as a secondary audit/monitoring source alongside the existing Python MT5 path. MCP execution remains unvalidated and outside the current production path.
