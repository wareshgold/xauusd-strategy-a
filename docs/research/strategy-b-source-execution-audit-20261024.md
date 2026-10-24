# Strategy B source/execution audit — 2026-10-24

**Scope:** research-only audit of the Strategy B source on branch `research/strategy-b-pythontraderbot-forward-20261022`, source commit `0037c54074c6b01adfa3393fb38687be6ea074d5`. This is not a live-runner change and does not authorize production decisions.

## Source links

- [Strategy B runner at audited branch](https://github.com/wareshgold/xauusd-strategy-a/blob/research/strategy-b-pythontraderbot-forward-20261022/scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py)
- [Meta execution implementation](https://github.com/wareshgold/xauusd-strategy-a/blob/research/strategy-b-pythontraderbot-forward-20261022/scripts/strategy_b_pythontraderbot_live/Meta.py)
- [Monthly candidate replay harness](https://github.com/wareshgold/xauusd-strategy-a/blob/research/rr2-trail4-vs-pythontraderbot-monthly-matrix-20261024/scripts/research/compare_rr2_trail4_vs_strategy_b_monthly.py)

## Source-confirmed configuration

| Setting | Value in audited source |
|---|---|
| Symbol | `STRATEGY_B_SYMBOL`, default `XAUUSD.ecn` |
| Timeframe / history | M1 / 500 bars |
| Spike multiplier | 1.5 |
| P-Gap | 100 × runtime `symbol_info.point` |
| Max SL distance | 1,000 × runtime `symbol_info.point` |
| SL anchor | Previous-to-spike candle extreme; lower-low/higher-high alternative disabled |
| TP ratio | 0.9R |
| Entry style | Market order after a valid entry candidate |
| First-entry magic / volume | 8 / 0.01 lot |
| Second entry | Disabled; magic 9 path is not expected in this profile |
| EMA filter | Enabled, period 60 |
| Trend filter | Enabled, maximum opposite moves 1 |
| Range/ADX filter | Disabled |
| ADX-rising filter | Disabled |
| New York session filter | Disabled |

The source computes `P_GAP_PRICE = PGAP_POINTS * BROKER_POINT` and `MAX_SL_DISTANCE_PRICE = MAX_SL_DISTANCE_POINTS * BROKER_POINT`. Therefore the price-unit values depend on the runtime symbol's broker point; they are not hardcoded price distances.

## Entry and stop geometry

- BUY setup requires the current candle low to be below the previous candle low, the two post/pre-spike candle comparisons, three bullish candle bodies, and the source P-Gap relation.
- SELL is the mirrored high/ bearish-candle form.
- The spike body is compared to the bodies of the immediately pre-spike and post-spike candles. The detection candle's body is **not** part of that size comparison.
- With `USE_LOWERLOW_HIGHERHIGH_SL=False`, BUY SL is `low[-4]`; SELL SL is `high[-4]`, relative to the five-candle setup/detection window.
- A pending setup waits for the first entry candidate passing risk, trend and EMA checks. Risk must be positive and no greater than `MAX_SL_DISTANCE_PRICE`. No pending-setup TTL is defined in the inspected strategy logic.
- The candidate entry is the current bar low for BUY or current bar high for SELL, but the runner then sends a market order. These are not guaranteed to equal the executed fill.

## Actual order and target path

- BUY sends a market DEAL using the current Ask quote; SELL uses the current Bid quote.
- The strategy calls `Meta.SetExecutionBasedTP(enabled=True, tp_r=0.9, signal_entry=entry)` before `Meta.run(..., stopLossPure=True)`.
- `Meta.SendOrder` calculates an immediate fallback TP from the pre-order Ask/Bid and fixed SL, then sends the DEAL request with that TP.
- After an accepted result (`TRADE_RETCODE_DONE` or `TRADE_RETCODE_PLACED`), `Meta.UpdateTPAfterFill` polls positions by symbol and magic, reads `position.price_open` and the current SL, computes TP at 0.9 × actual fill-to-SL distance, rounds to symbol digits, and attempts a SLTP modification.
- If the position is not visible, the risk distance is invalid, or the TP modification fails, the code logs/skips the update; the fallback TP can remain. The source therefore targets 0.9R but does not prove every realized trade exits at exactly +0.9R.
- Exit notifications query MT5 deal history and sum profit, commission, swap and fee for the position. Those are execution records; they cannot be reconstructed exactly from OHLC alone.

## Why the M1 candidate scan is not a realized trade matrix

1. M1 OHLC does not provide the actual Ask/Bid quote at the polling instant, executed fill price, order retcode, post-fill TP modification result, commission, swap or fee.
2. The bot polls every 0.5 seconds and updates the forming candle intrabar. A bar-close replay cannot recover the precise intrabar sequence of setup detection, EMA state, entry validation, market execution and immediate SL/TP hits.
3. If a bar touches both SL and TP, OHLC alone does not identify event order.
4. Strategy A uses a pending-limit research profile with a 30-minute TTL and M1 trailing; its fill and trail path is also not established by OHLC-only candidate records.

Accordingly, the current monthly harness is a **candidate-count replay only**. Do not label its theoretical prices as fills or calculate them as realized P&L. A defensible per-trade realized matrix requires MT5 deal/order history for observed trades; a hypothetical historical matrix requires tick/quote data and an explicitly labelled execution model. Any hypothetical model must remain separate from actual forward results.

## Deterministic source-fidelity fixture

`tests/research/test_strategy_b_candidate_source_fidelity.py` verifies BUY and SELL detector fixtures where the detection candle's body is larger than the spike body threshold, while all actual source conditions pass. This protects the source rule that the spike-body ratio compares against the pre-spike and post-spike candles only. Tests import the research harness only; they do not import the live runner or MetaTrader5.
