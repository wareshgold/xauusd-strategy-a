# SP2L Entry / Invalidation / Trigger / 2X Resolution v1 — 2026-09-09

## Gate

**SOURCE RESOLUTION: PARTIAL PASS.**

This document records discrimination fixtures and the current evidence state. It does not freeze a production trading specification.

## Primary evidence

The primary evidence is the creator's SP2L video, recovered transcript, and direct frame inspection. The source explicitly demonstrates pending Buy Limit orders, structural SL/invalidation, 1/2/3-candle trigger examples, and 2X terminology. The source ledger records these concepts as confirmed while preserving unresolved geometry. See `docs/research/SP2L_SOURCE_LEDGER_V1_2026-09-09.md`.

## 1. Entry

### Confirmed

- Entry is a **pending limit** mechanism.
- The teacher demonstrates placing the order before the correction completes rather than requiring a market close-reclaim.
- Visual evidence shows an Entry/Buy Limit level distinct from the later Leg-2/target region.
- Source language refers to the first Low, while visual examples also show a relevant/current higher-low level.

### Competing interpretations retained

1. first structural Low/High;
2. relevant/current higher Low/High;
3. start of Leg 2.

### Current resolution

**Do not freeze a universal exact price anchor.** The safe canonical abstraction remains:

`Correction → Relevant Structural Low/High → Pending Limit`

`Entry = Leg2Start` is rejected as a canonical assumption because direct visual evidence separates Entry from the Leg-2/target region.

Wick extreme vs body edge also remains unresolved.

## 2. Structural invalidation

### Confirmed

- The stop/invalidation is structural.
- The source explicitly shows SL and discusses deleting/replacing a pending order when subsequent structure changes the risk distance materially.
- Therefore a generic fixed-distance stop is not source-aligned.

### Competing interpretations retained

- structural/base Low/High;
- local Entry-adjacent Low/High;
- fixed-distance proxy (retained only as a negative/discrimination fixture).

### Current resolution

The strongest source-aligned interpretation is **structural/base invalidation**, but the exact anchor is not frozen.

The source discussion implies a material-change condition for pending-order replacement, but no deterministic numeric threshold has been authorized. No percentage, ATR multiple, candle count, or pip threshold is introduced here.

## 3. Trigger

### Confirmed

The source explicitly discusses examples involving **1 candle, 2 candles, and 3 candles** as trigger constructions. This establishes a trigger concept and a family of observed candle-count forms, not a universal trigger formula.

### Current resolution

Trigger taxonomy and acceptance criteria remain unresolved. In particular, the implementation must not silently convert Trigger into:

- market close-reclaim;
- generic engulfing pattern;
- generic BOS/MSS;
- arbitrary candle-count rule.

The fixtures preserve the three observed candle-count forms for later frame-by-frame discrimination.

## 4. 2X

### Confirmed

The source explicitly uses the term **2X** and describes a half-target-type trigger/management concept. The source also shows 2X in annotated examples.

### Current resolution

The exact 2X formula and reference levels are unresolved. Competing candidate interpretations remain visible in the fixtures only; none is promoted to production.

Do not assume that 2X is simply `2R`, nor that its reference is necessarily Entry, SL, Leg 2, or TP without direct source confirmation.

## 5. Negative findings

The following remain non-canonical unless separately source-confirmed:

- market-close reclaim as replacement for pending limit;
- fixed-distance stop;
- arbitrary ATR/pip/percentage replacement threshold;
- BOS/MSS/displacement as trigger definitions;
- generic three-candle imbalance/FVG as P-Gap or Trigger;
- `Entry = Leg2Start`.

## 6. Synthetic fixture status

Fixture file:
`research/fixtures/sp2l_entry_invalidation_trigger_2x_discrimination_v1.py`

Test file:
`research/fixtures/test_sp2l_entry_invalidation_trigger_2x_discrimination_v1.py`

The fixtures are designed to test **interpretation discrimination**, not profitability. No historical optimization is performed.

Execution status: **NOT CLAIMED HERE**. The files have been committed, but this document intentionally does not assert a local test-run result unless a reproducible test command and output are captured separately.

## 7. Gate decision

**SOURCE RESOLUTION remains PARTIAL PASS.**

Resolved enough to encode as source-confirmed concepts:

- pending-limit entry;
- structural invalidation;
- trigger concept with 1/2/3-candle examples;
- 2X concept.

Not resolved enough for frozen production geometry:

- exact Entry price anchor;
- wick/body edge;
- exact invalidation anchor;
- pending-order replacement threshold/timing;
- Trigger taxonomy/acceptance criteria;
- 2X formula/reference levels.

Therefore the project must **not** advance to historical DEV optimization or production implementation on the basis of these unresolved interpretations.
