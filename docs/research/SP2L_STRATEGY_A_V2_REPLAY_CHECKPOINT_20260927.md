# SP2L Strategy A V2 — MT5 Replay Checkpoint — 2026-09-27

## Status

**RESEARCH-ONLY CHECKPOINT — NOT CANONICAL**

This checkpoint records the first MT5-local replay of the V2 external comparator on the frozen research window. The result is evidence for reconciliation, not a strategy promotion or production decision.

## Repository context

- Branch: `research/sp2l-strategy-a-v2-2026-09-27`
- Runner commit before this checkpoint: `a836ed038ae84a401b32dfc27690ddb04044de01`
- Mode: `RESEARCH_ONLY_SP2L_STRATEGY_A_V2`
- Canonical: false
- Symbol requested: `XAUUSD`
- Broker symbol resolved: `XAUUSD.ecn`
- Timeframe: M1

## Replay window

- Start: `2026-09-14T00:00:00Z`
- End: `2026-09-25T23:59:59Z`
- MT5 terminal: Otet Group MT5
- Explicit terminal path was supplied.

## Frozen V2 research geometry

- P-Gap price threshold: 1.0
- Spike multiplier: 1.5
- Maximum accepted base risk: 10.0 price units
- TP: 1R
- Trigger BUY: current Low < previous Low
- Trigger SELL: current High > previous High
- Entry BUY: trigger candle Low
- Entry SELL: trigger candle High
- SL BUY: Low of candle before Spike
- SL SELL: High of candle before Spike
- Second entry: disabled
- EMA/ATR/ADX/trend/session filters: disabled
- Same-bar SL+TP convention: SL first
- This geometry remains a research comparator and is not source-confirmed canonical Strategy A geometry.

## Replay result

- Signals: **222**
- Trades: **204**
- Wins: **127**
- Losses: **77**
- Win rate: **62.2549%**
- Net R: **+50R**
- Simplified profit factor: **1.64935**
- Max drawdown: **6R**
- Maximum consecutive losses: **5**
- BUY: 94 trades, 59 wins, 35 losses, 62.7660% WR, +24R
- SELL: 110 trades, 68 wins, 42 losses, 61.8182% WR, +26R
- Exit reasons: 127 TP, 74 SL, 3 SL_FIRST_SAME_BAR

## Artifact

`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260927T052251Z.json`

## Interpretation boundary

The V2 result is materially different from the earlier source-aligned replay on the same date window. Earlier source-aligned evidence recorded 53 signals and 33 decisive outcomes with 12 wins, 21 losses, and -9R.

This difference is a reconciliation target, not evidence that V2 is the correct interpretation. The immediate next experiment is signal-set reconciliation:

1. identify V2-only setups;
2. identify source-aligned-only setups;
3. identify common setups;
4. compare timestamps, direction, setup candle roles, trigger timestamps, entry prices, and SL anchors;
5. inspect representative OHLC fixtures before any parameter optimization.

No parameter optimization, promotion, or production execution is authorized by this checkpoint.

## Research gate

**NEXT GATE: SIGNAL RECONCILIATION**

Do not use the +50R result to select canonical geometry. Source evidence remains higher priority than backtest performance.
