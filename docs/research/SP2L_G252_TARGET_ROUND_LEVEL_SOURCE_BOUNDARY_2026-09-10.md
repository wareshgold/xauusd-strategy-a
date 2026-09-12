# SP2L G252 — Target Round-Level / Terminal TP Source Boundary

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B6_TERMINAL_TP_ROUND_LEVEL`  
**Status:** `SOURCE_OBSERVATION_CONFIRMED__DETERMINISTIC_SELECTION_UNRESOLVED`

## 1. Purpose

G252 continues the source-first investigation after G250 by reviewing the original SP2L video around 43:20–44:40 frame-by-frame. The objective is to determine what the source establishes about `Round level`, point-distance annotations, and terminal TP selection.

No historical performance, optimization, or implementation convenience is used to infer source meaning.

## 2. Direct visual sequence reviewed

The source schematic remains visible with explicit `TP2`, `TP1`, `Entry`, and `SL` references.

During the subsequent hand-annotation sequence the teacher visibly:

1. writes `Round level`;
2. marks numbered horizontal reference levels (`2`, later `3`);
3. writes a price example around `3255 / 3250`;
4. writes another round-level example around `2500 / 3200`;
5. then separately writes distance examples `250 point`, `500 point`, and `1000`.

The distinction between the `Round level` annotation and the later `point` distance annotations is visually clear enough to record them as separate source-observed concepts.

## 3. What is source-confirmed

### C1 — Round-level concept exists

**FROZEN SEMANTICALLY:**

The source explicitly introduces `Round level` as a practical price-reference concept during target-side discussion.

### C2 — Point-distance examples exist

**FROZEN SEMANTICALLY:**

The source separately illustrates numerical point-distance examples, including approximately `250 point`, `500 point`, and `1000`.

These examples must not be silently converted into a universal target-distance formula.

### C3 — TP1/TP2 reference geometry remains frozen from G250

The source schematic explicitly labels TP1 and TP2 and visually places them at approximately one-risk and two-risk distances from Entry relative to SL. G250 froze this as reference geometry, not terminal order selection.

## 4. What the visual sequence does NOT prove

The reviewed frames do not, by themselves, establish a deterministic rule such as:

- terminal TP = nearest round level;
- terminal TP = nearest round level in the trade direction;
- terminal TP = TP1/TP2 adjusted to a round level;
- round level has a fixed increment such as 5, 10, 25, 50, 100, etc.;
- `250 point / 500 point / 1000` are mandatory TP distances;
- `250 point` = TP1 or `500 point` = TP2;
- terminal TP is selected by whichever of TP1/TP2 is closer to a round level;
- round-level selection is performed before or after Entry/SL measurement;
- round-level selection overrides the 1R/2R references.

The visual annotations show the concepts, but not a sufficiently explicit decision procedure connecting them to the terminal TP field.

## 5. Reconciliation with terminal-order evidence

G213/G219 provide a concrete bearish terminal state:

- Entry = 3229.08
- SL = 3237.12
- TP = 3213.44

The simple 2R reference is 3213.00. The 0.44 difference is therefore preserved as unresolved evidence. G252 does not attribute it to round level, tick rounding, spread, slippage, or another mechanism.

The correct source-first representation remains:

`TP1/TP2 reference geometry = known`

`terminal TP selection = unknown`

`round-level interaction = unknown`

## 6. Synthetic fixture authorization

G252 authorizes research-only fixture dimensions for later B6 testing:

- exact TP1 with no round-level candidate;
- exact TP2 with no round-level candidate;
- TP1 near a round level;
- TP2 near a round level;
- terminal TP exactly on a round level;
- terminal TP between TP1 and TP2;
- terminal TP offset from both references;
- multiple round-level candidates at different distances;
- point-distance examples independent of round-level examples;
- bearish cases marked unresolved until source-equivalent target geometry is frozen.

These fixtures discriminate interpretations only; they must not be used to optimize a round-level increment.

## 7. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B6 — TP1/TP2 reference geometry
`FROZEN_PARTIAL`

### B6 — Round-level semantic concept
`FROZEN_SEMANTIC`

### B6 — Terminal TP selection
`BLOCKED`

### B6 — Round-level deterministic formula
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

## 8. Final decision

G252 strengthens the source map by confirming that `Round level` is an explicit source concept and is visually distinct from point-distance examples. It does **not** provide enough evidence to define how a terminal TP is selected from TP1/TP2 and/or round levels.

Therefore no terminal TP selector, round increment, nearest-level rule, or adjustment formula is frozen.

The next productive source-first task is to inspect the earlier order-placement walkthrough and later worked examples for an explicit case where the teacher states or demonstrates the selection of one target level as the actual order TP. If no such case exists, the terminal TP field must remain unresolved even though TP1/TP2 reference geometry is frozen.
