# SP2L Stop-Loss / Origin-Candle Four-Trade Audit — 2026-09-08

## Objective
Cross-check the four real XAUUSD trade examples in the authoritative source video for Stop-Loss (SL) placement and Spike-origin-candle semantics, without inventing wick/body or buffer rules.

## Source-visible trade records

| Trade | Entry | SL | Risk distance | Status |
|---|---:|---:|---:|---|
| T1 | 3229.08 | 3237.73 | 8.65 | source-visible |
| T2 | 3223.84 | 3235.50 | 11.66 | source-visible |
| T3 | 3228.88 | 3235.50 | 6.62 | source-visible |
| T4 | 3232.41 | 3237.80 | 5.39 | source-visible |

Risk distance is the absolute difference between the observed execution price and observed stop price. It is descriptive only.

## Visual/source findings

### 1. Source semantics for SL are strong
The teaching sequence explicitly places the SL behind the candle where the Spike originated. The source diagram also shows Entry above/below and SL on the invalidation side of the originating structure.

### 2. The four real trades are consistent with structural, not fixed-distance, invalidation
The observed SL distances differ materially (8.65, 11.66, 6.62, 5.39 price units). This is consistent with an SL derived from setup structure rather than a single fixed price-distance parameter. This observation does **not** identify the exact structural price formula.

### 3. Origin candle remains relational
The clearest source teaching frames mark the beginning/earliest candle of the source-defined directional Spike sequence and place the invalidation beyond that origin area. The real-trade frames contain annotations and overlapping candles, so they do not establish a universally fixed candle index across all Spike variants.

### 4. Wick-versus-body remains unresolved
The real chart drawings show SL/reference levels beyond the originating structure, but the available resolution does not prove whether the stop is exactly beyond the origin wick extreme, origin body boundary, or another source-defined boundary.

### 5. Stop buffer remains unresolved
No source evidence in the inspected real-trade frames uniquely establishes a fixed tick/point/pip buffer beyond the origin candle. Do not invent one.

### 6. Trade-management changes do not redefine canonical SL geometry
The source narration allows an order to be deleted/replaced when the setup's SL distance changes materially. This supports treating observed stop prices as execution records rather than as a universal fixed formula.

## Discrimination matrix

| Hypothesis | Status | Evidence |
|---|---|---|
| SL is on invalidation side of Spike-origin candle | SOURCE-CONFIRMED SEMANTIC | Explicit source teaching |
| Bullish SL below origin structure | SOURCE-CONFIRMED SEMANTIC | Source diagram/narration |
| Bearish SL above origin structure | SOURCE-CONFIRMED SEMANTIC | Source mirror semantics |
| Exact origin = first/earliest candle of source-defined Spike | STRONG CANDIDATE | Source visual sequence + prior origin audit |
| Exact origin candle fixed by absolute index | REJECTED | Source has multiple Spike constructions |
| SL = exact origin wick extreme | UNRESOLVED | Visual evidence insufficient |
| SL = exact origin body edge | UNRESOLVED | Visual evidence insufficient |
| SL = origin extreme plus fixed buffer | UNRESOLVED | No source-confirmed buffer |
| SL = Entry minus/plus fixed distance | REJECTED AS CANONICAL | Conflicts with structural wording and variable observed distances |
| Observed fill-to-SL distance defines canonical risk | REJECTED | Execution record is not source geometry |

## Gate decision

- SL semantic: **SOURCE-CONFIRMED**
- Structural invalidation behind origin: **SOURCE-CONFIRMED**
- Relational origin-candle interpretation: **STRONG CANDIDATE**
- Exact wick/body boundary: **UNRESOLVED**
- Fixed buffer: **UNRESOLVED**
- Exact origin identity across all variants: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- Historical optimization: **LOCKED**
- Production: **UNCHANGED**

## Source-first rule
Observed trade prices and apparent profitability must not be used to choose the unresolved SL boundary. The source defines the semantics; exact executable geometry remains unresolved until authoritative evidence uniquely determines it.
