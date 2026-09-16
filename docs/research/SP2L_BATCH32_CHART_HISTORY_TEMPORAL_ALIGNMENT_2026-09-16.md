# SP2L Batch 32 — Chart/History Temporal Alignment Boundary — 2026-09-16

## Purpose

Determine whether the visible chart time axis in the May 12 worked-trade screenshots reaches the same timestamps shown in the account/history rows, so that an event-level chart-candle → order/fill mapping can be reconstructed without inference.

This is a research-only forensic artifact. It does not define canonical execution semantics.

## Direct visual observations

The supplied primary-video worked-trade montage contains multiple chart/account snapshots from approximately 58:00–67:30.

### Chart time ranges visible in the worked screenshots

- In the account/position screenshot around the 59:30 teaching segment, the visible chart axis spans approximately `12 May 10:28` through `12 May 12:20`.
- In later worked-trade screenshots around the 65:00–67:30 segment, the visible chart axis advances into the approximately `12 May 12:34`–`12 May 12:53` region.
- The readable history table in the same later screenshots contains rows at `2025.05.12 12:56:02`, `12:56:24`, `12:56:58`, and `12:57:06`.

Therefore the readable history timestamps occur after the latest clearly visible chart-axis region in those screenshots. The screenshot set does not show the chart continuing through the 12:56–12:57 event window with sufficient timestamp/price resolution to identify the exact candle for each history row.

## What can be aligned

The following cross-view identities are directly observable:

- Same XAUUSD instrument/context.
- Same general price region around the 3213–3238 levels.
- Repeated entry/SL/TP values across position and history tables, including:
  - `3229.08 / 3237.73 / 3213.37`
  - `3223.84 / 3235.50 / 3213.37`
  - `3228.88 / 3235.50 / 3213.37`
  - `3232.41 / 3237.80 / 0.00`
- The history contains a tight cluster of records at `12:56:02` and later records for `3232.41` at `12:56:24`, `12:56:58`, and `12:57:06`.

These observations establish cross-view consistency of displayed account values and chronological ordering of history records.

## What cannot be aligned from the artifact

The available screenshots do not establish:

1. The exact chart candle corresponding to each `12:56:xx` history event.
2. The semantic meaning of the history `Time` field (creation, execution, close, modification, or another platform event) for each displayed row.
3. Whether the three `12:56:02` rows represent three independent fills, a grouped account action, or another platform-history representation.
4. Whether the `3232.41` rows at `12:56:24/58/06` are separate fills, closes, modifications, or other events.
5. Whether any displayed history row was preceded by the `Buy Limit` / pending-order state visible elsewhere in the video.
6. A deterministic intrabar activation rule (touch, wick penetration, close, next-bar confirmation, etc.).
7. Bid/ask, spread, slippage, partial-fill, or order-priority semantics.

## Forensic conclusion

The temporal alignment attempt reaches a **source-resolution boundary** rather than a geometry resolution.

The evidence is sufficient to say:

`worked chart context → account positions → chronological history records`

but not sufficient to say:

`specific chart candle → specific pending order → specific fill event → specific history row`.

The missing bridge is not safely recoverable from the displayed timestamps because the chart's visible time axis does not extend through the relevant 12:56–12:57 history cluster in the inspected screenshots.

Accordingly, no event-level fill rule is promoted and no canonical lifecycle transition is inferred.

## Fixture impact

- **F9:** chronological executed-state evidence strengthened; exact activation/fill event remains unresolved.
- **F11:** chronological history evidence strengthened; pending → fill → management causality and lifecycle precedence remain unresolved.
- **F12:** no additional canonical trigger taxonomy evidence.
- **F13:** no additional canonical 2X formula/sizing evidence.

## Gate impact

**Source Resolution: PARTIAL PASS — temporal cross-view consistency established, event-level bridge unavailable.**

**Frozen Geometry: BLOCKED.**

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant, canonical geometry, execution rule, or production behavior was changed.