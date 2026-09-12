# SP2L G262 — Structural SL Anchor Cross-Reference

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `SEMANTIC_CONFIRMED__OHLC_BOUNDARY_UNRESOLVED`

## Objective

Cross-reference repeated source examples for the structural stop-loss location and determine whether the visual evidence is sufficient to promote a precise OHLC boundary.

## Source observations

### 1. Multi-example source sheet — ~28:00–29:00

The teacher marks low points beneath several bullish candle sequences with handwritten `L` annotations. These marks demonstrate repeated attention to candle lows during the setup construction, but they are not explicitly labeled `SL`; therefore they are retained as contextual evidence only and are not treated as direct stop orders.

### 2. Buyer construction — ~33:00–33:40

The source explicitly labels a bullish construction **Buyer** and draws a separate horizontal line beneath the structure as **SL**. The SL line is visually aligned with/just beneath the low of the candle from which the upward movement originates.

This is direct visual support for the source semantic “behind the candle from which the Spike originated.” It does not provide a numeric scale or a declared tick/pip buffer.

### 3. Continuous worked schematic — ~39:40–40:20

The source labels **BuyLimit** and separately marks **SL**. The SL is drawn beneath the low of the initial/origin candle in the bullish sequence. The distance is visually tiny and hand-drawn, so the frame cannot distinguish exact candle Low from `Low - buffer`.

### 4. Continuous worked schematic — ~41:40–42:30

The teacher again marks **Buy**, **2x**, and a separate **SL** below the bullish structure. The SL reference is again visually placed behind/below the origin portion of the Spike structure.

### 5. Clean target schematic — ~42:50–43:20

The clean schematic labels **Entry** and **SL** as separate horizontal levels. The SL level is at the bottom of the construction and remains distinct from Entry and the target levels.

## Candidate SL boundary matrix

| Candidate bullish SL interpretation | Evidence | Status |
|---|---|---|
| below origin candle | direct and repeated | **SOURCE-CONFIRMED SEMANTIC** |
| exact `Low(origin)` | visually compatible | **NOT PROVEN** |
| `Low(origin) - fixed buffer` | visually compatible | **NOT PROVEN** |
| origin candle body low | possible only by interpretation | **NOT PROVEN** |
| wick extreme + buffer | possible only by interpretation | **NOT PROVEN** |
| bearish mirror `High(origin)` | not directly established in this cross-reference | **UNRESOLVED** |

## Decision

**Freeze:**

- SL is a **structural invalidation level**.
- It is placed **behind the candle from which the Spike originated**.
- Entry and SL are separate source references.

**Do not freeze:**

- bullish SL = exact `Low(origin)`;
- bearish SL = exact `High(origin)`;
- wick versus body boundary;
- fixed or proportional buffer;
- spread adjustment;
- rounding;
- intrabar versus close invalidation timing.

## Important cross-reference result

The repeated drawings materially strengthen the relationship:

`Spike origin candle → structural SL behind that candle`

but they do **not** resolve the final executable OHLC formula. The distinction matters because the exact Entry anchor is also unresolved; therefore numerical R cannot yet be treated as a source-defined quantity.

## Gate effect

`SOURCE RESOLUTION: PASS_PARTIAL`  
`FROZEN GEOMETRY: BLOCKED_FOR_SL_PRICE`  
`PRODUCTION: BLOCKED`
