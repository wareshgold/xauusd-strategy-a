# SP2L G261 — Entry Anchor Cross-Reference

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `SEMANTIC_CONFIRMED__PRICE_ANCHOR_UNRESOLVED`

## Objective

Cross-reference independent source appearances of the SP2L Entry / BuyLimit concept before assigning an executable price formula.

## Source observations

### 1. Continuous worked schematic — ~39:00–40:20

The source explicitly labels a horizontal order/reference line **BuyLimit**. A separate horizontal line is drawn below it and labeled **SL**. The BuyLimit line is visibly a price level inside the upward structure rather than a market-close instruction.

Important observation: the drawing does **not** label the BuyLimit line as `C`, correction-low, P-Gap boundary, or any other OHLC anchor. The hand-drawn line also has no numeric price scale from which an exact offset can be recovered.

### 2. Continuous worked schematic — ~42:00–42:30

The teacher again marks **Buy** and a separate **SL** beneath the bullish structure, then uses the `2x` measurement vocabulary. This is a second independent visual occurrence of an entry/reference level distinct from the structural stop.

The geometry demonstrates separation of Entry and SL, but does not identify the Entry price as a specific candle high/low/open/close, P-Gap boundary, correction extreme, or measurement-derived coordinate.

### 3. Clean target schematic — ~42:50–43:20

The source schematic explicitly labels a horizontal level **Entry** and a separate **SL**. Above Entry it labels **TP1** and **TP2**. This confirms that Entry is a first-class source-defined reference in the target construction schematic.

The schematic does not expose the construction anchor in OHLC terms.

### 4. Practical order-panel examples — ~21:40 and ~23:40

At ~21:40 the visible order row contains:

- Entry/Price: `3229.08`
- S/L: `3237.12`
- T/P: `3213.44`

At ~23:40 multiple rows are visible, including:

- `3229.08 / 3237.12 / 0.00`
- `3223.84 / 3235.50 / 3213.33`
- `3228.88 / 3235.50 / 0.00`

These are practical execution examples, but the chart does not expose enough information to prove the source construction formula for each Entry price.

## Candidate-anchor matrix

| Candidate Entry interpretation | Source correlation | Deterministically proven? |
|---|---|---|
| correction extreme | conceptually adjacent to correction | **NO** |
| correction candle low/high | possible visual relationship | **NO** |
| P-Gap boundary | plausible structural reference | **NO** |
| spike-origin extreme | visually nearby in some examples | **NO** |
| `E` measurement level | execution examples correlate with E vocabulary | **NO** as construction rule |
| fixed retracement / percentage | no explicit source formula found | **NO** |
| explicit BuyLimit horizontal reference | directly source-confirmed | **YES semantic only** |

## Decision

**Do freeze:**

- Entry is a distinct source-defined reference/order level.
- The mechanism is a **pending BuyLimit/SellLimit-style order**, not a market-entry substitution.
- Entry and structural SL are separate references.

**Do not freeze:**

- Entry = correction extreme.
- Entry = C.
- Entry = P-Gap boundary.
- Entry = spike-origin extreme.
- Entry = a particular wick/body/open/close.
- Entry = `E` by definition.
- Entry = a fixed percentage/retracement.
- Any spread, rounding, or buffer rule.

## Gate effect

`SOURCE RESOLUTION: PASS_PARTIAL`  
`FROZEN GEOMETRY: BLOCKED_FOR_ENTRY_PRICE`  
`PRODUCTION: BLOCKED`

The source now gives repeated independent confirmation of the **Entry semantic**, but not an executable OHLC price anchor. The engine must remain fail-closed until that anchor is source-resolved.
