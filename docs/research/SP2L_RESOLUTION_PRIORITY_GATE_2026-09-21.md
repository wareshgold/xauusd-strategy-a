# SP2L Resolution Priority Gate — 2026-09-21

## P0 — Source blockers
- F08 Swing selection
- F10 exact Stop anchor/field/buffer

## P1 — Dependent resolution
- F09 Entry geometry
- F14 AB=CD anchors/tolerance
- F11 Pending lifecycle
- F12 Trigger/activation/fill semantics

## P2 — Downstream
- F15 bearish executable symmetry

## Gate
This is a research prioritization control, not a canonical rule set. It identifies which unresolved source questions constrain downstream reconstruction.

**Result: PASS — priority graph established; Frozen Geometry remains BLOCKED.**

No forward-test or production logic changed.

## F08 resolution pass
F08 now has BUY/SELL hypothesis coverage and explicit wick-vs-body, structural-turn-vs-fixed-pivot, and asymmetric-window counterexamples. These constrain the reconstruction but do not select a canonical swing algorithm.

**Gate: PASS — F08 remains unresolved at the field/algorithm level.**


## F10 resolution pass
F10 now has BUY/SELL coverage across wick, body, structural, and buffered anchor hypotheses plus touch/breach/close and spike-origin counterexamples. Source meaning remains preserved without selecting an executable stop rule.

**Gate: PASS — F10 remains unresolved at field/buffer/invalidation level.**


## F09/F14 resolution pass
F09 now covers BUY/SELL, 1/2/3-candle families, Pending Limit, and competing price-field hypotheses. F14 now covers BUY/SELL and three anchor families with exact/near/materially unequal ratios while tolerance remains unresolved.

**Gate: PASS — neither feature is promoted to canonical geometry.**


## Blocker-resolution checkpoint — 2026-09-21
The active blockers now have explicit evidence requirements and promotion guards in `SP2L_BLOCKER_RESOLUTION_PLAN_2026-09-21.md`. P0 remains F08/F10; downstream work must not promote unresolved geometry.


## F09/F14 dependency discrimination checkpoint
F09/F14 candidate families are narrowed without selecting executable entry fields, A/B/C/D anchors, or tolerance. Variable candle development is retained as a source-shaped family; AB=CD near-equality is retained as diagnostic only. P0 and execution blockers remain gating dependencies.
