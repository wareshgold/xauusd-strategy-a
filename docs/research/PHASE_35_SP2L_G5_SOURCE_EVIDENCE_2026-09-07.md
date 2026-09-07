# Phase 35 — SP2L G5 Source Evidence

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — no production Strategy A changes

## Objective

Continue G5 using the preserved Pour Samadi SP2L transcript, focusing on the worked example around 1:03:03–1:04:32.

## Source evidence

### 1:03:03–1:03:13 — nested 2Leg versus parent leg

The source explicitly describes an outer first leg and second leg, then notes that the move itself contains its own 2Leg structure and reaches its own TP.

Semantic consequence:

- a visible move can contain a nested 2Leg;
- the intended parent Leg 2 must be resolved at the parent scenario scale;
- nested TP/Leg boundaries must not automatically become the parent projection origin.

### 1:03:19 — correction separates the parent legs

The teacher states that the main scenario treats one large segment as one leg and the other large segment as the next leg, and that **from the deep correction** the next leg runs from one source-selected chart point to another.

This strengthens the already established ordering:

```text
LEG 1 -> DEEP CORRECTION -> LEG 2
```

It also provides direct source evidence that the parent Leg 2 origin is associated with the intervening correction structure.

### 1:04:00–1:04:19 — deep leg and order placement

The teacher says that when uncertain he waits for a deep leg, identifies where that deep leg starts visually, observes a sequence of lower highs, and places the order at the shown level.

The transcript then states that the order is moved down until it becomes activated and immediately describes the first leg as the segment between two visually indicated chart points.

Important distinction:

- order placement/fill is explicitly part of the execution sequence;
- Leg 1 is separately described as a visual structural segment;
- therefore the transcript does not prove that Leg 1 starts/ends at the order fill.

### 1:04:19–1:04:32 — activation and TP1

The source says the order is moved until activated and that the SP2Leg target is then derived from the Leg 1 segment. It identifies the resulting TP as the reward-1 target.

This confirms that the projected target is downstream of the source-selected Leg 1 measurement, but the transcript still does not expose the exact numerical C price.

## G5 conclusion

G5 can now be split into two levels:

### G5-A — semantic origin

**SOURCE-CONFIRMED:** Leg 2 begins from the structural/intervening correction of the intended parent leg scenario.

The strongest wording in the preserved source is the explicit parent scenario statement that the next leg comes **from its deep correction**.

### G5-B — executable OHLC coordinate

**STILL TBD.**

The transcript does not encode which exact candle price inside the visually shown correction is the machine-readable C coordinate.

The remaining candidates are:

1. correction extreme;
2. selected structural HL/LH price;
3. pending-limit price;
4. actual fill price;
5. another source-selected visual structural point.

The evidence now makes candidate (5) particularly important: the teacher repeatedly refers to points by pointing at chart locations rather than defining them with an OHLC formula.

## Critical non-equivalence

Do not convert:

```text
Leg 2 starts from the deep correction
```

into:

```text
Leg2Origin = correction.low/high
```

without source evidence for that exact OHLC mapping.

Likewise, do not convert order activation into:

```text
Leg2Origin = fillPrice
```

The source sequence contains both concepts, but the transcript does not establish them as identical.

## New research decision

G5 semantic ordering is now **stronger than before**:

```text
PARENT LEG 1
    -> DEEP / INTERVENING CORRECTION
    -> PARENT LEG 2
```

Exact C coordinate remains **TBD**.

This is sufficient to update the research model so that G5 is represented as a source-selected correction-origin concept rather than an arbitrary projection point, while preserving the exact price coordinate as unresolved.

## Guardrails

- No production Strategy A changes.
- No historical performance used to resolve source meaning.
- No equality tolerance fitted.
- No P-GAP threshold invented.
- Fresh Holdout remains LOCKED.
- 2X remains separate.

## Next step

Create a source-shaped G5 semantic fixture that distinguishes:

- correction-origin concept;
- pending-limit/fill event;
- exact C price as explicit TBD;

and verifies that the semantic engine cannot silently substitute fill price for the unresolved C coordinate.
