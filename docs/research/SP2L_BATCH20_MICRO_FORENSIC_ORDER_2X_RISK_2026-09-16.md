# SP2L Batch 20 — Micro-Forensic Order / 2X / Risk Diagram — 2026-09-16

## Purpose

This batch narrows the primary-artifact inspection to the exact order-placement, deletion, 2X, and Entry/TP/SL teaching diagrams. The objective is to determine whether any remaining semantic can be closed without inference.

## Primary artifact observations

### 1. Pending-order placement and deletion sequence

Frames approximately 2340–2460 seconds show a bullish SP2L chart with a horizontal level and handwritten annotations including `Buy Limit`, `money`, `delete`, and numbered notes. The sequence demonstrates that a buy-limit order is placed at a horizontal level and that deletion of an order is explicitly discussed/annotated.

What this establishes:

- pending buy-limit placement is directly taught;
- order deletion is directly taught in the same instructional section;
- the order is represented as a horizontal price level on the chart.

What it does **not** uniquely establish:

- the exact condition that causes deletion;
- whether deletion means cancellation before fill, replacement by a newer level, invalidation after structure change, expiry, or another money-management action;
- whether multiple pending orders may coexist;
- whether an order is automatically replaced or manually replaced.

Status: **F11 remains unresolved at state-machine level.**

### 2. 2X geometric relation

Frame approximately 2520 seconds shows a dedicated diagram with three horizontal levels annotated `Buy`, `2X`, and `SL`. The diagram draws the 2X level between Buy and SL, with the instructional distance markers depicting the Buy→2X and 2X→SL segments as equal divisions of the Buy→SL span.

This is stronger than the earlier worked-example evidence because the primary artifact presents the relation as a dedicated teaching diagram rather than only as a chart annotation.

Safe source-level conclusion:

- `2X` is explicitly taught;
- the primary diagram visually depicts `2X` at the halfway point between `Buy` and `SL` (50% of the Buy→SL distance).

Important boundary:

The diagram alone does not establish all executable semantics. It does not uniquely specify:

- whether `Buy` means intended Entry price, filled Entry price, or order level in every context;
- whether 2X is a pending order, an additional position, a sizing instruction, or another execution action;
- exact trigger/activation condition;
- fill semantics;
- position sizing;
- cancellation/replacement interaction with the original order.

Therefore the canonical **geometric relation** can be recorded as primary-artifact-supported, while the complete 2X execution rule remains unresolved.

Status: **F13 concept + geometric 50%-relation strengthened; execution semantics unresolved.**

### 3. Entry / TP1 / TP2 / SL separation

Frame approximately 2550 seconds shows a dedicated bullish diagram with four explicitly labelled horizontal levels: `TP2`, `TP1`, `Entry`, and `SL`. The labels are attached to separate price levels on the right-hand side of the diagram.

This directly establishes that the teaching material distinguishes Entry from TP1, TP2, and SL as separate levels in the worked geometry.

It does not uniquely establish:

- exact Entry construction from A/B/C/D;
- whether Entry is a candle close, level touch, pending order price, or another activation price;
- exact TP1 formula;
- exact TP2 formula;
- exact SL price convention.

Status: **F9/F10 strengthened; executable price formulas remain unresolved.**

### 4. Round-level annotation

Frame approximately 2640 seconds contains handwritten `Round level` notes and example numeric levels around `2500`, `3000`, `3250`, and `3255`. This confirms that round levels are discussed in the primary teaching material.

However, the handwritten examples do not uniquely define the deterministic round-level algorithm, including:

- exact step size;
- whether levels are fixed, instrument-dependent, or contextual;
- distance tolerance;
- which reference price is used;
- how the level participates in candidate qualification.

Status: **Round-level concept confirmed; exact algorithm remains unresolved.**

## Gate impact

This micro-forensic pass closes no blocker at the full executable-rule level.

It does, however, materially strengthen two source facts:

1. **F13:** primary diagram support for `2X` as the midpoint of the Buy→SL distance.
2. **F9/F10:** primary diagram support for distinct Entry, TP1, TP2, and SL levels.

F11 remains unresolved because the deletion annotation does not specify the state transition condition.

No P-Gap formula, AB=CD anchor/tolerance, trigger taxonomy, swing-selection algorithm, or exact SL/Entry formula is invented or promoted.

## Non-canonical boundary

The following remain explicitly non-canonical:

- complete 2X execution/activation/fill/sizing semantics;
- Entry activation semantics;
- TP1/TP2 formulas;
- exact SL boundary;
- pending-order replacement/cancellation/expiry/invalidation state machine;
- A/B/C/D anchors and AB=CD tolerance;
- trigger taxonomy;
- swing-selection algorithm;
- round-level algorithm.

## Validation status

No backtest variant was selected from this evidence. No strategy geometry or production execution logic was changed. 125R remains untouched.
