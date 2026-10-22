# Strategy B — PythonTraderBot SP2L source audit (2026-10-22)

Status: research-only. This document does not authorize live orders or freeze all execution semantics.

## Source of truth under review

- Backtest notebook: https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/SP2L2_Optimized_BackTest.ipynb
- Live bot: https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/SP2L_Advanced_Bot_Optimized.py
  - Retrieved source blob SHA: `14c936ed1810e8101a4ead74f3536ae6f3a6e4f5`
- MT5 wrapper: https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/Meta.py
  - Retrieved source blob SHA: `4743a64e864acdf3463e3fd433e71735a48e8736`
- Telegram helper: https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/TelegramBot.py
  - Retrieved source blob SHA: `c75e2e4f71f86cfee161607541f764f4e0147f4f`

The notebook is an offline tick-replay/live-loop-aligned state machine; the live bot is a separate implementation. They must be reconciled rather than assumed byte-for-byte equivalent.

## Source-declared configuration

Notebook settings reviewed:
- Symbol: `XAUUSD`; timeframe: M1; history length: 10,000 bars.
- Spike multiplier: 1.5.
- P-Gap: 100 broker points; max SL distance: 1,000 broker points.
- Backtest risk per trade: 100 account-currency units (backtest sizing only; not a live lot instruction).
- TP_R: 0.9.
- Second entry: disabled.
- Candle-colour filter: enabled.
- EMA filter: enabled, period 60; EMA60/EMA200 alignment filter disabled.
- Trend-structure filter: enabled.
- Realistic execution model enabled; simulated spread 30 points; simulated slippage 0.
- Tick data is preferred/used when valid data is available; OHLC fallback is explicitly an estimate.
- Live-loop replay interval: 0.5 seconds; deterministic phase 0.5 seconds.
- Exact state-machine option says a newly detected setup is not entered in the same polling loop; an existing pending setup is checked first.
- Forming M1 candles can be rebuilt from chronological Bid/Ask ticks. In OHLC fallback, intrabar order is unknown and SL is prioritized if SL and TP are both touched in one candle.
- Naive timestamps default to `Etc/GMT-3` in the notebook.

