# SP2L G219 — Measurement Affine Reconstruction

Date: 2026-09-10
Gate: SOURCE RESOLUTION
Status: STRONG SOURCE-CORRELATED CANDIDATE — NOT FROZEN

## Objective

Use an independent later source state to test whether the visible `0.0 / 2x / E / 1 / 2` measurement stack is numerically related to the terminal Order Panel's Entry and S/L values.

This pass is source-first. No backtest result is used to choose the interpretation.

## Source material inspected

Primary raw source video:
- `strtjy_sp2l_strategy_subtitle_7hec5mO3d3U_7899aa08.mp4`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- 30 fps; 640x360

Key frames inspected directly from the local MP4:
- ~24:20 (`t1460.jpg`)
- ~24:30 (`t1470.jpg`)

## State A — first visible terminal row

At ~24:20 the Order Panel shows:

- Price/Entry: 3229.08
- S/L: 3237.12
- T/P: 0.00

Therefore:

- risk = S/L - Entry = 8.04
- midpoint(Entry, S/L) = 3233.10
- Entry - 1*risk = 3221.04
- Entry - 2*risk = 3213.00

The chart simultaneously shows a measurement stack labelled `0.0`, `2x`, `E`, `1`, and `2`.

Visual/price-axis alignment is consistent with:

- `0.0` ↔ 3237.12 ↔ S/L
- `2x` ↔ 3233.10 ↔ midpoint between S/L and Entry
- `E` ↔ 3229.08 ↔ Entry/Price
- `1` ↔ 3221.04 ↔ Entry - 1R
- `2` ↔ 3213.00 ↔ Entry - 2R

The visible `2` line is close to the terminal TP shown in later order state (3213.33–3213.45), but this does NOT prove `2 = TP` or that TP is exactly 2R.

## State B — independent order row

At ~24:30 the Order Panel shows a separate row:

- Price/Entry: 3223.84
- S/L: 3235.50
- T/P: 3213.33

Therefore:

- risk = 11.66
- midpoint(Entry, S/L) = 3229.67
- Entry - 1*risk = 3212.18
- Entry - 2*risk = 3200.52

The chart contains another measurement stack whose visible `0.0`, `2x`, and `E` positions are consistent with approximately:

- `0.0` ↔ 3235.50 ↔ S/L
- `2x` ↔ 3229.67 ↔ midpoint
- `E` ↔ 3223.84 ↔ Entry

The lower `1`/`2` levels for this larger-risk stack are not sufficiently visible in the inspected crop to establish their numeric positions independently.

## Strongest current interpretation

The combined evidence supports the following candidate affine convention for a bearish measurement object:

Let `E` be the entry/price level and `S` the structural stop level, with `R = |S-E|`.

For a bearish setup:

- `0.0 = S`
- `2x = S - 0.5*(S-E)` = `E + 0.5R`
- `E = E`
- `1 = E - R`
- `2 = E - 2R`

Equivalently, when the measurement is oriented from stop toward entry and continuation:

`0.0 → E` spans one risk unit; `2x` is the midpoint of that span; `1` and `2` extend the same risk unit beyond E.

This explains the visible State A levels quantitatively and the `0.0 / 2x / E` portion of State B independently.

## Important boundary

The source does NOT show the actual gesture/anchor creation of the measurement object: the video transitions/cuts into a view where the stack is already instantiated. Therefore this pass cannot prove which chart points the author used to construct the object, even though the terminal-price mapping is strongly supported.

This distinction is preserved deliberately:

1. **Level/value mapping:** strong source-correlated evidence.
2. **Measurement construction anchors:** unresolved.
3. **Universal application to every SP2L setup:** not yet frozen.
4. **`2 = TP` or `2 = 2R` as an execution rule:** not proven.
5. **AB=CD A/B/C/D anchor mapping:** unresolved.

## TP observation

For State A:
- Entry = 3229.08
- 2R bearish projection = 3213.00
- later terminal TP examples are approximately 3213.33–3213.45.

The difference is small but non-zero. It is insufficient to infer rounding, spread adjustment, execution adjustment, or any other formula. Those remain unresolved until source evidence explicitly establishes them.

## Effect on source-resolution matrix

### B2 — Entry
Status: **STRONG SOURCE-CORRELATED CANDIDATE**

`E` aligns with terminal Order Panel Entry/Price in multiple observed states.

### B3 — Stop
Status: **STRONG SOURCE-CORRELATED CANDIDATE**

`0.0` aligns with terminal S/L in multiple observed states.

### 2x
Status: **STRONG SOURCE-CORRELATED CANDIDATE**

`2x` is numerically consistent with the midpoint between Entry and S/L in multiple observed states and independently corroborated by the creator's public explanation of a 50% secondary entry from Entry to Stop-Loss. The exact raw-video construction remains unobserved.

### B6 — Leg2 / TP
Status: **UNRESOLVED**

The `1` and `2` labels are numerically consistent with 1R/2R continuation levels in State A, but this does not establish that these levels are the canonical TP1/TP2 rules, nor does it establish the source's exact execution semantics.

### B5 — AB=CD
Status: **UNRESOLVED at executable anchor level**

The risk-projection observation does not identify the source's A/B/C/D anchors.

## Non-inferences

This document does NOT freeze:

- a generic Fibonacci implementation;
- `2 = TP`;
- `2 = 2R` as a mandatory target rule;
- any rounding/spread/slippage adjustment;
- the measurement object's hidden construction anchors;
- fill price = geometric C;
- any P-Gap formula;
- any mandatory trigger gate;
- any liquidity/BOS/MSS/displacement/FVG/retest/session rule.

## Next evidence target

The highest-value next source pass is an independent setup where the full measurement stack and all relevant terminal order values remain simultaneously visible, preferably with a different Entry/S/L pair and enough chart range to expose `1` and `2`. This would test whether the affine mapping repeats beyond State A and strengthen the case for freezing the level-value convention while keeping construction anchors separately unresolved.

## Gate decision

**SOURCE RESOLUTION: BLOCKED**

Reason: executable entry/SL level mapping is now strongly supported, but measurement construction anchors, exact TP/Leg2 semantics, and AB=CD executable anchors remain unresolved.
