# SP2L C01–C08 Human Adjudication Briefs — 2026-09-15

## Purpose

This document converts the persistent source-video audit into eight concise human-review briefs. It is an input to Issue #175 only. It does not adjudicate source meaning and does not freeze geometry.

## Human decision contract

For every candidate, the adjudicator must answer:

1. Does the source itself contain a precise discriminator for the stated dimension?
2. Is that discriminator reproducible from the recorded source evidence?
3. Does it uniquely eliminate the competing hypotheses without importing generic technical-analysis convention?
4. Does using it require an invented formula, threshold, buffer, candle index, fill rule, or symmetry assumption?

Allowed outcomes are exactly:

- `SOURCE_DISCRIMINATED`
- `REMAINS_BLOCKED`

AI may prepare the evidence and questions. AI must not decide the source meaning on behalf of the human adjudicator.

## Review briefs

### C01 — P-Gap

**Dimension:** `p_gap`

**Source evidence:** `35:53–36:30`, especially `36:16` and `36:30`.

**Source explicitly shows:** three numbered spike constructions; shaded P-Gap regions; repeated `Valid BO = P-Gap`; a separate invalid/red-X example; P-Gap used as part of breakout validity.

**Not explicitly provided:** exact upper/lower OHLC boundary; exact candle-index formula; general executable rule resolving all visually similar cases.

**Human discriminator question:** Can the source-visible shaded region be mapped to one unique, reproducible candle/price boundary using only what the source explicitly teaches?

**Guardrail:** Do not substitute a generic three-candle imbalance/FVG definition.

**Pre-adjudication:** `BLOCKED`

### C02 — Entry Anchor

**Dimension:** `entry_anchor`

**Source evidence:** `38:40–40:10`, especially `39:40`.

**Source explicitly shows:** correction after the spike/continuation sequence; `Buy Limit` on a horizontal reference; SL separately below; pending entry during correction.

**Not explicitly provided:** whether the entry anchor is open/close/high/low/body boundary/midpoint/gap edge/another exact price; universal candle indexing.

**Human discriminator question:** Does the source explicitly identify the exact candle/price feature defining the Buy Limit level, or only demonstrate the level visually?

**Guardrail:** Do not infer an OHLC anchor from drawing geometry.

**Pre-adjudication:** `BLOCKED`

### C03 — Leg-2 Start / AB=CD

**Dimensions:** `leg2_start`, with source evidence relevant to `abcd_anchors` and `abcd_tolerance`.

**Source evidence:** `36:30–37:20`.

**Source explicitly shows:** handwritten `AB=CD`; candle-level spike/correction/second-leg construction; repeated presentation; `1M / 5M` annotations.

**Not explicitly provided:** unique A/B/C/D anchors; exact Leg-2 start candle/price; numerical tolerance.

**Human discriminator question:** Does the source itself identify the four AB=CD anchors and an exact equality/tolerance rule, rather than only expressing the semantic relationship?

**Guardrail:** Do not import classical Fibonacci AB=CD definitions or choose anchors because they backtest well.

**Pre-adjudication:** `BLOCKED`

### C04 — TP1 / TP2 / 2X

**Dimension:** `targets_2x`

**Source evidence:** `41:45–42:40` and `44:30–44:50`.

**Source explicitly shows:** `Buy`, `2X`, `SL`; a clean diagram with `TP1`, `TP2`, `Entry`, `SL`; point-distance examples including `250 point` and `500 point`.

**Not explicitly provided:** universal TP1 formula; universal TP2 formula; exact 2X price/size/risk formula; unambiguous unit/indexing semantics sufficient for execution.

**Human discriminator question:** Does the source explicitly define reproducible target and 2X formulas, or only illustrate concepts/examples?

**Guardrail:** Do not derive a formula from one worked example.

**Pre-adjudication:** `BLOCKED`

### C05 — Bearish Mirror

**Dimension:** `bearish_mirror`

**Source evidence:** `62:35–64:35`.

**Source explicitly shows:** bearish chart sequence; declining structure and highlighted regions; continued bearish movement with later markings.

**Not explicitly provided:** complete field-by-field bullish-to-bearish mapping; proof that every bullish rule is mirrored with sign reversal.

**Human discriminator question:** Does the source explicitly state the bearish mapping, or is the mapping only inferred from symmetry?

**Guardrail:** Inferred symmetry is not source evidence.

**Pre-adjudication:** `BLOCKED`

### C06 — Pending Refresh / Delete

**Dimension:** `pending_refresh`

**Source evidence:** `40:20–40:40`.

**Source explicitly shows:** `Delete` annotation; subsequent changed/redrawn setup; pending state can change as later structure develops.

**Not explicitly provided:** exhaustive delete/replace/retain predicate; universal numerical threshold/buffer; exact candle indexing for every branch.

**Human discriminator question:** Does the source explicitly state the condition causing delete, replacement, or retention, or only demonstrate that lifecycle changes can occur?

**Guardrail:** Do not invent a distance threshold or use implementation convenience.

**Pre-adjudication:** `BLOCKED`

### C07 — Trigger Classifier

**Dimension:** `trigger_classifier`

**Source evidence:** `35:53–36:17`.

**Source explicitly shows:** three numbered constructions `1`, `2`, `3`; multiple valid spike constructions; connection to P-Gap breakout-validity discussion.

**Not explicitly provided:** exhaustive machine-testable classifier; complete candle-index/boundary conditions; proof that the three visible constructions exhaust every valid trigger state.

**Human discriminator question:** Does the source explicitly define all conditions needed to classify every valid trigger into the 1/2/3 family?

**Guardrail:** Do not convert the visual numbering into an arbitrary candle-count algorithm.

**Pre-adjudication:** `BLOCKED`

### C08 — Correction / Structural Invalidation

**Dimension:** `structural_invalidation`

**Source evidence:** `38:40–40:40` plus the previously recorded transcript evidence around correction/invalidation.

**Source explicitly shows:** correction after bullish construction; lower horizontal reference; Buy Limit and separate SL; delete/lifecycle behavior when structure changes.

**Not explicitly provided:** exact OHLC invalidation boundary; wick-vs-close-vs-other event; universal candle indexing.

**Human discriminator question:** Does the source explicitly define the exact event/price boundary that invalidates the setup?

**Guardrail:** Do not equate structural invalidation with risk-stop/fill unless source explicitly does so.

**Pre-adjudication:** `BLOCKED`

## Adjudication order

`C01 → C02 → C08 → C03 → C04 → C05 → C06 → C07`

The order is operational only; it is not an inference of strategy logic.

## After human adjudication

1. Record one valid `ManualAdjudication` per candidate/dimension set.
2. Preserve complete provenance and rationale.
3. Run Frozen Geometry Readiness (#179).
4. If and only if all ten executable dimensions are source-discriminated and reproducible, execute the separate canonical freeze decision (#180).
5. Otherwise preserve `REMAINS_BLOCKED` and continue only with genuinely new Tier-1/Tier-2 discriminating evidence.

## Explicit prohibition

This brief package must not be used to freeze geometry, define execution/fill semantics, choose hypotheses by backtest performance, infer bearish symmetry, generate BUY/SELL, or authorize production.