Live bot settings reviewed:
- `SYMBOL="XAUUSD"`, M1, `NUMBER_OF_DATA=500` (not the notebook's 10,000).
- `SPIKE_CANDLE_SIZE=1.5`, `PGAP_POINTS=100`, `MAX_SL_DISTANCE_POINTS=1000`.
- `TP_R=0.9`; `USE_SECOND_ENTRY=False`.
- `USE_EMA_FILTER=True`, `EMA_PERIOD=60`; `USE_TREND_FILTER=True`, `MAX_OPPOSITE_MOVES=1`.
- `USE_RANGE_FILTER=False`, ADX-rising filter disabled, session filter disabled.
- `USE_LOWERLOW_HIGHERHIGH_SL=False`: the default SL anchor is the candle immediately before the spike (BUY low / SELL high).
- `MAGIC=8`, `SECOND_ENTRY_MAGIC=9`, `LOT=0.01`, loop interval 0.5 seconds.
- Runtime P-Gap and maximum SL prices are computed as points multiplied by the connected symbol's broker point.
- The live code uses an internal pending-setup state and then submits a market deal when its trigger condition is met; this is not the same thing as placing a broker-side limit order.

## Live entry geometry visible in the bot source

Index convention in the live bot: latest/forming candle `-1`, post-spike candle `-2`, spike candle `-3`, candle before spike `-4`.

BUY detector requires:
- latest low < previous low;
- open and close of each of candles `-2` and `-3` rise relative to the prior candle as coded;
- candles `-2`, `-3`, `-4` all bullish;
- `low[-2] > high[-4] + P_GAP_PRICE`;
- bullish body of candle `-3` is strictly greater than 1.5 times the bodies of both candles `-2` and `-4`.

SELL is the inverse:
- latest high > previous high;
- open and close of candles `-2` and `-3` fall relative to the prior candle as coded;
- candles `-2`, `-3`, `-4` all bearish;
- `high[-2] < low[-4] - P_GAP_PRICE`;
- bearish body of candle `-3` is strictly greater than 1.5 times the bodies of both candles `-2` and `-4`.

Entry trigger in the live bot uses the current/forming candle: BUY when current low is below the previous low, SELL when current high is above the previous high. The signal entry is that observed low/high; order execution then uses the current Ask for BUY or Bid for SELL. The live wrapper's optional execution-based TP path computes a fallback TP from the quote and subsequently attempts to recalculate it from actual fill. The notebook's tick replay has its own execution simulation; equivalence still needs tests.

## Explicit blockers / unresolved before any order-enabled run

1. Broker symbol: source says `XAUUSD`; the known local terminal previously exposed `XAUUSD.ecn`. The exact symbol, point size, digits, trade mode, volume step/minimum, filling mode, stops/freeze constraints and account type must be read from the connected terminal. No silent symbol substitution.
2. Source live magic values are 8 and 9. Before any order-enabled run, prove there are no existing orders/positions on the account with those magic values (and inspect any matching strategy comments). Do not silently invent a new magic while claiming exact source settings; any isolation change requires an explicit documented decision.
3. Source live lot is 0.01, while notebook risk is 100 currency units. These are different sizing conventions; notebook risk must not be converted into a live lot without an explicit source-backed rule.
4. Notebook history length (10,000) and live bot history length (500) differ.
5. Tick replay and live bot use forming-candle/intrabar state; closed-bar-only implementation would not be equivalent.
6. Notebook and live bot are separate code paths. Every geometry, filter timing, setup lifetime, post-close cooldown, SL/TP behavior, restart reconciliation and order result must be reconciled with synthetic fixtures before execution.
7. The live Telegram helper contains blank token/chat ID placeholders and a proxy configuration. Do not copy credentials or proxy assumptions; notifications must use a separate, explicit configuration and fail closed if not configured.
8. Backtest simulated spread (30 points) and zero slippage are assumptions, not verified live execution costs.
9. No source evidence here establishes that these defaults have a statistical edge. A profitable backtest cannot resolve source ambiguities.

## Required implementation gates

- Source resolution: record the notebook and live-bot differences above.
- Synthetic fixtures: test BUY/SELL geometry, strict inequalities, point conversion, entry-trigger timing, setup persistence, SL/TP, simultaneous touches, restart/reconciliation and duplicate-order prevention.
- Frozen geometry: only source-confirmed rules; retain unresolved items as blockers.
- Development: isolated Strategy B branch/worktree, dedicated config/state/event log and Telegram namespace; no edits to Strategy A runner or its evidence.
- Validation: tests and deterministic replay first; untouched validation and fresh holdout before any production claim.
- Forward test: read-only account/symbol/order/position preflight first; require explicit approval for order-enabled execution. Never start automatically or submit orders as part of setup.

## Current disposition

Research only. No MT5 order was sent as part of this audit. No existing Strategy A worktree, process, state file, event log or Telegram configuration should be changed by this branch.

## Source symbol resolution follow-up (2026-10-22)

Direct inspection of the current upstream live bot (`SP2L_Advanced_Bot_Optimized.py`, blob `14c936ed1810e8101a4ead74f3536ae6f3a6e4f5`) resolves the configuration question:

- `SYMBOL = "XAUUSD"` is a hard-coded default/configuration constant in the script, not a broker-symbol discovery or alias-resolution mechanism.
- Startup immediately calls `mt5.symbol_info(SYMBOL)`. If it returns `None`, the script calls `mt5.shutdown()` and raises `RuntimeError`. There is no fallback to `XAUUSD.ecn` or suffix matching.
- On successful startup, `BROKER_POINT` and `DIGITS` are read from that exact symbol. `P_GAP_PRICE = PGAP_POINTS * BROKER_POINT` and max-SL price is likewise points multiplied by that symbol's point. Rates, ticks, position lookups and order requests subsequently use the configured symbol name.
- Therefore, the string can technically be changed in a separate research configuration, but changing it to `XAUUSD.ecn` is a source adaptation, not an exact source-default run. Equal `point=0.01` alone does not prove full contract/execution equivalence. Do not make this substitution silently or enable orders on the basis of this check.

Read-only MT5 preflight performed by the operator on 2026-10-22:
- Terminal path matched `C:\\Program Files\\Otet Group MT5 Terminal`; connected server reported `OtetGroup-MT5`.
- `XAUUSD` was absent from `symbols_get(group="*XAUUSD*")` results.
- `XAUUSD.ecn` was present with point `0.01`, digits `2`, minimum volume `0.01` and volume step `0.01`. No `symbol_select`, order-send, or order-modification call was made by the preflight.
- Disposition: source-default symbol cannot currently be observed under its exact name on this terminal. Keep the Strategy B observer blocked until source/configuration intent and symbol compatibility are explicitly resolved. No Strategy A files or runner were changed.
