# SP2L G249 — Target Construction Source Boundary

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B6_TARGET_CONSTRUCTION_SOURCE_BOUNDARY`  
**Status:** `SOURCE_EVIDENCE_INSUFFICIENT__VISUAL_CONSTRUCTION_REQUIRED`

## 1. Purpose

G249 performs the next source-first pass requested after G248: isolate the target-construction sequence around the source's TP1/TP2 teaching and determine whether the repository's existing evidence uniquely exposes the chart-object construction needed to freeze target geometry.

No historical performance, optimization result, or implementation convenience is used to infer source meaning.

## 2. Evidence currently available

G209 records the relevant source windows:

- ~42:30 / frame 76,500 — `TP1 / TP2 / Entry / SL` shown together;
- ~44:30 — target-distance discussion.

G213 records the practical order-panel sequence and confirms that explicit terminal Entry, SL and TP prices coexist with chart measurement labels `0.0 / 2x / E / 1 / 2`. It explicitly states that the labels alone do not prove the generating formula or TP identity.

G219 records a concrete bearish state:

- Entry = 3229.08
- SL = 3237.12
- TP = 3213.44
- risk = 8.04
- theoretical 2R continuation level = 3213.00

The terminal TP therefore differs from the simple 2R calculation by 0.44 price units. Existing evidence does not establish whether that difference is due to a different anchor, a separate target rule, rounding, spread, execution convention, or another source-specific mechanism. No such mechanism may be invented.

G247 freezes only the semantic existence of AB=CD and leaves A/B/C/D anchors and equality tolerance unresolved.

G248 freezes only the semantic existence of second-leg continuation and TP/TP1/TP2 concepts, while leaving executable target geometry unresolved.

## 3. Source-resolution result

The repository evidence available to this pass does **not** contain a provenance-safe frame sequence showing the target measurement object being created from identifiable chart anchors with enough detail to establish:

1. the exact origin anchor of the target measurement;
2. the exact endpoint anchor of the projected Leg 2;
3. whether the target uses wick, body, close, or another chart coordinate;
4. whether TP1 and TP2 are projections, staged exits, or distinct source-defined reference levels;
5. whether the terminal TP is identical to a displayed measurement level;
6. whether `1` and `2` are target labels, projection multiples, or another source measurement vocabulary.

The existing evidence proves that these concepts are taught together, but not the executable geometry connecting them.

## 4. Explicit non-inferences

The following remain prohibited:

- TP1 = 1R;
- TP2 = 2R;
- TP = level `2`;
- TP = AB=CD endpoint;
- D = TP;
- C = Entry/fill;
- any target tolerance;
- any rounding or spread adjustment;
- partial-close/scaling semantics from multiple terminal rows;
- intrabar-versus-close target execution rule.

## 5. Required source artifact to cross the boundary

A provenance-safe visual sequence is required. The highest-value artifact is the original SP2L video (or source-quality extraction) covering approximately **42:00–44:40**, ideally including several seconds before and after each target-construction action.

Required evidence characteristics:

- frame timestamps tied to the registered 30-fps convention;
- sufficient resolution to identify chart-object endpoints;
- continuous sequence rather than isolated screenshots where possible;
- visible teacher annotations/measurement gestures;
- visible terminal TP1/TP2/Entry/SL values when applicable.

If the original video is unavailable, an independently provenance-identified transcript/audio plus source-quality frame sequence may be used, but text must not silently override unresolved visual geometry.

## 6. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B6 semantic meaning
`FROZEN`

### B6 executable target construction
`BLOCKED`

### Evidence boundary
`SOURCE_ARTIFACT_REQUIRED`

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

## 7. Decision

**G249 does not invent a target formula.** The current repository evidence is sufficient to preserve the semantic existence of Leg 2 and TP1/TP2, but insufficient to freeze executable target geometry.

The next productive action is not backtesting. It is obtaining or reintroducing the provenance-safe source visual artifact for the 42:00–44:40 target-construction window and reviewing it frame-by-frame.

Until that evidence exists, all candidate target formulas remain research hypotheses only.
