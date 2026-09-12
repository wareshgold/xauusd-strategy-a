# G345 — Source-Evidence Discrimination Matrix

Date: 2026-09-12  
Parent gate: G344  
Source asset: preserved full SP2L lesson + source transcript  
Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Purpose

Convert the G340 source-resolution boundary into an explicit evidence matrix. Each unresolved executable dimension is mapped to the authoritative evidence that would be sufficient to resolve it. This gate does not choose a competing interpretation.

## Matrix decision

The research representation distinguishes four states:

- `SOURCE_CONFIRMED`: directly taught or explicitly labelled by the source;
- `SOURCE_SUPPORTED`: strongly constrained by source examples but not executable as a unique formula;
- `UNRESOLVED`: multiple executable interpretations remain possible;
- `EXPLICITLY_REJECTED`: the source evidence supports keeping the candidate as a negative control rather than canonicalizing it.

Unresolved dimensions are required to have an explicit evidence requirement. No requirement is treated as already satisfied merely because a visual example appears plausible.

## Evidence requirements

| Dimension | Current status | Sufficient new source evidence |
|---|---|---|
| Exact A anchor | UNRESOLVED | Explicit label or unambiguous chart convention identifying A event/candle and endpoint |
| Exact B anchor | UNRESOLVED | Explicit label or unambiguous chart convention identifying B event/candle and endpoint |
| A/B/C price field | UNRESOLVED | Explicit high/low/open/close/body-endpoint convention |
| C anchor | UNRESOLVED | Explicit definition tying C to one correction event/price independently of fill |
| Wick/body | UNRESOLVED | Explicit wording or repeated unambiguous chart convention |
| Parent/nested scale selection | SOURCE_SUPPORTED | Explicit rule selecting executable parent scale when nested structures coexist |
| D formula | UNRESOLVED | Explicit equation or labelled A/B/C → D mapping in executable price terms |
| AB=CD tolerance | UNRESOLVED | Explicit tolerance/acceptance band or exact-equality convention |
| TP1/TP2 ↔ D | UNRESOLVED | Explicit mapping from D to TP1/TP2, including partial/extension semantics |
| P-Gap formula | UNRESOLVED | Explicit endpoints, candle count, price fields, and minimum/overlap condition |

## Existing source references

- `36:59–37:08`: explicit `AB=CD` and `Valid BO = P-Gap`.
- `38:38–39:48`: pending-limit correction entry and structural invalidation.
- `41:26–42:37`: TP1/TP2 and R terminology, including reward-selection language.
- `43:27–44:29`: 250/500/1000 described as selectable round/trend-level spacing, not a deterministic TP-distance bridge.
- `01:02:41–01:04:32`: deep-leg origin, parent/nested hierarchy, correction, lower highs, pending-limit movement/activation, and later parent-leg measurement/target discussion.
- G340 formal stopping rule: without new explicit source evidence, unresolved A/B/C/D semantics remain competing research hypotheses.

## Negative control

`FILL_AS_C` remains explicitly rejected as a canonical interpretation. The pending-limit activation marker and the later parent-leg measurement are distinct source objects; fill price must not be silently substituted for geometric C.

## Gate decision

**G345 = PASS — SOURCE-EVIDENCE DISCRIMINATION MATRIX, GEOMETRY STILL UNRESOLVED**

This gate does not freeze geometry and does not authorize historical optimization, live signal generation, or production promotion.

```text
SOURCE_RESOLUTION       BOUNDARY ESTABLISHED
EVIDENCE_MATRIX         COMPLETE FOR CURRENT UNRESOLVED DIMENSIONS
FROZEN_GEOMETRY         BLOCKED
DEV                     BLOCKED
VAL                     PROTECTED
FRESH HOLDOUT           LOCKED
PRODUCTION              BLOCKED
```

## Next authorized step

Either obtain genuinely new authoritative source evidence, or continue synthetic research only where it helps test the implications of the unresolved hypotheses. Synthetic results must not be used to decide what the source means.
