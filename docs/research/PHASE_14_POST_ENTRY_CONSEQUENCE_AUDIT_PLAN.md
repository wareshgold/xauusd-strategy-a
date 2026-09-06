# Phase 14 — Post-Entry Consequence Audit Plan

## Objective

Audit whether the canonical Strategy A codebase already defines a deterministic **post-entry structural consequence** that can be measured without inventing a new price-action rule.

The purpose is methodology validation, not optimization or exit-rule discovery.

## Canonical-source audit

The current Strategy A detectors define the following deterministic chain:

1. Breakout
2. Follow-through
3. Spike candidate
4. Correction extreme
5. Entry trigger

`EntryTrigger` explicitly starts at `correctionExtremeIndex + 1` and returns the first candle whose close reclaims the correction extreme in the spike direction. Therefore the trigger is the end of the pre-entry setup chain, not a post-entry consequence.

`CorrectionDetector` likewise defines correction extremes only after the spike and before the entry trigger. `SpikeDetector` defines the impulse window around breakout/follow-through. These components do not expose a canonical post-entry structural-event detector.

## Decision rule

Do **not** manufacture new definitions such as:

- favorable-first,
- adverse-first,
- reclaim-first,
- structural break after entry,

unless those events are already represented by a canonical detector/contract in Strategy A.

A generic candle move after entry is not sufficient to call something a structural consequence.

## Research constraints

- Canonical baseline universe only.
- Preserve existing DEV/VAL cutoff: `entryIndex < 6000` DEV, `6000 <= entryIndex < 10000` VAL.
- Fresh holdout remains locked.
- No threshold search.
- No horizon selection.
- No detector changes.
- No production changes.
- No retrospective outcome-derived event definitions.
- No new trading rule.

## Audit result

The canonical detector chain currently provides no dedicated post-entry structural consequence primitive. Consequently, a Phase 14 implementation based on invented `FAVORABLE_FIRST`, `ADVERSE_FIRST`, or `RECLAIM_FIRST` semantics would violate the research-first methodology.

Therefore **Phase 14 should not be implemented as a trading-rule research experiment**.

## Next research direction

Return to the pre-entry side and investigate setup/entry quality using only deterministic geometry already available from the canonical chain. Candidate research should be selected ex ante and validated across chronological DEV/VAL segments before touching the fresh holdout.

The existing reclaim-to-range finding remains descriptive only and must not be promoted into a threshold/rule without a new independent hypothesis.

## Status

`PHASE_14_STATUS=ABORTED_BEFORE_BUILD`

`REASON=NO_CANONICAL_POST_ENTRY_STRUCTURAL_EVENT`

`NO_OPT`

`NO_THRESHOLD_SEARCH`

`NO_HORIZON_SELECTION`

`NO_NEW_RULE`

`NO_FRESH`

`PRODUCTION_UNCHANGED`
