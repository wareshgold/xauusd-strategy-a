# SP2L G299 — Geometry ↔ Execution Reconciliation Audit

**Date:** 2026-09-12  
**Status:** `SOURCE_RECONCILIATION_ONLY__FROZEN_GEOMETRY_BLOCKED`  
**Purpose:** Reconcile source-confirmed semantics against the current research implementation before any further performance interpretation or canonical freeze.

## 1. Scope

This audit compares the source ledger against the current Strategy A research implementation across the complete executable chain:

`P-Gap → Spike → Correction → Entry → SL → Leg 1 / AB=CD → TP1/TP2 → terminal target → execution semantics`

The audit is deliberately non-corrective. It records mismatches and unresolved geometry; it does **not** modify the Strategy A implementation.

## 2. Evidence hierarchy

1. Raw authoritative source material
2. Source visual evidence / extracted chart frames
3. Source ledger and canonical meaning map
4. Frozen deterministic rule specification
5. Implementation
6. Historical research / statistical validation

A research implementation cannot promote a hypothesis to canonical meaning merely because it produces attractive historical results.

## 3. Reconciliation matrix

| Component | Source status | Current research implementation | Classification | Prohibited inference | Required evidence |
|---|---|---|---|---|---|
| P-Gap | Valid breakout associated with P-Gap is source-supported; bullish endpoint relation is partially supported | Research fixtures include bullish gap candidates | `SOURCE-CONFIRMED / PARTIAL GEOMETRY` | Do not assume equality handling, minimum gap, bearish mirror, timing, or generic FVG equivalence | Explicit source OHLC definition for all directions/edge cases |
| Spike | Directional sharp movement is source-supported; valid Spike associated with P-Gap | Detector supplies executable SpikeCandidate | `SOURCE-CONFIRMED SEMANTIC / HYPOTHESIS GEOMETRY` | Do not assume a particular candle-count, magnitude, wick/body rule, or origin anchor | Source-defined construction and examples sufficient for deterministic detection |
| Correction | Source says bullish correction reaches previous candle low; bearish mirror reaches previous candle high | Current detector searches for first later low below `spike.startPrice` or high above it | `SOURCE-CONFIRMED SEMANTIC / IMPLEMENTATION MISMATCH` | Do not equate source correction reference with Spike origin price | Source sequence identifying the exact reference candle/price and first-valid-correction rule |
| Entry | Pending Buy Limit / Sell Limit mechanism is source-supported | Current EntryTrigger waits for close reclaim and sets entry equal to candle close | `SOURCE-CONFIRMED MECHANISM / IMPLEMENTATION MISMATCH` | Do not replace pending-limit with market close-reclaim; do not assume fill=C, correction extreme, E, or 2x | Source order example or explicit statement giving the pending-limit price anchor |
| Structural SL | Source says SL is behind the candle from which the Spike originated | Current invalidation level is correction extreme and invalidates on candle close | `SOURCE-CONFIRMED SEMANTIC / IMPLEMENTATION MISMATCH` | Do not infer origin Low/High, body edge, buffer, spread adjustment, or close/intrabar semantics | Source example with executable SL price or explicit OHLC boundary |
| Leg 1 | AB=CD relationship is source-confirmed; second-leg continuation is source-supported | Current Leg 1 = `abs(spikeEnd.close - spikeStart.open)` | `SOURCE-CONFIRMED RELATION / ANCHORS UNRESOLVED` | Do not freeze open→close, wick→wick, body→body, or any other A/B/C/D anchors | Source schematic/example explicitly identifying A/B/C/D |
| AB=CD | Explicit source relationship | Current implementation uses a single derived leg size rather than source-confirmed A/B/C/D geometry | `SOURCE-CONFIRMED SEMANTIC / UNRESOLVED GEOMETRY` | Do not invent tolerance or equate AB=CD endpoint with TP | Source equation/diagram with named anchors and equality semantics |
| TP1 / TP2 | Both target levels are source-visible and source-discussed | Current research projection exposes TP1 only from the hypothesis above | `SOURCE-CONFIRMED CONCEPT / FORMULA UNRESOLVED` | Do not assume TP1=1R, TP2=2R, TP1=250 points, TP2=500 points | Worked example tying target labels to numeric prices/equations |
| Round Level | Source concept explicitly shown in target construction | Selector/increment/priority unresolved | `SOURCE-CONFIRMED CONCEPT / UNRESOLVED SELECTOR` | Do not implement nearest round level, fixed increment, or terminal-target override | Explicit source instruction connecting round level to TP selection |
| Point Distance | 250/500/1000 point vocabulary is source-visible | Exact unit and mapping to targets unresolved | `SOURCE-CONFIRMED VOCABULARY / UNRESOLVED GEOMETRY` | Do not equate 250=TP1 or 500=TP2 solely from visual proximity | Source statement/equation or order example with matching numeric distances |
| Terminal TP | Order panels contain concrete TP values | Selection logic is not source-frozen | `UNRESOLVED` | Do not assume final TP=2R, AB=CD endpoint, TP2, round level, or fixed distance | Continuous worked example linking final TP to its construction |
| Execution semantics | Pending order is source-supported; exact stop/target hit semantics unresolved | Phase40 counterfactual uses intrabar high/low first-hit; current invalidation uses close-based invalidation | `UNRESOLVED / IMPLEMENTATION MISMATCH` | Do not treat either convention as canonical | Source material explicitly defining intrabar/close/touch/fill ordering |

