# SP2L Source-to-Code Reconciliation Audit — 2026-09-22

## Scope

Read-only reconciliation of the current Strategy A domain implementation against the source-resolution boundary established by the archived primary evidence.

No performance result is used to choose an interpretation. No canonical production rule is promoted.

## Findings

### 1. P-Gap

**Source:** semantic relationship is source-confirmed; executable OHLC/index geometry remains unresolved.

**Current code:** `PGAPResearch.ts` explicitly implements a three-candle imbalance heuristic:
- bullish: `right.low > left.high`
- bearish: `right.high < left.low`
- fixed `i-2 / i` indexing.

The module itself labels this as research-only and says it is not validated as P-Gap.

**Reconciliation:** correctly isolated as research evidence. The formula must NOT be promoted to canonical P-Gap.

### 2. Spike

**Source:** Spike concept and breakout/follow-through relationship are source-supported; exact executable spike grammar is not frozen.

**Current code:** `SpikeDetector.ts` applies implementation-defined parameters `maxCandles`, `minDirectionalFraction`, and `maxOverlapFraction`, then derives start/end prices from window wick extremes.

**Reconciliation:** this is a research-stage heuristic, not source-frozen geometry. It must remain non-canonical.

### 3. Correction / Entry

**Source:** correction is the entry phase; Pending Limit and evolving structural reference are demonstrated. Exact executable entry anchor and fill semantics remain unresolved.

**Current code:** `CorrectionDetector.ts` chooses the first post-spike candle whose low/high penetrates `spike.startPrice`, then `EntryTrigger.ts` waits for the first later candle whose close reclaims the correction extreme and uses that close as `entryPrice`.

**Reconciliation:** this is materially narrower/more specific than the source evidence. In particular:
- first correction extreme is an implementation choice;
- close-reclaim activation is not source-frozen;
- market-style entry at the reclaim close is not equivalent to the demonstrated Pending Limit lifecycle;
- fill=C is not authorized.

Therefore `EntryTrigger.ts` remains non-canonical.

### 4. Leg1 / AB=CD

**Source:** AB=CD / Leg2≈Leg1 magnitude is source-confirmed; A/B/C/D anchors, price field, and tolerance remain unresolved.

**Current code:** `LegProjection.ts` defines:
- Leg1 start = `spikeStartIndex`;
- Leg1 end = `spikeEndIndex`;
- size = `abs(last.close - first.open)`;
- projection origin = `correction.extremePrice`;
- TP1 = origin ± Leg1 size.

**Reconciliation:** every executable geometric choice above is implementation-derived rather than source-confirmed. In particular, the source does not authorize the selected open/close endpoints, correction extreme as C, or the projection formula.

`LegProjection.ts` must therefore remain research/non-canonical.

### 5. Stop / invalidation

**Source:** structural invalidation is distinct from risk budget; source evidence ties the SL concept to the spike-origin/base structural area. Exact OHLC field and invalidation event remain unresolved.

**Current code:** `CorrectionDetector` and related legacy flow derive geometry from `spike.startPrice`; exact source alignment cannot be claimed from the current modules alone.

No SL field, wick/body convention, buffer, or close/touch rule should be frozen from this implementation.

## Canonical boundary

The current repository code contains useful deterministic research machinery, but the following implementation semantics must not be mistaken for canonical Strategy A:

| Area | Current implementation | Source status | Canonical? |
|---|---|---|---|
| P-Gap | 3-candle wick-gap heuristic | Geometry unresolved | NO |
| Spike | directional/overlap thresholds | Grammar unresolved | NO |
| Correction | first penetration of spike start | Exact rule unresolved | NO |
| Entry | close reclaim of correction extreme | Trigger/fill unresolved | NO |
| Leg1 | spike start→end, open/close measurement | A/B unresolved | NO |
| Projection | correction extreme + Leg1 size | C/tolerance unresolved | NO |
| 2X | research candidates elsewhere | Lifecycle incomplete | NO |
| SL | research spike-origin concepts | exact price/invalidation unresolved | NO |

## What is source-aligned today

The codebase can safely preserve these as semantic/research constraints:
- SP2L means Spike → 2 Leg.
- P-Gap is a distinct source concept associated with valid breakout; executable geometry unresolved.
- Correction is an entry phase.
- Pending Limit is part of the demonstrated model.
- Entry and structural invalidation are distinct concepts.
- AB=CD / Leg2≈Leg1 is source-confirmed as a magnitude relationship.
- 2X is a secondary/optional concept with source evidence for a half-target-related context.
- Bearish examples exist, but executable bearish mirror geometry remains unresolved.

## Required action before Frozen Geometry

Do **not** rewrite these modules into a guessed canonical implementation.

Instead, retain them as research/legacy layers and require any future canonical layer to consume only source-frozen primitives after the remaining blockers are uniquely resolved.

Remaining blockers:
1. P-Gap executable boundaries/indexing.
2. Exact SL/invalidation price semantics.
3. Pending-order refresh predicate.
4. Trigger variant precedence and activation semantics.
5. F14 A/B/C/D anchors and tolerance.
6. F13 complete 2X lifecycle.

## Gate

**Source-to-Code Reconciliation: COMPLETE for current archived evidence.**

**Canonical implementation: NOT SOURCE-COMPLETE.**

**Frozen Geometry: BLOCKED.**

**Untouched Validation / Fresh Holdout: LOCKED.**

**Production: OFF.**

No canonical production code changed.
