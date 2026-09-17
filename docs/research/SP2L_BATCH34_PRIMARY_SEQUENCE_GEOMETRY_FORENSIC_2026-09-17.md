# SP2L Batch 34 — Primary Sequence Geometry Forensic — 2026-09-17

## Purpose

Research-only forensic pass over the primary SP2L training video, concentrating on the instructional sequence at approximately **36:30–44:30**. The objective is to determine whether the source itself exposes a deterministic chain from **AB=CD → P-Gap / valid BO → swing/level selection → Buy Limit → SL → order management → Round Level**.

No backtest result, implementation convenience, or visual preference is used to select a canonical rule.

## Inspection scope

Fine frame sampling was performed from approximately **36:30–44:30**, with additional focused inspection of the transitions around **36:30–38:00**, **38:00–41:00**, and **43:30–44:30**.

Representative video positions inspected include:

- ~36:30–37:15: SP2L title/teaching diagram, `AB=CD`, and handwritten `1M` / `5M`.
- ~38:00: printed `Valid BO = P-Gap`.
- ~38:20–38:40: bullish leg diagram with multiple local lower points visibly marked.
- ~39:00–39:30: `BO` and `Buy Limit` annotations introduced around the same teaching example.
- ~39:30–40:00: a horizontal level explicitly labelled `Buy Limit`; a separate lower `SL` reference is subsequently shown.
- ~40:00–41:00: the represented order level persists; `delete` and numbered/money-management annotations appear.
- ~43:30–44:30: worked/diagrammatic risk and `2X` material followed by `Round level` examples and handwritten spacing values.

## Direct primary-artifact observations

### 1. AB=CD is explicitly taught in the opening sequence

At approximately 36:30–37:15 the SP2L teaching slide is annotated with a large handwritten `AB=CD`. The same sequence also contains handwritten `1M` and `5M`.

This is direct evidence that AB=CD is part of the teaching material. It does **not** expose a deterministic A/B/C/D anchor algorithm, whether anchors use wick/body/OHLC, whether D is projected or observed, or any equality/tolerance/rounding rule.

### 2. The diagram visually distinguishes two directional legs, but the exact anchors remain unspecified

The subsequent hand-drawn/annotated bullish examples show two visually corresponding impulse/correction structures. The drawings communicate a two-leg relationship, but there is no source text in the inspected frames that assigns deterministic A/B/C/D indices to unique candles or prices.

The visible diagrams therefore strengthen the **concept** of two-leg symmetry/equality without resolving executable geometry.

### 3. `Valid BO = P-Gap` is explicit

At approximately 38:00 the printed label `Valid BO = P-Gap` is directly visible beside the bullish example.

This establishes a source-level relationship between a valid breakout (`BO`) and P-Gap in the teaching sequence. It does not expose the complete P-Gap formula, candle indexing, threshold/epsilon, wick/body choice, mirror rule, or the exact condition that makes the BO valid.

### 4. Multiple local lower points are marked before Buy Limit is introduced

Around 38:20–38:40, several local lower points on the bullish sequence are visibly marked. The marks appear associated with successive candle lows/local lows in the drawing.

This is useful evidence that local lower points are structurally relevant to the teaching example. However, the source does not state in these frames which point is the **first important** swing, which point supersedes another, how many points must exist, or how an executable level is selected when multiple candidates coexist.

Therefore F8 remains unresolved at the selection-algorithm level.

### 5. BO and Buy Limit are shown in the same teaching sequence

Around 39:00–39:30, `BO` is handwritten near the bullish structure and `Buy Limit` is then explicitly written beside a horizontal level. A later frame isolates the same concept with the label `Buy Limit` next to the horizontal order level.

This strengthens the source-confirmed concept chain:

`BO context → Buy Limit level`

It does **not** prove that the Buy Limit price equals a specific OHLC field, a P-Gap boundary, an HL/LH value, an AB=CD point, or another particular geometric construction.

### 6. A separate SL reference is visibly introduced below the Buy Limit example

In the simplified Buy Limit diagram around 39:30–40:00, the horizontal Buy Limit level is shown above a separate lower horizontal reference labelled `SL`.

This visually confirms separation between entry/order level and stop-loss/risk reference in the teaching diagram. It does not establish the exact SL price, offset, structural boundary, invalidation event, or whether the SL is always placed at the exact low/high of the spike-origin candle.

The observation is therefore consistent with the previously source-supported **risk/origin separation concept**, while the exact executable SL rule remains unresolved.

### 7. Order persistence and `delete` are directly visible

Around 40:00–41:00, the horizontal order reference remains present as the diagram advances. In the following frames, handwritten `delete` appears next to the order-management illustration, together with numbered/money-management annotations.

This directly confirms that order deletion is part of the demonstrated teaching sequence.

The frames do not state the deletion predicate. In particular, they do not distinguish:

- replacement by a newer candidate;
- structural invalidation;
- timeout/expiry;
- manual cancellation;
- another management condition.

Likewise, the frames do not establish multiple-pending-order precedence or a complete pending → fill → management state machine.

### 8. `2X` is visibly associated with a deeper level in the diagram, but no canonical formula is exposed

The sequence around 38:40–39:00 and again around 43:30–44:00 contains handwritten `2X` annotations and a diagram with Buy, `2X`, and SL references. The visual relationship indicates that 2X is a distinct teaching concept and is drawn at a level between the primary Buy level and the SL/risk reference in the shown example.

