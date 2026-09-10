# SP2L G245 — Correction + Pending-Limit Entry Geometry Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B2_CORRECTION_PENDING_LIMIT_GEOMETRY`  
**Status:** `PARTIAL_FREEZE__EXECUTION_GEOMETRY_BLOCKED`

## 1. Purpose

This pass resolves only source-supported semantics for the SP2L correction and pending-limit entry sequence. It does not infer A/B/C/D anchors, does not equate the fill price with a geometric point, and does not substitute a market-entry rule for the source's order-placement mechanism.

No historical performance or implementation convenience is used to decide source meaning.

## 2. Evidence basis

Primary authoritative source:

- SP2L source video: `https://youtu.be/7HEC5mO3d3U`

Supporting source-resolution records:

- G209 — source evidence matrix
- G211 — May 13 entry walkthrough
- G213 — first four trades / order-panel evidence
- G217–G219 — measurement/level mapping and affine reconstruction
- G244 — B1 P-Gap source-resolution decision

Official creator explanation:

- `https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/`

## 3. Source-confirmed correction semantics

The official creator explanation states the operational correction condition in directional form:

- bullish/uptrend: wait for the corrective candle to reach the **low of the previous candle**;
- bearish/downtrend: wait for the corrective candle to reach the **high of the previous candle**.

This is stronger than a generic statement that “a correction happens”: it identifies the source's directional reference level for the correction event.

The May-13 walkthrough independently shows repeated initial move → correction → continuation constructions and repeatedly marks a lower correction/reference zone before the continuation. G211 explicitly records that the walkthrough operationalizes the correction after the first move, while also noting that the executable horizontal entry price was not uniquely identified. fileciteturn296file0L2-L2

### B2-C1 decision

**FROZEN AT SEMANTIC LEVEL:**

`Correction event = corrective candle reaches the previous candle's opposing extreme in the direction stated by the source.`

This freezes the source meaning of the correction trigger/reference only.

It does **not** freeze:

- which candle is the canonical “previous candle” when multiple correction candles occur;
- whether the event is evaluated intrabar or only after candle close;
- whether the touch must be exact, exceeded, or merely visually reaches the level;
- whether the correction event itself is the order-placement event;
- any A/B/C naming convention.

## 4. Pending-limit / order-placement evidence

The early source walkthrough contains a deliberate order-placement section. G213 records the 21:40–24:00 order-panel sequence with explicit terminal Price, S/L and T/P fields, while the chart simultaneously displays `0.0`, `2x`, `E`, `1`, and `2` measurement labels. This establishes source-level execution mechanics rather than a purely schematic setup. fileciteturn297file0L2-L2

G213 also records that the source uses an explicit entry-related level (`E`) and a separate `2x` level, but the displayed panel does not uniquely identify whether canonical Entry is `E`, `2x`, or another relationship. It also does not establish that either level is C, nor that the terminal fill price equals a geometric source point. fileciteturn297file0L2-L2

G211 similarly records repeated horizontal entry/reference levels in the May-13 walkthrough and explicitly preserves the uncertainty around the executable entry anchor. fileciteturn296file0L2-L2

### B2-C2 decision

**FROZEN:** the source uses an explicit order-placement / entry-level mechanism associated with the correction-to-continuation sequence.

**NOT FROZEN:** the exact price formula for that pending entry.

## 5. Entry anchor candidates — explicit boundary

The following candidates remain research hypotheses only:

1. Entry equals the correction-reference level.
2. Entry equals a level labelled `E` in the source measurement.
3. Entry equals a `2x`-derived level.
4. Entry equals a source-defined candle extreme associated with the correction.
5. Entry equals another source-specific level that is not recoverable from the currently available visual evidence.

No candidate is promoted to canonical Strategy A geometry.

In particular:

- `Entry = C` is **not frozen**;
- `fill = C` is **not frozen**;
- `Entry = 2x` is **not frozen**;
- `Entry = E` is **not frozen merely because the chart labels a level E**;
- a market close/reclaim entry is **not an acceptable substitute** for the source pending-order mechanism.

