# SP2L Risk Management Boundary V1 — 2026-09-09

## Purpose

Freeze the research boundary between source-defined trade geometry and account-level risk management. This is a research contract, not a production trading rule.

## Core separation

The deterministic pipeline is:

`Source setup → Entry + Structural Invalidation → Stop Price → Stop Distance → Position Size from Risk Budget`

A risk budget such as 1% of equity does **not** select the structural invalidation level. It selects the amount of capital that may be lost if the structurally defined stop is hit.

## Strategy responsibilities

Strategy A must determine, once source geometry is frozen:

- whether a valid setup exists;
- executable Entry price and order type;
- structural invalidation condition;
- stop-price semantics derived from that invalidation;
- Leg 1 / Leg 2 geometry;
- target/exit logic supported by the source.

These are strategy semantics and cannot be changed to satisfy a desired account-risk percentage.

## Risk-management responsibilities

Risk management may determine:

- account risk budget;
- position size from the approved stop distance;
- maximum exposure constraints;
- broker/instrument sizing constraints;
- portfolio-level limits.

Conceptually, for a linear price-value model:

`PositionSize = AccountRiskAmount / (StopDistance × ValuePerPriceUnit)`

The exact XAUUSD contract-value calculation must be defined separately from source geometry and verified against the execution venue.

## Prohibited coupling

The following are not allowed:

- moving SL closer because the chosen risk percentage would otherwise be too large;
- choosing an SL distance from Entry solely to produce a desired R multiple;
- using ATR or another volatility metric as a stop substitute unless independently source-confirmed and approved;
- selecting a wick/body anchor because it improves backtest results;
- replacing structural invalidation with a fixed point/percentage distance;
- allowing position-size constraints to silently redefine the Strategy A setup.

If the structural stop produces unacceptable size, the risk engine may reject/reduce the trade according to an explicitly approved risk policy; it must not rewrite Strategy A geometry.

## Current source status

**Confirmed:** structural invalidation exists and is distinct from Entry.

**Unresolved:** exact OHLC invalidation anchor, wick-vs-body semantics, stop buffer/offset, and any execution-specific adjustment.

Therefore no production stop formula is frozen by this document.

## Synthetic fixture requirement — F10

F10 must test at least these competing interpretations:

1. structural invalidation anchor vs risk-budget-derived stop;
2. wick extreme vs body edge;
3. base/deeper structural swing vs relevant/current swing;
4. unchanged structural stop when the risk budget changes;
5. changed position size when the risk budget changes while Entry/Stop remain unchanged.

Expected invariant:

> Changing the risk budget may change position size, but must not change the source-defined Entry or structural invalidation/Stop geometry.

If source evidence cannot uniquely resolve the stop anchor, the result remains **UNRESOLVED** and no historical optimization is permitted to choose it.

## Gate impact

This boundary strengthens the SYNTHETIC FIXTURES gate but does not pass FROZEN GEOMETRY. DEV, VAL, robustness, Fresh Holdout, and Production remain locked until source geometry is frozen.
