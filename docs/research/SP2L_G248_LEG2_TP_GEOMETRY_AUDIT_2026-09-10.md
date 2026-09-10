# SP2L G248 — Leg 2 / TP1 / TP2 Geometry Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B6_LEG2_TP_GEOMETRY`  
**Status:** `SEMANTIC_FREEZE__PROJECTION_AND_EXECUTION_BLOCKED`

## 1. Purpose

This pass isolates the source-defined second-leg / target concepts from the unresolved Entry, Structural SL and AB=CD executable anchors.

The objective is to determine what can be frozen from the source regarding Leg 2, TP1 and TP2, without inventing a projection formula, target anchor, target priority, or execution rule.

No historical performance or optimization result is used to determine source meaning.

## 2. Source evidence reviewed

G209 records direct source observations around the dedicated SP2L construction and order-placement sequence:

- ~37:20 / frame 67,200 — continuation / multi-wave sequence;
- ~38:40 / frame 69,600 — bullish sequence with horizontal reference and correction/continuation;
- ~39:40 / frame 71,400 — explicit `Buy Limit` and `SL`;
- ~42:30 / frame 76,500 — `TP1 / TP2 / Entry / SL` shown together;
- ~44:30 — target-distance discussion.

G213 independently records the practical order-panel walkthrough: the terminal carries explicit Entry, SL and TP prices while the chart simultaneously displays `0.0 / 2x / E / 1 / 2` measurement references. It explicitly preserves the boundary that visible `1` and `2` levels do not, by themselves, prove a TP formula. fileciteturn358file0L2-L2

G219 further establishes a strong numerical source-correlation for the measurement vocabulary: `0.0` aligns with terminal SL, `E` with Entry, and `2x` with the midpoint between Entry and SL in multiple observed states. It deliberately does not freeze `2 = TP`, `2 = 2R`, or the hidden construction anchors. fileciteturn346file0L2-L2

G247 separately freezes only the semantic existence of `AB=CD` as a relationship between two measured movements/legs and leaves A/B/C/D anchors, tolerance, and TP mapping unresolved.

## 3. What is source-confirmed

### B6-C1 — Second-leg continuation

**FROZEN AT SEMANTIC LEVEL:**

`After the correction/entry structure, the source teaches continuation as a second directional movement (Leg 2) in the direction of the Spike.`

This is consistent with the source's SP2L construction and the repeated continuation examples recorded in G211/G209.

### B6-C2 — TP concepts

**FROZEN AT SEMANTIC LEVEL:**

`The source explicitly uses TP/target concepts, including TP1 and TP2, as part of the practical SP2L execution teaching.`

The source therefore establishes that target handling is not an implementation artifact. It is part of the strategy teaching grammar.

## 4. What remains unresolved

| Field | Status | Reason |
|---|---|---|
| Leg-1 executable anchors | `UNKNOWN` | B5 A/B anchors are unresolved. |
| Leg-2 executable anchors | `UNKNOWN` | B5 C/D anchors are unresolved. |
| Leg-2 projection equation | `UNKNOWN` | Source evidence reviewed does not expose a unique formula. |
| TP1 price formula | `UNKNOWN` | TP1 is visibly named but its exact anchor/equation is not frozen. |
| TP2 price formula | `UNKNOWN` | TP2 is visibly named but its exact anchor/equation is not frozen. |
| Relationship TP1 ↔ TP2 | `UNKNOWN` | No deterministic precedence/spacing rule is source-confirmed. |
| AB=CD → TP mapping | `UNKNOWN` | AB=CD semantic relationship is confirmed, but A/B/C/D and target mapping are unresolved. |
| `1` / `2` measurement labels | `STRONG CANDIDATE / NOT FROZEN` | They visually correlate with continuation/projection levels, but labels alone do not establish canonical TP semantics. |
| `2 = 2R` | `NOT PROVEN` | G219 numerical alignment is suggestive in one state but terminal TP differs slightly and construction gesture is unavailable. |
| `2 = TP` | `NOT PROVEN` | The displayed measurement and terminal TP are not source-proven identical. |
| Rounding / tick adjustment | `UNKNOWN` | No source rule reviewed establishes one. |
| Spread / execution adjustment | `UNKNOWN` | No source rule reviewed establishes one. |
| Partial TP / scaling | `UNKNOWN` | Multiple order rows exist, but their semantic role is not proven. |
| Target timing | `UNKNOWN` | No canonical touch/close/intrabar target rule is frozen. |