However, the inspected frames do not expose a numeric formula or sizing rule. In particular, no canonical `2X = 50% Entry→SL` rule is inferred from the drawing.

### 9. Round Level is explicitly taught with multiple spacing examples

Around 43:30–44:30 the diagram is annotated `Round level`. Subsequent frames visibly show handwritten values/examples including **250 point**, **500 point**, and **1000**, with price examples around the chart such as `2500` and `3200`.

This is direct evidence that round-level spacing/examples are part of the teaching material and strengthens F16 at the concept level.

The inspected sequence does not establish which spacing is canonical in which context, whether the values are examples or universal intervals, the exact rounding algorithm, or how Round Level interacts with SP2L setup selection.

## Source-resolution impact

### F8 — First important swing / evolving swing selection

**Status:** PRIMARY-ARTIFACT STRUCTURAL-POINT EVIDENCE STRENGTHENED / EXECUTABLE SELECTION ALGORITHM UNRESOLVED.

The sequence visibly marks multiple local lower points before the Buy Limit teaching step. This confirms that more than one structural/local point can be visually relevant. It does not uniquely select the first-important point, latest point, HL/LH point, or another candidate-selection rule.

### F9 — Entry vs Leg-2 start / activation

**Status:** PRIMARY-ARTIFACT BUY-LIMIT CONCEPT + SEPARATE SL REFERENCE CONFIRMED / EXACT ENTRY CONSTRUCTION AND ACTIVATION UNRESOLVED.

The source explicitly labels a horizontal level `Buy Limit` and later shows the order-management sequence. It does not define the exact price field represented by that level or the event that activates/fills the order.

### F10 — Structural invalidation vs SL

**Status:** PRIMARY-ARTIFACT ENTRY/SL SEPARATION CONFIRMED / EXACT SL CONSTRUCTION AND INVALIDATION EVENT UNRESOLVED.

The teaching diagram visibly separates the Buy Limit level from a lower SL reference. Exact price semantics and invalidation remain unresolved.

### F11 — Pending-order replacement / refresh / cancellation

**Status:** PENDING LEVEL PERSISTENCE + `DELETE` CONFIRMED / CAUSALITY AND STATE MACHINE UNRESOLVED.

The source shows an order level persisting and later explicitly shows `delete`. It does not say why the order is deleted or whether a newer level replaces it.

### F12 — Trigger taxonomy

**Status:** `VALID BO = P-GAP` + BO→BUY-LIMIT ORDERING CONFIRMED / EXACT TRIGGER TAXONOMY UNRESOLVED.

The source provides the concept/order of events but does not uniquely specify touch, wick penetration, bar close, following-bar confirmation, or a 1/2/3-candle rule.

### F13 — 2X

**Status:** PRIMARY-ARTIFACT CONCEPT + VISUAL LEVEL RELATION CONFIRMED / EXACT FORMULA, SIZING, AND EXECUTION SEMANTICS UNRESOLVED.

No numeric formula is promoted.

### F14 — AB=CD

**Status:** EXPLICIT PRIMARY-ARTIFACT CONCEPT CONFIRMED / A-B-C-D ANCHORS AND TOLERANCE UNRESOLVED.

The source directly writes `AB=CD`, but the inspected sequence does not define deterministic anchors or tolerance.

### F15 — Bearish mirror

**Status:** NO NEW DETERMINISTIC MIRROR RULE FROM THIS PASS.

The inspected sequence is predominantly bullish and does not provide a source-complete bearish mirror algorithm.

### F16 — Round Level

**Status:** PRIMARY-ARTIFACT CONCEPT + MULTIPLE EXPLICIT SPACING EXAMPLES CONFIRMED / EXACT ALGORITHM UNRESOLVED.

Observed examples include 250, 500, and 1000 point annotations. No one interval is selected as canonical.

## Deliberate non-inferences

This pass does **not** infer:

- a numeric P-Gap formula or threshold;
- a specific P-Gap candle-index convention;
- Entry = wick/body/OHLC field;
- Entry = P-Gap boundary;
- Entry = AB=CD D point;
- Entry = HL/LH by default;
- touch/wick/close/next-bar fill semantics;
- broker bid/ask/slippage/partial-fill semantics;
- `delete` = replacement, invalidation, timeout, or manual cancellation;
- 2X = 50% Entry→SL;
- a canonical SL offset or exact origin-candle boundary;
- a canonical AB=CD tolerance;
- 250/500/1000 as one universal Round Level interval;
- any multiple-order precedence rule.

## Deterministic source chain currently supportable

The strongest source-aligned chain exposed by this pass is:

`AB=CD concept`
→ `Valid BO = P-Gap`
→ `structural/local points are marked`
→ `Buy Limit is explicitly taught`
→ `separate SL reference is shown`
→ `order deletion is demonstrated`
→ `2X is separately demonstrated`
→ `Round Level is separately demonstrated`

The **conceptual chain is source-supported; the executable geometry/state semantics are not yet source-complete**.

## Gate decision

**Source Resolution: PARTIAL PASS — primary sequence relationships strengthened.**

**Frozen Geometry: BLOCKED** — exact executable geometry, trigger, entry, SL, lifecycle, 2X, AB=CD, and Round Level semantics remain unresolved.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant was selected from this evidence and no production BUY/SELL logic was changed.
