# SP2L G215 — 2x Multi-Order Triangulation

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## 1. Objective

This pass tests the current `2x = 50% of Entry→SL distance` candidate against multiple independent order states visible in the supplied source video, using direct frame inspection rather than backtest performance.

The source video is 30 fps. Frame convention: `round(total_seconds × 30)`.

## 2. Frame-state correction to G214

Direct inspection of the supplied MP4 at exact frame `39,000` (21:40) shows **one visible order row**, not three:

- Price/Entry: `3229.08`
- S/L: `3237.12`
- T/P: `3213.44`
- current market Price column: approximately `3224.67`

The three-row state is first clearly visible later, including at exact frame `41,400` (23:00).

Therefore G214's statement that exact frame 39,000 contained three terminal rows should not be treated as source evidence. G213's one-row observation at 21:40 is consistent with the direct frame inspection.

This correction does not change the underlying 2x candidate; it changes only the bookkeeping of when the additional rows become visible.

## 3. Independent order states observed

### State A — first order

Frame `39,000` / 21:40:

- Entry/Price = `3229.08`
- SL = `3237.12`
- TP = `3213.44`

Risk distance:

`3237.12 − 3229.08 = 8.04`

50% Entry→SL midpoint:

`3229.08 + 8.04/2 = 3233.10`

The chart simultaneously shows the measured labels `0.0`, `2x`, `E`, `1`, and `2`. The visible `2x` reference is approximately at the 3233 area, consistent with the midpoint candidate.

### State B — second order

Frame `41,400` / 23:00:

- Entry/Price = `3223.84`
- SL = `3235.50`
- TP = `3213.33`

Risk distance:

`3235.50 − 3223.84 = 11.66`

50% Entry→SL midpoint:

`3223.84 + 11.66/2 = 3229.67`

A separate measured `2x` reference is visible around the 3229–3230 region. This is directionally and geometrically consistent with the same midpoint transformation.

### State C — third order

Frame `41,400` / 23:00:

- Entry/Price = `3228.88`
- SL = `3235.50`
- TP = `0.00` at this state

Risk distance:

`3235.50 − 3228.88 = 6.62`

50% Entry→SL midpoint:

`3228.88 + 6.62/2 = 3232.19`

A further measured `2x` reference is visible around the 3232 area. Again, the source drawing is consistent with the midpoint candidate.

## 4. Triangulation result

The important observation is not a single visually plausible match. Three distinct Entry/SL pairs generate three distinct midpoints:

| State | Entry | SL | Risk | 50% midpoint |
|---|---:|---:|---:|---:|
| A | 3229.08 | 3237.12 | 8.04 | 3233.10 |
| B | 3223.84 | 3235.50 | 11.66 | 3229.67 |
| C | 3228.88 | 3235.50 | 6.62 | 3232.19 |

The source chart contains multiple independently positioned `2x` references whose vertical placement is consistent with these three midpoint values. This is materially stronger than the single-order observation used in G214.

Because the source frames are 640×360 and the horizontal annotations are manually drawn/labelled, this pass treats the chart comparison as **visual corroboration**, not as a pixel-perfect proof of an exact price formula.

## 5. What this strengthens

### 2x relationship

Status moves from:

**STRONG CANDIDATE / SOURCE-CORRELATED — NOT FROZEN**

to:

**STRONGER MULTI-EXAMPLE SOURCE-CORRELATED CANDIDATE — NOT FROZEN**

Candidate formula for a short setup:

`2x = Entry + 0.5 × (SL − Entry)`

Long mirror:

`2x = Entry − 0.5 × (Entry − SL)`

Equivalent statement: `2x` is the midpoint between Entry and structural SL.

This remains a candidate because the raw video still does not provide a uniquely recovered textual definition tying the label `2x` to this arithmetic transformation.

## 6. What remains unresolved

This triangulation does **not** establish:

- exact primary Entry anchor or exact meaning of label `E`;
- exact structural SL rule, including wick/body treatment;
- whether every SP2L setup uses exactly this 2x relationship;
- whether `2x` is mandatory or an optional secondary entry level;
- whether the order-panel Price field equals the geometric Entry anchor in every case;
- exact TP/Leg2 formula;
- exact relationship of chart levels `1` and `2` to AB=CD/Leg2;
- pending-order replacement/cancellation semantics.

The official creator page independently corroborates a secondary entry at 50% of Entry→SL distance, which is consistent with this candidate, but the source webpage does not by itself resolve the remaining raw-video geometry.

## 7. Non-inference boundary

No rule is promoted from this pass based on profitability or optimization. In particular, this pass does not infer:

- generic Fibonacci logic;
- generic FVG/P-Gap equivalence;
- Entry = C;
- TP = 1R or 2R;
- level `2` = TP;
- a particular wick/body stop formula;
- any mandatory trigger;
- any session filter.

## 8. Gate decision

**SOURCE RESOLUTION remains BLOCKED at executable geometry.**

Current evidence status:

- `2x` midpoint relationship: **STRONGER MULTI-EXAMPLE SOURCE-CORRELATED CANDIDATE — NOT FROZEN**
- optional secondary-entry concept: **official-source corroborated**
- primary Entry geometry: **UNRESOLVED**
- structural SL geometry: **UNRESOLVED**
- TP/Leg2 geometry: **UNRESOLVED**
- source transcript/audio explanation: **not recovered with sufficient provenance**

Next source-resolution priority should be to recover a source-text explanation of `2x` and/or inspect additional independent trades where the `E`, `2x`, `0.0`, `1`, and `2` labels can be paired with explicit terminal prices. If no textual definition is recovered, the midpoint relationship should remain a research candidate rather than being frozen solely from visual correlation.