## 5. Important evidence from terminal values

G213 records a concrete bearish order state:

- Entry `3229.08`
- SL `3237.12`
- TP `3213.44`

G219 calculates risk `8.04` and the theoretical 2R continuation level `3213.00`. The terminal TP is approximately `0.44` above that theoretical level. This is useful evidence that a visual `2` level can be close to the eventual TP while still being insufficient to prove identity. The difference cannot be assigned to rounding, spread, slippage, or another adjustment without source evidence. fileciteturn346file0L2-L2

Therefore the project must retain the distinction:

`measurement level ≠ proven execution TP`

until the source explicitly connects them.

## 6. Candidate B6 interpretations — research only

### H1 — AB=CD projection target

Leg 2 magnitude equals Leg 1 magnitude and the projected endpoint is a target.

**Status:** semantically compatible with B5, but executable anchors and target identity unresolved.

### H2 — `1` / `2` continuation levels

The source measurement labels may represent staged continuation distances, potentially corresponding to first/second target levels.

**Status:** source-correlated candidate only. No canonical TP mapping is frozen.

### H3 — risk-multiple targets

The labels may correspond to 1R/2R continuation distances relative to Entry/SL.

G219 provides strong numerical correlation for the measurement scale, but this does not prove that the source defines TP as a risk multiple. This remains research-only.

### H4 — target level distinct from measurement labels

The terminal TP may be independently selected from the visual projection/reference levels.

**Status:** cannot be rejected from current evidence.

## 7. Non-inferences

This audit explicitly does NOT freeze:

- `TP1 = 1R`;
- `TP2 = 2R`;
- `TP = 2`;
- `TP = AB=CD endpoint`;
- `D = TP`;
- `C = Entry/fill`;
- any fixed target tolerance;
- any rounding or spread adjustment;
- any partial-close rule;
- any market-order substitution;
- any session/time target rule.

## 8. Synthetic fixture requirements

Before historical development, a dedicated B6 fixture suite should distinguish at minimum:

1. exact AB=CD endpoint equals candidate TP;
2. AB=CD endpoint differs from candidate TP by a small amount;
3. `1` and `2` levels present but terminal TP differs;
4. TP1/TP2 both visible with different possible precedence;
5. target hit intrabar versus candle close;
6. target hit before/after a second entry;
7. multiple order rows without assuming scaling semantics;
8. rounding/tick differences;
9. spread/execution differences;
10. Leg 2 projection valid while candidate TP is independently placed.

These are discrimination fixtures only. Historical profitability must not choose the source interpretation.

## 9. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B6 — second-leg semantic meaning
`FROZEN`

Frozen:

`The source teaches a second continuation movement after the correction and explicitly teaches TP/target concepts including TP1 and TP2.`

### B6 — executable projection / TP geometry
`BLOCKED`

Unresolved:

- Leg-1/Leg-2 anchors;
- projection equation;
- TP1 formula;
- TP2 formula;
- relation to AB=CD;
- target execution semantics.

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

**G248 freezes B6 only at semantic level. It does not authorize an executable Leg-2 or TP formula.**

The strongest currently justified statement is:

> **After the correction, the source expects a second directional continuation and explicitly teaches target handling including TP1/TP2.**

The source does not yet justify turning the visible measurement labels, AB=CD relationship, or terminal TP values into a deterministic target equation.

## 11. Required next work

1. Continue source inspection around 42:00–44:40, prioritizing frames where TP1/TP2, Entry and SL are simultaneously visible and the teacher is actively constructing the target measurement.
2. Cross-reference the target construction with the 36:30–38:40 AB=CD sequence.
3. Resolve whether the measurement object is created from identifiable chart anchors rather than merely displayed after a cut.
4. Only after B5/B6 anchor resolution, build synthetic AB=CD/Leg-2/TP fixtures.
5. Preserve all current validation/holdout protections.
