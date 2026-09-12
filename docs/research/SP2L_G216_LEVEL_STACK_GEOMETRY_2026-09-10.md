# SP2L G216 — Level-Stack Geometry Pass

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## 1. Objective

Re-examine the visible `0.0 / 2x / E / 1 / 2` stack in the early order sequence and determine which relationships are directly supported by the chart geometry, versus which require an assumption that the displayed terminal order row belongs to the same measurement object.

The source video is 30 fps; frame convention is `round(total_seconds × 30)`.

## 2. Exact source frames inspected

- 21:40 → frame `39,000`
- 23:00 → frame `41,400`

The 21:40 frame shows one visible order row:

- Price `3229.08`
- S/L `3237.12`
- T/P `3213.44`

The 23:00 frame shows multiple rows:

- `3229.08 / 3237.12 / 0.00`
- `3223.84 / 3235.50 / 3213.33`
- `3228.88 / 3235.50 / 0.00`

The 23:00 chart simultaneously shows multiple horizontal measurement stacks.

## 3. New geometric observation

The labels are not merely arbitrary text. In the clearest 21:40 measurement stack, the vertical spacing is approximately structured as follows:

- `0.0` → `2x`: one unit interval
- `2x` → `E`: one unit interval
- `E` → `1`: approximately two unit intervals
- `1` → `2`: approximately two unit intervals

This means the visible stack has a highly regular source-drawing geometry. However, the image alone does not uniquely establish what numerical unit those intervals represent.

The visual regularity is therefore evidence about the **source's measurement construction**, not yet a deterministic price formula.

## 4. Critical distinction: chart measurement vs terminal order values

A major risk identified in this pass is assuming that the visible measurement stack and the currently selected terminal order row are necessarily the same trade object.

The terminal provides exact numerical values, while the chart measurement is a manually drawn/annotated object. At the available frame resolution, the horizontal lines can be visually compared to the price axis, but this is insufficient to prove an exact mapping for every label.

In particular, the following mappings remain unproven:

- `0.0` = terminal SL;
- `E` = terminal Entry/Price;
- `1` = 1R from terminal Entry;
- `2` = 2R from terminal Entry;
- `2x` = 50% Entry→SL midpoint.

Some of these relationships may be visually compatible in individual examples, but compatibility is not the same as source-unique proof.

## 5. What is now strongest

There are two independent pieces of evidence for the 2x concept:

1. Raw-video chart drawings repeatedly show a distinct `2x` level positioned between the stop-side `0.0` level and the entry-side `E` level.
2. The official creator page explicitly describes a secondary entry at 50% of the distance from Entry to Stop-Loss.

This makes the midpoint interpretation highly credible as a **source-correlated candidate**.

Nevertheless, the exact identity of `E` and `0.0` with the terminal order fields must be established before the candidate can be converted into executable geometry.

## 6. TP / level `1` / level `2`

The terminal TP values are close to the lowest displayed `2` reference in the relevant early sequence, but the available visual evidence does not justify claiming an exact formula yet.

Likewise, the labels `1` and `2` have regular geometric spacing but their semantic meaning remains unresolved. They could represent target/projection stages or source-specific measurement levels. A numerical interpretation such as 1R/2R must not be frozen from appearance alone.

This is particularly important because the first order has:

`Entry 3229.08`, `SL 3237.12`, `TP 3213.44`

while a naive 2R calculation from those terminal values gives:

`3229.08 − 2 × (3237.12 − 3229.08) = 3213.00`

not `3213.44`.

Therefore **TP = exact 2R is not source-proven** by this order state. The 0.44 difference is material enough that it must not be silently rounded away.

## 7. Consequence for G215

G215's conclusion that the multiple order states provide stronger visual corroboration for the midpoint candidate remains directionally useful, but this pass adds an important qualification:

> The order-panel values and the chart measurement stacks cannot yet be proven to be one-to-one objects from the available visual evidence.

Accordingly, `2x = Entry/SL midpoint` remains a **STRONG SOURCE-CORRELATED CANDIDATE — NOT FROZEN**, rather than a validated executable rule.

## 8. B-gate impact

### B2 Entry

Still unresolved. The label `E` is clearly source-defined, but exact mapping from `E` to terminal Price/Entry and exact candle anchor are not uniquely established.

### B3 Structural SL

Still unresolved. `0.0` appears to be a stop-side measurement reference, but its exact mapping to the structural invalidation boundary and terminal SL is not yet source-unique.

### B6 Leg2 / TP

Still unresolved. `1` and `2` are deliberate source measurement levels, and TP is explicitly populated in the terminal, but exact formula, anchor, and execution semantics remain unresolved.

### 2x

Strong source-correlated candidate; official 50% secondary-entry description provides independent corroboration; still not frozen.

## 9. Non-inference boundary

This pass does not promote:

- `E = Entry`;
- `0.0 = SL`;
- `1 = 1R`;
- `2 = 2R`;
- `TP = 2R`;
- `2x = exact midpoint`;
- any A/B/C/D anchors;
- any wick/body rule;
- any trigger rule;
- any pending-order lifecycle rule.

## 10. Gate decision

**SOURCE RESOLUTION remains BLOCKED at executable geometry.**

The next highest-value task is not backtesting. It is to obtain source-text/audio evidence that explicitly explains the level stack, or to locate additional source frames where the measurement object is visibly created/anchored at the same moment as an order and the mapping can be established without inference.
