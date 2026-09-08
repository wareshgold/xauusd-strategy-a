# Strategy A / SP2L — Source-to-Code Sync Audit

Date: 2026-09-08
Branch: `research/source-aligned-sp2l-semantics-v1`

## Executive result

The repository's research path is aligned with the teacher's source-first methodology, but the legacy deterministic Strategy A modules are **not** a canonical implementation of the source SP2L semantics.

This branch therefore adds a source-aligned semantic layer without changing production behavior and without guessing unresolved geometry.

## Source-confirmed meanings

| Concept | Source status | Legacy code status | Action |
|---|---|---|---|
| SP2L = Spike -> 2 Leg | confirmed | partially represented | preserve semantic label |
| Spike follows range/context and is a sharp directional movement | confirmed | heuristic detector | do not freeze heuristic as canonical |
| Breakout + follow-through | confirmed | implemented approximately | keep as research candidate until full grammar is frozen |
| Valid breakout associated with P-GAP | direct video evidence + ledger | generic gap heuristic only | require explicit source confirmation |
| P-GAP distinct from E-GAP/Common/Morning Gap | confirmed | not encoded canonically | do not collapse all gaps into one flag |
| AB = CD / Leg 2 magnitude equals Leg 1 | direct video evidence | projection exists | measure only from source-confirmed anchors |
| Pending-limit entry during correction | confirmed | close-reclaim market-style trigger | canonical layer must use pending-limit semantics |
| Fill price equals C | **not established** | risk of implicit conflation | explicitly forbid the substitution |
| Structural invalidation / no SL widening | confirmed | separate legacy logic exists | preserve source rule |

## Important conflicts

### 1. P-GAP
`PGAPResearch.ts` detects a three-candle imbalance as a research observation. It explicitly does not establish that observation as the teacher's P-GAP. This remains correct and must not be silently promoted.

### 2. Spike
`SpikeDetector.ts` uses directional fraction and overlap thresholds around breakout/follow-through events. These are research heuristics, not source-derived spike grammar. They remain non-canonical.

### 3. Entry
`EntryTrigger.ts` currently implements `CORRECTION_EXTREME_RECLAIM` using a later candle close. That is not the demonstrated canonical SP2L entry semantics in the source, where a pending limit can be placed during correction. The new source-aligned layer therefore does not reuse this trigger.

### 4. Leg 1 / Leg 2 geometry
`LegProjection.ts` currently measures Leg 1 as `abs(last.close - first.open)` and projects from `correction.extremePrice`. The source confirms AB=CD but does not, in the available material, freeze those exact OHLC anchors. The new layer requires source-confirmed A/B/C points instead of inventing them.

## New guardrails

`src/domain/strategy-a/SourceAlignedSP2L.ts` provides:

- explicit `P_GAP` source-confirmation type;
- explicit source-confirmed Leg 1 A/B prices;
- explicit source-confirmed correction C price;
- explicit pending-limit entry semantics;
- AB=CD projection using the supplied source-confirmed anchors;
- no invented equality tolerance;
- hard rejection of unconfirmed P-GAP evidence.

## What this branch deliberately does NOT do

- no production Strategy A replacement;
- no automatic P-GAP formula invention;
- no selection of G4/G5 anchors without source visual evidence;
- no ATR/tick/percentage tolerance invention;
- no Fresh Holdout access;
- no profitability-driven semantic changes.

## Next canonical step

Use the supplied source-video frames to identify the exact visual A/B/C/D anchors and P-GAP geometry. Once those are source-confirmed, wire the canonical detector/entry/projection path to this semantic layer, then run synthetic fixtures -> DEV -> untouched VAL -> robustness -> Fresh Holdout.
