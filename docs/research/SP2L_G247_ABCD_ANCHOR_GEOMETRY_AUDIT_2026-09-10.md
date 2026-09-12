# SP2L G247 — AB=CD Anchor Geometry Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B5_ABCD_ANCHOR_GEOMETRY`  
**Status:** `SEMANTIC_FREEZE__ANCHORS_AND_TOLERANCE_BLOCKED`

## 1. Purpose

This pass isolates the source-defined AB=CD relationship from the unresolved Entry, Stop and TP mechanics.

The objective is to determine exactly what can be frozen from the source's explicit `AB=CD` teaching, while refusing to invent A/B/C/D anchors, projection direction, equality tolerance, or execution semantics.

No historical performance or optimization result is used to decide source meaning.

## 2. Source evidence

The primary source registry records the following high-value raw-video observations:

- approximately 36:30 / frame 65,700: explicit `AB=CD` together with `Valid BO = P-Gap`;
- approximately 37:00 / frame 66,600: `AB=CD` shown with `1M / 5M` context;
- approximately 37:20 / frame 67,200: continuation / multi-wave sequence;
- approximately 38:40 / frame 69,600: bullish sequence with horizontal reference and correction/continuation.

The source evidence therefore directly establishes that `AB=CD` is part of the author's SP2L teaching grammar and is associated with the spike/P-Gap → correction → continuation structure.

The May-13 walkthrough independently shows repeated initial move → correction → continuation constructions, but its visual annotations do not uniquely expose the mathematical point labels A/B/C/D. fileciteturn345file0L2-L2

## 3. What is source-confirmed

### B5-C1 — AB=CD semantic relationship

**FROZEN AT SEMANTIC LEVEL:**

`AB = CD` is an explicit source-defined relationship between two measured segments/legs.

At minimum, the source therefore supports the concept that the second measured movement is intended to correspond in magnitude to the first measured movement.

This is consistent with the broader SP2L meaning of a first directional movement followed by correction and a second-leg continuation.

However, the statement above deliberately does **not** assign candle indices or price anchors to A/B/C/D.

## 4. What is NOT source-resolved

The following remain `UNKNOWN`:

| Field | Status | Reason |
|---|---|---|
| Point A anchor | `UNKNOWN` | Source label is visible, but no source-unique OHLC point has been recovered. |
| Point B anchor | `UNKNOWN` | Same ambiguity; could represent an endpoint of the first measured leg, but the exact price/time anchor is not frozen. |
| Point C anchor | `UNKNOWN` | Correction/entry geometry remains unresolved under G245. |
| Point D anchor | `UNKNOWN` | The second-leg endpoint / target geometry remains unresolved under B6. |
| Price-only vs time+price anchor | `UNKNOWN` | Source does not establish whether points are candle extrema, bodies, closes, or another chart-object anchor. |
| Wick vs body | `UNKNOWN` | No authoritative definition ties AB=CD to wick or body extrema. |
| Intrabar vs close | `UNKNOWN` | No deterministic event-timing rule is source-confirmed. |
| Equality tolerance | `UNKNOWN` | No numeric tolerance or rounding rule is stated. |
| Projection direction | `SOURCE-CONTEXT SUPPORTED / FORMULA UNKNOWN` | Continuation is shown, but the exact projection equation is not frozen. |
| Target execution | `UNKNOWN` | AB=CD does not by itself establish TP1/TP2 order semantics. |

## 5. Candidate anchor families — research only

The following are explicitly retained as hypotheses and must not enter canonical production logic:

### H1 — Spike-leg interpretation

`A → B` = source-defined first spike/directional leg; `C → D` = second continuation leg.

This is semantically attractive because it matches the SP2L name and the explicit second-leg concept, but the exact price anchors remain unproven.

### H2 — Full-extrema leg interpretation

A/B/C/D are candle wick extrema at the start/end of the two legs.

This is a plausible geometric implementation candidate, but it cannot be promoted merely because P-Gap endpoint geometry elsewhere favors wick extrema.

### H3 — Body/close leg interpretation

A/B/C/D are candle body or close-derived anchors.

The current source evidence does not provide enough resolution to reject this hypothesis solely from chart appearance.

### H4 — Entry/SL measurement interpretation

AB=CD may interact with the source measurement stack (`0.0 / 2x / E / 1 / 2`) and the correction/entry/SL structure.

G219 shows that the measurement stack has strong source-correlated value relationships, but explicitly preserves AB=CD construction anchors as unresolved. fileciteturn346file0L2-L2

Therefore no mapping such as `A=SL`, `B=Entry`, `C=Entry`, or `D=TP` is allowed.

## 6. Important distinction: magnitude equality vs point identity

The source phrase `AB=CD` supports a relationship between the lengths/magnitudes of two source-defined segments.

It does **not**, by itself, prove:

- that B = C;
- that C is the pending-limit fill;
- that D is TP;
- that AB is the spike body range;
- that CD is the entire post-correction move;
- that equality is exact to the market's minimum tick;
- that any tolerance should be applied.

These distinctions are essential because the production engine must be deterministic and reproducible.

## 7. Relation to B2, B3 and B6

### B2 — Entry

G245 leaves the exact pending-limit anchor unresolved. Therefore G247 cannot use `Entry` as C merely because C is a conventional label in an AB=CD construction.

### B3 — Structural SL

G246 freezes only the semantic statement that SL is placed behind the candle from which the spike originated. It does not define an AB anchor or B anchor.

### B6 — Leg 2 / TP

The source supports second-leg continuation and TP1/TP2 concepts, but exact projection semantics remain unresolved. Therefore D cannot be frozen as TP, TP1, or TP2 from `AB=CD` alone.

## 8. Synthetic fixture requirements

Before any historical development, the fixture layer should distinguish at least:

1. equal first/second leg with exact equality;
2. second leg shorter by a small amount;
3. second leg longer by a small amount;
4. same price magnitude but different candle/time anchors;
5. wick-based versus body-based leg measurement;
6. close-based versus extreme-based measurement;
7. correction ending at a candidate C that is not the eventual fill;
8. pending order filled before/after the geometric C candidate;
9. D equal to projected leg endpoint but not terminal TP;
10. candidate exact-equality versus tolerance-based acceptance.

These fixtures must remain research-only. Their purpose is to separate geometric interpretations, not to choose the interpretation by profitability.

## 9. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B5 — AB=CD semantic meaning
`FROZEN`

Frozen:

`The source explicitly uses AB=CD as a relationship between two measured movements/legs.`

### B5 — A/B/C/D executable anchors
`BLOCKED`

### B5 — equality tolerance
`BLOCKED`

### B6 — projection / TP
`BLOCKED`

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

## 10. Final decision

**G247 freezes only the semantic existence of the AB=CD relationship. It does not freeze A/B/C/D.**

The source evidence is strong enough to reject the idea that AB=CD is merely an implementation artifact, but not strong enough to convert the visible teaching label into a deterministic OHLC formula.

No tolerance, anchor, fill mapping, TP mapping, or projection equation is invented.

## 11. Required next work

1. Continue source inspection around the 36:20–38:50 AB=CD / multi-wave sequence.
2. Prioritize a frame sequence where the measurement object is created rather than merely displayed.
3. Cross-reference the same sequence with the explicit `Buy Limit`, `SL`, `TP1/TP2` panels recorded in G209.
4. Resolve B6 independently rather than deriving TP from AB=CD by assumption.
5. After B5/B6 source resolution, construct a dedicated synthetic AB=CD fixture suite before any historical testing.
