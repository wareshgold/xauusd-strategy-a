# SP2L G253 — Worked Examples / Terminal TP Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `WORKED_EXAMPLES_REVIEWED__NO_UNIQUE_TERMINAL_TP_SELECTOR`

## Objective

Cross-check the later worked-example sequence against the schematic TP1/TP2 teaching and determine whether the teacher's actual examples uniquely reveal which reference becomes the terminal TP.

## Evidence reviewed

The original SP2L video was reviewed across the later worked-example sequence following the TP1/TP2 schematic, including the repeated chart examples around the 49:00–54:00 region. The examples repeatedly show the strategy's trade/measurement vocabulary and target-side annotations, but the available visual sequence does not expose a single deterministic instruction of the form `choose TP1`, `choose TP2`, `choose nearest round level`, or `choose AB=CD endpoint` for every setup.

The earlier terminal order-panel evidence remains important: explicit Entry/SL/TP prices coexist with measurement labels, but the labels do not uniquely establish the terminal TP selector.

## Source-confirmed facts carried forward

- The source teaches TP1 and TP2 as named target references.
- The bullish schematic relates TP1 to one risk distance from Entry and TP2 to two risk distances from Entry.
- Round level is taught as a separate concept.
- Point-distance examples are taught as a separate concept.
- Actual examples contain explicit terminal trade/order information.

## Unresolved

The worked examples do not establish, with provenance-safe uniqueness:

1. whether terminal TP is always TP1;
2. whether terminal TP is always TP2;
3. whether the choice depends on context;
4. whether round levels override TP1/TP2;
5. whether AB=CD overrides TP1/TP2;
6. whether a point-distance rule controls the terminal target;
7. whether multiple target rows represent staged exits rather than alternatives;
8. exact execution/touch semantics.

## Important numerical cross-check

Existing example: Entry 3229.08, SL 3237.12, TP 3213.44. Risk is 8.04, so the simple 2R reference is 3213.00. The 0.44 difference is real in the recorded example and must remain unexplained until a source rule accounts for it.

## Decision

Worked examples strengthen the existence of target handling but do not uniquely resolve terminal TP selection. No target selector enters canonical Strategy A.

### Gates

- SOURCE RESOLUTION: `PASS_PARTIAL`
- B6 semantic: `FROZEN`
- B6 executable terminal TP: `BLOCKED`
- FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`
- DEV: `BLOCKED`
- VALIDATION: `PROTECTED`
- PRODUCTION: `BLOCKED`
