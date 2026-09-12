# G333 — Entry / Leg Visual Audit

Date: 2026-09-12
Parent gate: G332
Source segment: `01:02:41–01:04:32`
Source video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Objective

Resolve the highest-value remaining source question: whether the correction/leg-origin point, the pending-limit entry price, and the Leg-1 measurement anchors are the same point.

This audit uses direct source-video frames and the source transcript. It does not use historical performance.

## Direct frame evidence

### F3859 — 01:04:19

Frame SHA-256:
`a7aa9b16bffb3209a6ebab728fae0ab93f229fc7d6ec8f37638ab064b70593a6`

The source displays a short red horizontal order marker at a lower-high area after the downward sequence has already developed.

This is temporally aligned with the presenter saying, approximately at `01:04:19`, that the order is placed and then pulled downward until activation.

### F3868 — 01:04:28

Frame SHA-256:
`91140cd04c7a84ce48f21e90ddb102d5626b2063def9cb99a8d9666faad3f4a0`

A red vertical measurement/position annotation appears over the newly developed downward move. Its upper anchor is materially above the contemporaneous order marker seen in the preceding frames.

This is important because it visually separates the measured deep-leg movement from the later pending-limit marker.

### F3871 — 01:04:31

Frame SHA-256:
`8a50db374defd08d16ac4430d8995cc94fa1dc93501d64dc76906e56ccef4a0c`

The red measurement rectangle is now positioned over the post-entry downward sequence, while the chart continues lower.

### F3872 — 01:04:32

Frame SHA-256:
`f65aef8f98c5be98d6a4c9f59df96c05221c9fa07acbd8d0f49d1f5de50ed17d`

The measurement annotation remains visible and the lower horizontal target/level marker is visible below the measured segment.

The presenter states at approximately this timestamp that the TP for the position was at the lower level for R1 and that R2 was also possible.

## Transcript bridge

At `01:04:00`, the presenter says the deep leg starts at a specific earlier point.

At `01:04:10`, the presenter counts seven lower highs.

At `01:04:19`, he says he places the order at the selected lower-high area and moves it downward until it becomes active.

At `01:04:32`, he states that the Leg 1 was from one earlier point to another point and identifies the position TP at the lower target for R1, with R2 also possible.

## Source-supported distinctions

The combined visual + verbal evidence supports the following distinctions:

1. **A deep-leg origin exists before the final pending-limit placement.**
2. **Multiple lower highs are used as successive candidate entry locations.**
3. **The pending-limit marker is moved downward as later lower highs form.**
4. **The pending-limit entry marker is therefore not automatically identical to the deep-leg origin.**
5. **The measured Leg-1 geometry is presented separately from the pending-limit marker.**

This is the strongest source evidence so far for the project rule:

`entry_price != automatically C`

and against the shortcut:

`fill_price = geometric C`

## What is still unresolved

The frames do not yet justify freezing exact candle-index anchors for A, B, and C because the presenter uses chart-relative visual references and the screen does not expose a machine-readable coordinate label for every anchor.

Specifically unresolved:

- exact candle index for deep-leg A;
- exact candle index for Leg-1 B;
- whether B is defined by the extreme wick, candle close, or another source-specific point;
- exact C definition for the AB=CD projection;
- exact relationship between the pending-limit fill and B/C;
- exact R1/R2 target construction in price units;
- whether the displayed R1/R2 is a risk overlay independent of the geometric AB=CD target.

## Updated source interpretation

The source now supports a symbolic separation:

`Deep Leg / Leg-1 geometry`  ≠  `Pending-limit entry marker`

and therefore the implementation must not derive the target by measuring from the eventual fill unless a separate source passage explicitly says so.

The source-confirmed target concept remains:

`Leg2 magnitude = Leg1 magnitude` / `AB=CD`

but the executable A/B/C anchor specification remains unresolved.

## Gate result

`G333 = PASS (entry-vs-leg distinction strengthened)`

`PENDING_LIMIT_ENTRY = SOURCE-CONFIRMED`
`ENTRY_MOVES_WITH_SUCCESSIVE_LOWER_HIGHS = SOURCE-VISUAL SUPPORTED`
`ENTRY != C = SOURCE-SUPPORTED AS A NON-EQUALITY RULE`
`AB=CD = SOURCE-CONFIRMED`
`EXECUTABLE_A/B/C_ANCHORS = UNRESOLVED`
`FROZEN_GEOMETRY = BLOCKED`
`DEV = BLOCKED`
`VALIDATION = PROTECTED`
`FRESH_HOLDOUT = NOT AUTHORIZED`
`PRODUCTION = BLOCKED`