## 6. Order timing and fill semantics

The source evidence supports an execution sequence in which an entry level is prepared around the correction/second-leg setup and an order is represented in the trading terminal. However, the reviewed evidence does not uniquely resolve the following machine-level semantics:

| Field | Status | Reason |
|---|---|---|
| Order type | `SOURCE-SUPPORTED / PENDING-LIMIT` | Prior source matrix and order-placement walkthrough support pending-order mechanics. |
| Exact entry price | `UNKNOWN` | `E`, `2x`, correction level and candle anchors are not uniquely mapped. |
| Order placement moment | `UNKNOWN` | Visual walkthrough does not establish the exact intrabar/candle event at which the order must be submitted. |
| Fill condition | `UNKNOWN` | No source statement freezes touch, penetration, close, bid/ask, or other fill semantics. |
| Fill price | `UNKNOWN` | Must not be assumed equal to C or another geometric anchor. |
| Partial fill semantics | `UNKNOWN` | No source evidence reviewed. |
| Order expiry/cancellation | `UNKNOWN` | No deterministic source rule reviewed. |
| Secondary 50% entry | `SEMANTICALLY SUPPORTED` | Official creator explanation states a secondary entry at 50% of the Entry→SL distance, but exact primary-entry anchor remains unresolved. |

## 7. Structural relationship to P-Gap

G244 freezes only the bullish P-Gap endpoint semantics and explicitly keeps complete P-Gap execution geometry blocked. The correction/entry audit therefore does not alter the G244 B1 boundary. fileciteturn298file0L2-L2

The intended source sequence remains semantically:

`valid spike/P-Gap context → correction → source entry mechanism → second-leg continuation`

but the executable mapping from those concepts to exact OHLC events remains incomplete.

## 8. Synthetic-fixture implications

The next fixture layer should distinguish correction/entry interpretations without selecting among them using historical profitability.

Required fixture families:

- bullish correction reaches previous candle low;
- bearish correction reaches previous candle high;
- touch exactly equals the reference level;
- correction penetrates beyond the reference level;
- correction stops short of the reference level;
- multiple correction candles reach the reference level;
- correction event followed by continuation without a fill;
- correction event followed by a pending-order fill;
- candidate `fill=C` versus non-C fill semantics;
- secondary 50% Entry→SL level with the primary entry left abstract.

These fixtures must remain research-only until the source uniquely resolves the corresponding geometry.

## 9. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B2 — Correction
`PARTIALLY FROZEN`

Frozen semantic rule:

- bullish: corrective candle reaches previous candle low;
- bearish: corrective candle reaches previous candle high.

### B2 — Pending-limit entry geometry
`BLOCKED`

The existence of source order-placement mechanics is supported, but exact entry anchor, placement timing, fill semantics and cancellation/expiry semantics are unresolved.

### FROZEN GEOMETRY
`BLOCKED_FOR_FULL_STRATEGY`

### DEV
`BLOCKED`

### UNTOUCHED VALIDATION
`PROTECTED`

### ROBUSTNESS / STABILITY
`BLOCKED`

### FRESH HOLDOUT
`PROTECTED`

### PRODUCTION
`BLOCKED`

## 10. Required next work

1. Preserve the correction semantic freeze above.
2. Continue source review around the explicit `2x` entry section and detailed first-four-trades explanation.
3. Recover source text/audio where possible for the exact meaning of `E`, `2x`, and the order-placement moment.
4. Audit structural invalidation/SL geometry independently rather than coupling it to the unresolved entry anchor.
5. Only after B2/B3/B5/B6 are independently source-resolved should a full deterministic Strategy-A geometry specification be frozen.

## 11. Final decision

**G245 does not freeze the executable pending-limit price.**

It does materially narrow B2: the correction reference is source-confirmed in both directions, and the source clearly uses an entry/order-placement mechanism around the correction → second-leg sequence. The exact pending-limit anchor, order timing, fill semantics and expiry/cancellation rules remain `UNKNOWN` and therefore cannot enter production or historical Strategy-A logic yet.
