# SP2L G312 — Round Level Reconciliation

**Date:** 2026-09-12
**Status:** `ROUND_LEVEL_SOURCE_CONFIRMED__SELECTOR_UNRESOLVED`

## Direct source finding

Around ~43:40 the source writes `Round level 2` next to the target construction. Around ~44:00 it shows price examples including 2500, 3200, 3255 and 3250.

This confirms Round Level is part of the source discussion.

## Unresolved

The frames do not establish:
- what increment defines a Round Level;
- whether `2` is a level number, multiplier, category, or another annotation;
- whether TP1 or TP2 must lie on a Round Level;
- whether Round Level is a target selector, context/filter, or explanatory example;
- whether Round Level overrides Point Distance or AB=CD;
- SELL-side mirror;
- tie-breaking between multiple candidate levels.

## Decision

`ROUND_LEVEL_CONCEPT = SOURCE-CONFIRMED`
`ROUND_LEVEL_FUNCTION = UNRESOLVED`
`ROUND_LEVEL_SELECTOR = UNRESOLVED`
`TARGET_OVERRIDE_RULE = UNRESOLVED`
`CANONICAL_ROUND_LEVEL_ENGINE = NOT_AUTHORIZED`
