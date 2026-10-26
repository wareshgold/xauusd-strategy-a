# RR2/TRAIL4 Order-Send Path Trace — 2026-10-26

Scope: source trace only, exact research branch `fix/rr2-trail4-telegram-deal-time-20261013`. No live order was sent and no runtime was opened.

## Source chain

1. `scripts/sp2l_v3_rr2_trail4_config.py` creates a theoretical candidate: direction, trigger time, theoretical entry, SL, risk, TP=2R, and secondary entry at 0.5R adverse.
2. `scripts/run_sp2l_v3_xauusd_forward_test.py` replaces the generic runner's detector/candidate functions with that config and calls the generic runner's candidate execution path.
3. `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py::execute_candidate` constructs an approved payload and calls `gateway.execute_signal`.
4. `scripts/live_mt5_gateway.py::execute_signal` selects `PENDING_LIMIT_RESEARCH` behavior from the process environment, applies pre-send checks, builds a pending-order request, checks the double environment gate, demo account mode and symbol trade mode, calls `mt5.order_send`, and attempts to verify broker-stored levels.
5. The V3 wrapper separately runs trailing logic against the latest completed M1 bar and calls `mt5.order_send(TRADE_ACTION_SLTP)` only after its own price/stops/freeze guards.

## Source-confirmed pending-order pre-send behavior

- BUY Limit is refused when theoretical entry `>= current Ask`; otherwise order type is BUY_LIMIT.
- SELL Limit is refused when theoretical entry `<= current Bid`; otherwise order type is SELL_LIMIT.
- Risk and reward distances must both be positive relative to theoretical entry.
- When broker stop-level distance is positive, both SL and TP distances must be at least `trade_stops_level * point`.
- Request declares theoretical entry, SL and TP unchanged, configured volume/magic, GTC lifetime and RETURN filling policy.
- Acceptance gates include `LIVE_TRADING_ENABLE`, `ALLOW_REAL_EXECUTION`, demo account mode, and an openable symbol trade mode.
- A successful return code is DONE or PLACED. This is pending-order acceptance, not proof of fill.
- After acceptance, the code attempts to verify stored entry/SL/TP with tolerance `max(2 * point, 1e-12)`.

## Important source-level verification concern

The gateway's stated intent is fail-closed if broker-stored levels cannot be verified. In the pinned implementation, if verification returns `verified=false` **and the order cannot be found in the active-order query**, the code does not enter the cancellation/false-return branch; it falls through and returns `ok` based on the original DONE/PLACED retcode while including a failed verification object.

This is a source-path concern requiring a dedicated regression test and careful patch review before that gateway revision is used for any future research run. This document does not modify the live gateway or claim the behavior has been fixed. A future code fix should make missing/unverified broker order state non-accepted and emit a distinct reason, without broadening cancellation scope.

## Trailing pre-send behavior

- Only the latest completed M1 bar (shift 1) is consulted.
- Favorable movement must reach the configured trail distance.
- BUY SL must improve, remain below the completed-bar high, and be strictly below `Bid - max(stops_level, freeze_level) * point`.
- SELL SL must improve according to the source comparison, remain above the completed-bar low, and be strictly above `Ask + max(stops_level, freeze_level) * point`.
- The request uses `TRADE_ACTION_SLTP`; the source logs success only when the returned retcode is `TRADE_RETCODE_DONE`.
- Passing these guards does not prove that MT5 accepted the update; a rejected or absent response must remain an observed failure/unknown, not an assumed stop change.

## What is not established

- The pending request's future fill path, partial fills, broker-specific execution details, spread/slippage/cost assumptions and event order inside a millisecond.
- Whether a secondary 2X candidate field is actually submitted as a separate order by this path. The traced `execute_candidate` payload contains only direction, entry, SL, TP, volume, signal identity/source/status; it does not pass `secondary_entry_2x` to the gateway.
- Any canonical SP2L geometry. All described behavior is specific to this research profile and exact code revision.

## Factory disposition

The added source execution fixtures are preflight contract tests, not a replay engine. They intentionally return `REQUEST_ELIGIBLE` rather than accepted/filled whenever source guards pass. The replay gate stays BLOCKED until the verification concern, fill/cost semantics, tick ordering, candle construction and immutable dataset binding are resolved and reviewed.
