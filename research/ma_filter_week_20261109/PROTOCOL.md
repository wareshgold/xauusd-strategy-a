# MA Filter Research — Week of 2026-11-09

Status: research-only proposal. No canonical SP2L rule is changed.

## Objective

Measure whether M1 moving-average context improves the existing V3.1 entry population, and whether any effect interacts with trade management. The first comparison is the actual V3.1 runner population from 2026-11-09 through the last complete available session, not a synthetic replacement.

## Data gate

1. Export runner deals for the exact XAUUSD.ecn symbol and XAU magic 26092301 from the same MT5 terminal/account used by the runner.
2. Export M1 OHLCV from that same terminal for the identical UTC interval, including enough pre-window warm-up bars for the longest MA (at least 250 bars).
3. Preserve raw exports unchanged; record account/server/terminal identity, UTC boundaries, counts and SHA-256.
4. Do not infer trades from the dashboard. Deals are raw execution evidence; group by position_id for position-level outcomes, preserving entry/exit deal rows and costs.
5. The local export must be run on Factory PC. GitHub/cloud code cannot read the user's local MT5 terminal directly.

## Filter candidates

All features use only completed M1 bars. For an entry decision at time t, use the latest bar whose close time is no later than t. The exact alignment must be tested and logged; no current/incomplete candle and no future data.

Baseline:
- F00: no MA filter.

Single MA price-side:
- F01/F02: close above/below SMA50 / SMA100.
- F03/F04: close above/below EMA50 / EMA100.
- F05/F06: close above/below SMA20 / SMA200.
- F07/F08: close above/below EMA20 / EMA200.

Dual MA agreement:
- F09: price and SMA50/SMA100 agree on direction.
- F10: price and EMA50/EMA100 agree on direction.
- F11: SMA50 above SMA100 for BUY / below for SELL (and price on matching side of both).
- F12: EMA50 above EMA100 for BUY / below for SELL (and price on matching side of both).
- F13: permissive OR: at least one of MA50/MA100 price-side tests agrees with direction. Keep separate from AND.

Slope / trend-strength variants:
- F14/F15: MA50 rising for BUY / falling for SELL (SMA / EMA separately).
- F16/F17: price-side MA50 plus matching MA50 slope (SMA / EMA separately).
- F18: MA50/MA100 stack direction plus both slopes aligned.

The filter definitions are hypotheses, not canonical rules. For every filter record pass/fail and exact feature values at each candidate entry. Do not silently change strictness or equality behavior; equality is neutral/reject for directional filters and is reported separately.

## Comparison plan

Stage A — actual runner audit:
- Reconstruct position-level results from raw deals, including commission, swap and fee.
- Report open positions separately; do not treat them as closed outcomes.
- Compare actual closed positions and the same actual entry population under each MA filter. A filtered trade subset is a diagnostic counterfactual, not proof of executable performance.

Stage B — offline management comparison:
- M0: reproduce the current ACT40 + TRAIL40 behavior only after its exact source semantics and broker constraints are pinned from the existing runner implementation and event evidence.
- M1/M2/M3/M4: fixed RR 1/2/3/4 candidates only after entry, initial SL, fill, spread, commission, stop/target touch ordering and same-bar ambiguity semantics are specified and fixture-tested.
- Never invent fill semantics, initial-SL anchors, or intrabar ordering. If unresolved, mark the management result blocked rather than guessing.

## Reporting

For each filter × management candidate: N, closed N, open N, win rate, gross/net P&L, PF, expectancy per position, max drawdown, losing streak, exposure, and excluded winners/losers. Show raw baseline beside each filtered result. Include paired trade-level deltas where trades overlap.

## Statistical controls

- Keep the first observed week as exploratory/development evidence, not a fresh holdout.
- Avoid selecting a winner from 19 filters × 5 management variants without multiple-comparison controls.
- Report confidence intervals and bootstrap by trading day (not individual deals) where sample size permits.
- Follow with a separately frozen untouched validation window, robustness/stability checks, then a fresh holdout.
- No production BUY/SELL decisions and no live runner changes.

## Local export

See `scripts/research/export_mt5_ma_filter_week.py`. It requires explicit terminal path, expected login and server to avoid accidentally reading another MT5 instance. It only reads history and M1 rates; it does not submit or modify orders.
