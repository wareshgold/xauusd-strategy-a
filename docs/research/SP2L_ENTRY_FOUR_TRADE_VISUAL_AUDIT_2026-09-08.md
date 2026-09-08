# SP2L Four-Trade Entry Visual Audit — 2026-09-08

## Objective
Cross-check the four initial XAUUSD trade examples shown in the authoritative source video against competing executable Entry interpretations.

## Primary source evidence inspected
The source-video section around the real trade examples (~52:00–65:00) was inspected at multiple timestamps, including the chart/order-history sequence around ~57:20–60:40 and the annotated SP2L examples immediately preceding it.

The visible order history contains four XAUUSD rows with entries approximately:

| Trade | Entry | SL | TP | Observation |
|---|---:|---:|---:|---|
| T1 | 3229.08 | 3237.73 | 0.00 | visible order-history record |
| T2 | 3223.84 | 3235.50 | 3213.37 | visible order-history record |
| T3 | 3228.88 | 3235.50 | 3213.37 | visible order-history record |
| T4 | 3232.41 | 3237.80 | 0.00 | visible order-history record |

These prices are source-visible execution records, not inferred geometry.

## Visual findings

### 1. Entry is represented as a horizontal price level
The real-trade charts show horizontal levels associated with the annotated corrective structure. The instructor marks the relevant local low/high areas and uses horizontal order/reference lines. This is consistent with the source's earlier explicit `Buy Limit` / `Entry` diagrams.

### 2. The visual evidence does not establish a unique candle index
The four real examples contain overlapping candles, hand-drawn circles/arrows, horizontal levels, and subsequent management annotations. The available video resolution does not permit a source-safe mapping of every execution price to exactly one universally indexed candle across all variants.

### 3. The examples do not justify importing a last-Spike-candle-breakout prerequisite
The source-video teaching sequence explicitly permits the pending order during correction and does not visually establish that the order must remain inactive until a later last-Spike-candle breakout/reclaim. The real-trade screenshots therefore do not overturn the earlier primary-source semantic conclusion.

### 4. Wick-versus-body remains unresolved
The order levels visually track candle-structure areas, but the resolution and annotation overlap do not prove whether the executable level is the wick extreme, body boundary, or another source-defined reference.

### 5. Order-history price is fill evidence, not proof of geometric level
The recorded entry price can differ from a hand-drawn/reference level because of order execution, platform precision, spread, or later order adjustment. Therefore the fill price must not be treated as the geometric definition of the source Entry without additional evidence.

## Discriminating interpretation matrix

| Candidate | Source status | Reason |
|---|---|---|
| Pending limit during correction | SOURCE-CONFIRMED SEMANTIC | Explicit source narration + diagrams |
| Previous/relevant Low for BUY | SOURCE-CONFIRMED SEMANTIC | Explicit source narration |
| Previous/relevant High for SELL | SOURCE-CONFIRMED SEMANTIC | Explicit source narration |
| Last-Spike-candle breakout required | REJECTED AS CANONICAL | Not established by primary source |
| Entry = P-Gap boundary | REJECTED | No source proof |
| Entry = generic FVG boundary | REJECTED | No source proof |
| Entry = classical C/Fibonacci | REJECTED | Source contrasts its candle-level method with classical ABCD |
| Entry = wick extreme | UNRESOLVED | Visual resolution insufficient |
| Entry = body boundary | UNRESOLVED | Visual resolution insufficient |
| Exact relevant candle index | UNRESOLVED | Variants are not uniquely indexed |
| Fill price = geometric Entry | UNRESOLVED / DO NOT ASSUME | Execution record is not geometric proof |

## Gate decision

This audit strengthens the semantic Entry contract but does **not** freeze executable Entry geometry.

- Entry semantic: **SOURCE-CONFIRMED**
- Pending-limit execution mode: **SOURCE-CONFIRMED**
- Exact Entry candle: **UNRESOLVED**
- Exact Entry price formula: **UNRESOLVED**
- Wick/body convention: **UNRESOLVED**
- Fill semantics: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- Historical optimization: **LOCKED**
- Production: **UNCHANGED**

## Source-first rule

The observed profitability or exact execution prices in the four examples must not be used to choose among unresolved geometric hypotheses. Source meaning controls; unresolved geometry remains unresolved until authoritative evidence uniquely determines it.
