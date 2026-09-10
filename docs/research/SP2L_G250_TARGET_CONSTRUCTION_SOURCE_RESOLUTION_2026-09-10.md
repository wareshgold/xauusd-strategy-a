# SP2L G250 — Target Construction Source Resolution

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B6_TARGET_CONSTRUCTION`  
**Status:** `PARTIAL_FREEZE__TARGET_REFERENCE_GEOMETRY_RESOLVED__EXECUTION_MAPPING_OPEN`

## 1. Purpose

G250 revisits the original SP2L source video directly, using the uploaded source-quality 30-fps video, to inspect approximately 42:00–44:40 frame-by-frame and resolve the target construction that was still blocked in G249.

No historical performance or optimization result is used to determine source meaning.

## 2. Source artifact identity

Uploaded source video:

`strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Observed media properties:

- duration: ~4155.67 s;
- video: H.264, 640×360;
- frame rate: 30 fps;
- frame count: 124,670;
- audio present.

The inspected target window is therefore reproducibly addressable using the project's 30-fps convention.

## 3. Direct visual evidence — construction sequence

### 3.1 Hand-drawn construction around 42:15–42:26

The source first shows a hand-annotated bullish SP2L schematic before switching to the clean strategy diagram.

Important observations:

- `BUY` is marked at the entry-side horizontal reference;
- `SL` is marked below the entry structure;
- a circled `2x` label is placed at a horizontal level halfway between the entry-side level and SL-side level;
- the teacher draws vertical distance brackets and a top target-side reference;
- a circled `1` is visible above the target-side construction.

The `2x` placement is visually consistent with the already documented measurement vocabulary from G217–G219: midpoint between Entry and SL. This remains a measurement-vocabulary observation, not a TP identity claim.

### 3.2 Clean source schematic around 42:27–42:30

The source then presents a clean SP2L Strategy diagram with four explicit horizontal references labelled:

`TP2` → top target level  
`TP1` → intermediate target level  
`Entry` → entry level  
`SL` → stop level

The diagram is geometrically constructed so that:

- Entry→TP1 is approximately the same vertical distance as Entry→SL;
- Entry→TP2 is approximately twice the Entry→SL distance.

At source-frame resolution, the displayed schematic is therefore a direct visual encoding of:

`TP1 = Entry + 1 × Risk` for bullish direction  
`TP2 = Entry + 2 × Risk` for bullish direction

with the obvious directional sign reversal for a bearish implementation **only if/when the source's bearish target diagram or equivalent source evidence is independently confirmed**.

The semantic target relationship is source-confirmed at the schematic level. This is materially stronger than the earlier inference from terminal measurement labels alone.

## 4. Important distinction: reference geometry vs terminal TP selection

The clean schematic resolves the target **reference geometry**, but it does not by itself prove that every terminal order's single TP field must equal TP1 or TP2.

This distinction is required because G213/G219 contain a concrete terminal bearish state:

- Entry = 3229.08
- SL = 3237.12
- TP = 3213.44

Simple 2R from Entry/SL is 3213.00, not 3213.44.

Therefore the project must freeze the following separately:

### Frozen

`TP1 reference = 1R from Entry away from SL.`

`TP2 reference = 2R from Entry away from SL.`

### Still open

- whether terminal `TP` is always TP1;
- whether terminal `TP` is always TP2;
- whether terminal TP may be selected at a round level or another source-defined reference;
- whether TP1/TP2 represent staged exits/scaling;
- exact bearish executable formula;
- tick rounding / price precision;
- target touch versus close semantics;
- partial-close behavior.

No terminal-order rule is invented from the schematic.

## 5. Cross-reference with 43:20–44:35 annotation sequence

After the clean schematic, the teacher annotates multiple horizontal target-side references and explicitly writes `Round level` with numbered levels (`1`, `2`, and later `3`). The subsequent handwritten examples include point-distance values around `250 point`, `500 point`, and `1000`.

This sequence is important evidence that target placement may involve a distinction between the ideal TP1/TP2 reference geometry and practical price/round-level selection.

However, the exact spoken semantics of the handwritten point examples are not sufficiently recoverable from the visual layer alone to freeze a deterministic round-level rule. Therefore:

- `Round level` is source-observed;
- its exact relationship to TP1/TP2 is unresolved;
- numeric round-level thresholds are **not** frozen.

## 6. AB=CD relationship remains separate

The target schematic does not expose enough information to retroactively assign A/B/C/D anchors.

Therefore G250 does **not** change G247's boundary:

- AB=CD semantic relationship: frozen;
- A/B/C/D executable anchors: unresolved;
- AB=CD endpoint = TP1/TP2: not proven;
- AB=CD endpoint = terminal TP: not proven.

The 1R/2R target geometry must not be conflated with AB=CD until the source explicitly connects the two constructions.

## 7. Synthetic fixture implications

G250 authorizes a new research fixture dimension for target-reference geometry:

1. bullish Entry/SL with exact 1R TP1;
2. bullish Entry/SL with exact 2R TP2;
3. bearish mirror only after source-equivalent confirmation;
4. terminal TP equal to TP1;
5. terminal TP equal to TP2;
6. terminal TP between TP1 and TP2;
7. terminal TP slightly offset from 1R/2R;
8. terminal TP at a candidate round level;
9. displayed 1R/2R references with no terminal TP;
10. AB=CD endpoint equal to, and different from, TP1/TP2.

These fixtures must test interpretation, not optimize target parameters.

## 8. Gate decision

### SOURCE RESOLUTION
`PASS_PARTIAL`

### B6 — second-leg semantic meaning
`FROZEN`

### B6 — target reference geometry
`FROZEN_PARTIAL`

Frozen:

- TP1 is a one-risk-distance target reference from Entry;
- TP2 is a two-risk-distance target reference from Entry;
- risk is the Entry-to-SL distance;
- target direction follows the trade direction at the reference level.

### B6 — terminal TP execution mapping
`BLOCKED`

Unresolved:

- which target reference is selected as terminal TP;
- round-level interaction;
- scaling/partial TP semantics;
- bearish visual confirmation;
- tick/precision adjustment;
- target execution timing.

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

## 9. Final decision

**G250 materially resolves the target-reference geometry.** The clean source diagram directly labels TP1 and TP2 and encodes them at approximately 1R and 2R respectively relative to Entry and SL.

This is sufficient to promote `TP1 = 1R reference` and `TP2 = 2R reference` from hypothesis to source-confirmed target-reference semantics.

It is **not** sufficient to claim that every terminal TP order is necessarily TP1, TP2, or an exact AB=CD endpoint.

The next source-first task is therefore narrower: resolve the **terminal TP selection / round-level relationship**, then independently build the B6 synthetic fixture suite. No historical backtest is authorized yet.
