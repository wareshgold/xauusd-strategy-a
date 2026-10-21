# RR2/TRAIL4 Live Trailing Baseline Audit
Date: 2026-10-21
Review type: source-aligned static audit; no live runner/config changed.
Source snapshot inspected: `7e79cae35e2c59b719df0ba765a00af14ae78b0d` (runner source); local forward-test worktree reported the same HEAD. The user's active forward event log is evidence in the conversation, not copied into this public repository document.

## Decision

**Do not change the live trailing parameter and do not run the existing matrix as if its defaults reproduce the live baseline.** The current unit contract and activation semantics must be frozen first; then reproduce the observed-forward baseline before comparing exit alternatives.

## Source-confirmed current behavior

The RR2/TRAIL4 configuration declares:

- `TRAIL_PIPS = 4.0`
- `XAU_PIP_SIZE_PRICE = 0.1`
- `TRAIL_DISTANCE_PRICE = TRAIL_PIPS * XAU_PIP_SIZE_PRICE = 0.40`

This means the current config's named “4 pips” is a 0.40 XAUUSD price-unit offset. It does **not** use the user's separately documented point convention (1 MT5 point = 0.01 price units) for this conversion. This is a naming/unit-contract discrepancy requiring explicit documentation; it is not, by itself, proof that either convention is the intended strategy rule.

The runner source applies the following behavior:

1. Reads the most recently completed M1 candle (bar index 1; the forming bar is excluded).
2. Uses that candle's high for BUY and low for SELL.
3. Uses `TRAIL_DISTANCE_PRICE` both as the favorable-move activation threshold and as the offset:
   - BUY: activation requires `bar_high - entry >= 0.40`; candidate SL is `bar_high - 0.40`.
   - SELL: activation requires `entry - bar_low >= 0.40`; candidate SL is `bar_low + 0.40`.
4. Only tighter SL values are eligible. The runner checks current Bid/Ask and broker stop/freeze distance before sending `TRADE_ACTION_SLTP`; TP is passed through unchanged.
5. It logs the requested SL and the MT5 send result. The inspected code does not follow the request with an independent read-back of the position to prove that the broker's currently applied SL exactly equals the requested value.

The forward log excerpt supplied for this audit records `trail_distance_price: 0.4` and successful `TRADE_ACTION_SLTP` retcodes. This confirms the requested offset and successful modification responses in those events; it does not alone prove the unit naming is appropriate or that the exit policy has positive net expectancy.

## Existing historical matrix is not yet a live-baseline replay

The existing research matrix on `research/rr2-trail4-trailing-matrix-20261013` has useful properties: deterministic price-distance grids, one shared M1 dataset, and newly computed stops taking effect only from the next completed bar.

However, its default activation grid is `0.05, 0.10`, while the live runner's activation threshold is tied to the distance and currently equals `0.40`. Its distance grid includes `0.40`, but those default combinations do not reproduce the live activation rule. Even a `0.40 / 0.40` grid row would still be only a theoretical-candidate OHLC counterfactual, not a one-to-one replay of actual pending-order fills and broker-observed forward outcomes.

The matrix also documents that spread, commission, swap, slippage, broker gap fills, and 2X entries are excluded. Therefore its gross outcomes cannot establish whether the current policy's small exits are net-profitable or whether a wider offset is better after costs.

## Required Stage 0 work, in order

1. **Freeze the unit contract without changing historical labels.** Record separately MT5 `point`/digits/tick metadata, the config's `XAU_PIP_SIZE_PRICE`, `TRAIL_PIPS`, computed price distance, and actual runner activation threshold. Do not silently convert old artifacts.
2. **Build a baseline identity/replay check.** Match observed runner-owned position/deal IDs, actual entry and exit prices/times, applied SL/TP changes, commissions, swap, and final net result. Preserve the original event log and its hash.
3. **Inspect post-exit price path** on reliable M1/tick data for matched trades. Report MFE/MAE after entry and after trailing updates where the data supports it; do not infer intrabar ordering from OHLC alone.
4. **Separate the estimands:** observed-forward results, counterfactual exits for actual fills, and theoretical signal-population simulations must have separate labels and reports.
5. Only after baseline reconciliation, define a versioned research-only matrix with activation and distance independently named in explicit **price units**. Include the unchanged live baseline and cost sensitivity. Freeze the candidate selection rule before untouched validation and fresh holdout.

## Non-scope / safety

- No runtime, strategy geometry, entry, SL anchor, pending order, TP, trailing, or MT5 behavior was changed by this audit.
- No live order or BUY/SELL decision was generated.
- No new matrix was run; no “best” distance is recommended.
- The live runner must remain uninterrupted during the current observation window.
- This RR2/TRAIL4 variant remains research-only, not canonical source-confirmed Strategy A.
