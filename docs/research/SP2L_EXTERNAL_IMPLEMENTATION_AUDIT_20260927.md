# SP2L External Implementation Audit — AlirezaSadabadi/PythonTraderBot — 2026-09-27

## Scope

Audit the public SP2L implementation in:
- code/SP2L/SP2L_Bot.py
- code/SP2L/SP2L_Advanced_Bot.py
- code/SP2L/SP2L_Advanced_Bot_Optimized.py
- code/SP2L/SP2L2_Advanced_Backtest.ipynb
- code/SP2L/SP2L2_Optimized_BackTest.ipynb

Repository:
https://github.com/AlirezaSadabadi/PythonTraderBot

## Observed reported result

The Advanced Backtest notebook reports:
- signals: 95
- trades: 89
- wins: 58
- losses: 31
- win rate: 65.17%
- total R: +27
- profit factor: 1.871
- max drawdown: -400
- BUY: 44 trades, 28 wins, +12R
- SELL: 45 trades, 30 wins, +15R

This is an observed result from the repository's own notebook output. It is not treated as independently validated evidence of a canonical SP2L edge.

## Geometry observed

The implementation uses:
- M1
- spike multiplier = 1.5
- P-Gap = 100 broker points; with point=0.01 this is price gap 1.0
- BUY P-Gap: low of candle after spike > high of candle before spike + 1.0
- SELL P-Gap: high of candle after spike < low of candle before spike - 1.0
- SL: low/high of candle before spike
- TP: 1R
- maximum SL distance: 10.0 price units

The P-Gap formula and candle-role mapping are therefore explicit in this implementation, but remain an implementation choice, not author-primary proof that this is the unique canonical SP2L P-Gap definition.

## Entry semantics observed

The Advanced Backtest searches forward from the setup for the first candle where:
- BUY: current low < previous candle low
- SELL: current high > previous candle high

It records the entry price as the current candle low/high.

The live optimized bot uses the same threshold test on the forming M1 candle and then sends a market order. Therefore:
- backtest entry price = sampled candle extreme
- live execution = market order at broker quote/execution price

This is not a proof of exact pending-order/fill semantics.

## Additional filters

The Advanced implementation defaults to:
- EMA(60) filter enabled
- trend-structure filter enabled
- max consecutive opposite moves = 1
- ADX/range filter disabled
- New York session filter disabled
- second entry disabled

These filters are not source-confirmed canonical SP2L rules in our source gate. They materially change the signal population.

## Intrabar exit semantics

The Advanced Backtest explicitly handles same-bar SL+TP as:
- BUY: if low <= SL AND high >= TP, exit at SL and label SL_and_TP_same_bar_SL_first
- SELL: if high >= SL AND low <= TP, exit at SL and label SL_and_TP_same_bar_SL_first

Otherwise it checks SL before TP.

Therefore the implementation does not resolve the true intrabar chronology. It imposes an SL-first convention.

## Implication for our research

This explains how the external implementation can produce a clean 65.17% number while our forensic harness retains ambiguous outcomes:
1. it chooses a specific P-Gap formula (+1.0 price unit);
2. it adds EMA/trend filters;
3. it defines entry as the first threshold-touch candle extreme;
4. it uses a market-order live path rather than proving pending-order fill semantics;
5. it resolves same-bar SL+TP by an explicit SL-first assumption.

None of these observations proves that the external implementation is wrong or that its reported result is fabricated. They show that its 65.17% result is conditional on a particular implementation contract.

## Research decision

Do not copy the external rules into canonical Strategy A.

Next reproducible experiment:
- port the external implementation contract into a separate research-only comparator;
- run it on the same MT5-local XAUUSD data and same date windows used by our current forensic harness;
- report signal-count differences, entry differences, ambiguity differences, and performance;
- separately test its SL-first convention against our tick-level chronology;
- do not optimize or promote any rule based on performance.

Frozen Geometry remains BLOCKED until author-primary source evidence resolves the unresolved geometry and execution semantics.
