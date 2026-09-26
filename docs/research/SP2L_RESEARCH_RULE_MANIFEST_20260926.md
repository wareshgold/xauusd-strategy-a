# SP2L Research Rule Manifest — 2026-09-26

## Purpose

This manifest is the source-aligned boundary for research/backtest work as of 2026-09-26.

It is a **research contract, not canonical Strategy A geometry**. Source meaning outranks implementation and backtest performance. A field marked UNRESOLVED must not be silently filled by an implementation assumption.

## Source hierarchy

1. Official author material
2. Repository evidence/fixtures that directly preserve source meaning
3. Research implementation, diagnostics, and backtests

Performance cannot promote an unresolved source field.

## Source-confirmed relations

| Feature | Status | Source-confirmed statement |
|---|---|---|
| F12 bullish trigger reference | SOURCE-CONFIRMED | In an uptrend, corrective candle reaches the Low of the previous candle. |
| F15 bearish trigger reference | SOURCE-CONFIRMED | In a downtrend, corrective candle reaches the High of the previous candle. |
| F13 2X placement relation | SOURCE-CONFIRMED | Secondary entry is at 50% of the Entry-to-SL distance. |
| F10 SL structural anchor | SOURCE-CONFIRMED | SL is behind the candle from which the Spike originated. |
| F14 AB=CD concept | SOURCE-CONFIRMED | AB=CD is described as a strategy concept. |

## Explicitly unresolved

| Feature | Status | Must NOT be invented |
|---|---|---|
| P-Gap exact formula | UNRESOLVED | OHLC indexing, offsets, tolerance, universal equation |
| Trigger semantics | UNRESOLVED | touch vs penetration vs cross vs close |
| Trigger candle indexing | UNRESOLVED | exact multi-candle indexing beyond source wording |
| Entry price anchor | UNRESOLVED | exact executable price |
| Fill semantics | UNRESOLVED | pending/market behavior and intrabar fill ordering |
| F10 exact SL boundary | UNRESOLVED | wick/body/open/close/buffer |
| F13 order lifecycle | UNRESOLVED | order type, timing, sizing, cancel/replacement |
| F14 AB=CD anchors | UNRESOLVED | A/B/C/D OHLC anchors |
| F14 equality tolerance | UNRESOLVED | Leg1=Leg2 tolerance |
| Bearish complete execution mirror | UNRESOLVED | inferred mechanical mirror is not source evidence |
| Cancellation/expiry | UNRESOLVED | no deterministic threshold promoted |

## Current research detector compatibility

The shared detector currently used by MT5 research backtest/forward paths is an **Author-Replica candidate**, not canonical Strategy A.

Current candidate parameters/assumptions:
- P-Gap price parameter: 1.0
- Spike multiplier: 1.5
- Maximum SL distance: 10.0
- TP: 1R
- detector window: candles[-5], [-4], [-3], [-2]
- bullish entry: trigger Low
- bearish entry: trigger High
- bullish SL: spike Low
- bearish SL: spike High

These are implementation parameters of the existing research candidate. They are **not promoted by this manifest** as source-confirmed rules.

## Backtest gate

Any new historical result must record:
- manifest revision/date;
- exact detector implementation used;
- all research parameters;
- source status of every geometry/execution field;
- MT5 acquisition API;
- symbol actually returned by the terminal;
- timestamp basis;
- session filter state;
- outcome/fill assumptions.

A backtest that does not preserve these fields is not eligible as evidence for canonical Strategy A.

## Current gate state

- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF

## Evidence checkpoint

Primary source-evidence delta:
3778152049ec374830769007ed91f84b301187bb

Official author pages recorded by that checkpoint:
- https://poursamadi.com/sp2l-strategy/
- https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

No P-Gap formula, exact SL boundary, AB=CD anchors/tolerance, fill semantics, or execution lifecycle is promoted by this manifest.

Generated: 2026-09-26