## 4. Current implementation facts

### Entry

The current `EntryTrigger.ts` explicitly implements a **close-reclaim** model: after the correction extreme, the first candle closing beyond the extreme becomes the entry price. The trigger reason is `CORRECTION_EXTREME_RECLAIM`. This is directly visible in the implementation and is not equivalent to the source-confirmed pending-limit mechanism. 

Source file: `src/domain/strategy-a/EntryTrigger.ts`.

### Correction

The current detector defines bullish correction through `low < spike.startPrice` and bearish correction through `high > spike.startPrice`. This is an executable research hypothesis, not a frozen source geometry.

Source file: `src/domain/strategy-a/CorrectionDetector.ts`.

### Stop / invalidation

The current invalidation rule uses `correction.extremePrice` and declares invalidation only when the candle close crosses that level. This differs from the source semantic of a structural stop behind the Spike-origin candle.

Source file: `src/domain/strategy-a/Invalidation.ts`.

### Leg 1 / projection

The current projection defines Leg 1 as the absolute difference between `spikeEnd.close` and `spikeStart.open`, then projects from the correction extreme. Neither anchor chain is source-frozen.

Source file: `src/domain/strategy-a/LegProjection.ts`.

## 5. Execution-semantics conflict

The Phase40 counterfactual audit uses next-candle high/low first-hit semantics for the flipped SELL scenario, while the current invalidation component is close-based. G298 already records this mismatch. Therefore the counterfactual R series cannot be interpreted as an execution-equivalent replay of the current engine, much less as canonical Strategy A evidence.

## 6. Required source-resolution work

The next research passes must prioritize a continuous worked example rather than parameter optimization:

1. Identify the exact Spike-origin candle.
2. Identify the exact P-Gap endpoints.
3. Identify the exact correction reference candle/price.
4. Identify the actual pending-limit Entry price.
5. Identify the actual structural SL price and its OHLC boundary.
6. Identify A/B/C/D for the source AB=CD relationship.
7. Map Leg 1 and Leg 2 to the displayed TP1/TP2 levels.
8. Reconcile the 250/500/1000 point annotations with actual price distances.
9. Determine the role and selection logic of Round Level.
10. Determine whether execution is touch/intrabar/close and how simultaneous hits are resolved.

## 7. Gate decision

`SOURCE_RESOLUTION = PARTIAL_PASS`

`FROZEN_GEOMETRY = BLOCKED`

`DEV = BLOCKED_FOR_CANONICAL_STRATEGY`

`VALIDATION = PROTECTED / NO PROMOTION`

`FRESH_HOLDOUT = NOT_AUTHORIZED`

`PRODUCTION = BLOCKED`

## 8. Explicit non-actions

This audit does **not**:

- change EntryTrigger.ts;
- change CorrectionDetector.ts;
- change Invalidation.ts;
- change LegProjection.ts;
- reinterpret the 65.913577R observation;
- trim/cap/delete outliers;
- select a better-performing geometry;
- introduce a bearish mirror by assumption;
- convert P-Gap into FVG;
- declare TP1/TP2 as 1R/2R;
- declare 250/500 as executable target distances;
- declare Round Level as a target selector.

## 9. Decision

**G299 records the geometry ↔ execution reconciliation boundary and makes no canonical Strategy A changes.** The project remains explicitly uncertain wherever source geometry is not uniquely resolved. The next gate is additional source reconstruction of a continuous worked example, followed only by synthetic-fixture discrimination and a frozen geometry decision.
