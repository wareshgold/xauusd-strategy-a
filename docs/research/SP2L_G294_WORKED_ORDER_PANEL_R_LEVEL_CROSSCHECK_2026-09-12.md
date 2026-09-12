# G294 — Worked Order Panel / R-Level Cross-Check

Date: 2026-09-12
Source: primary SP2L video `7HEC5mO3d3U`; worked order-panel sequence reviewed around 19:00–25:00, with high-resolution frames from the same worked example.

## Objective
Determine whether the visible `0.0 / 2x / E / 1 / 2` measurement ladder can be mapped to the actual order-panel Entry/SL/TP values without importing an external trading convention.

## Direct visual observations

The worked example contains a bearish price move and a visible measurement ladder. In the high-resolution frames:

- `0.0` is positioned at the stop-side horizontal level.
- `E` is positioned at the entry/reference level.
- `2x` is positioned between `0.0` and `E` and is consistent with the midpoint of that interval.
- `1` and `2` are positioned successively on the target side.
- The order panel simultaneously shows concrete prices, including:
  - Example A: Entry `3229.08`, SL `3237.12`, TP `3213.44`.
  - Example B: Entry `3223.84`, SL approximately `3235.50`, TP `3213.33`.
  - Example C: Entry `3228.88`, SL approximately `3235.50`, TP `3213.45`.

## Numeric reconstruction

For Example A:

- risk = `3237.12 - 3229.08 = 8.04`.
- the exact 1-risk projection below Entry is `3221.04`.
- the exact 2-risk projection below Entry is `3213.00`.
- observed TP = `3213.44`.
- observed TP is therefore approximately `1.945R` relative to Example A Entry/SL.

The chart's visible `1` and `2` labels occur in the corresponding target-side region, with `2` adjacent to the observed terminal TP region.

## Cross-example conflict that matters

The later orders use different Entries/SLs while the displayed terminal TP remains approximately `3213.3–3213.5`:

- Example B: Entry `3223.84`, SL `3235.50`, TP `3213.33`.
- Example C: Entry `3228.88`, SL `3235.50`, TP `3213.45`.

Their Entry-to-TP distances are not 2R:

- B ≈ `0.901R`.
- C ≈ `2.331R`.

This demonstrates that the visible `1/2` ladder cannot safely be interpreted as being recomputed from each later order's own Entry/SL pair.

## Decision

`R_LEVEL_LADDER_STRONGLY_SUPPORTED_AS_SOURCE_MEASUREMENT`

The source visual strongly supports that `1` and `2` are normalized measurement levels in the worked construction, and Example A numerically aligns closely with 1R/2R geometry. However, the source evidence reviewed here does **not** provide an explicit textual equation stating that the canonical Strategy A terminal TP is always `Entry ± 2 * (Entry-SL risk)`.

More importantly, the later order rows show that terminal TP is held near the same target while Entry changes. Therefore the source cannot be reduced to a per-order `TP = Entry ± 2R` formula.

## Canonical prohibition

Do not freeze from this evidence alone:

- `TP = 2R` for every order;
- `TP = Entry ± 2R` using the final filled Entry;
- `2 = TP` as a universal rule;
- `1` and `2` as recomputed levels for every subsequent Entry;
- any rounding/spread/slippage explanation for the 0.44-unit Example-A difference;
- any SELL mirror formula not directly sourced;
- any relationship between the `1/2` ladder and AB=CD unless separately sourced.

## Gate impact

This materially narrows the target hypothesis space: the source appears to construct a **fixed measurement/target ladder before or independently of later order-entry variations**, rather than simply recalculating TP from each order's final Entry.

The canonical target engine remains blocked until a source statement or unambiguous construction sequence identifies what generates the `1/2` levels and how the terminal TP is selected from them.
