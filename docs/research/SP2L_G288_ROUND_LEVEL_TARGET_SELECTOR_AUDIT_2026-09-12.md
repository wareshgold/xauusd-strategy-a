# G288 — Round Level Target Selector Audit

Date: 2026-09-12
Source frames: primary SP2L video, approximately 43:40–44:06.

## Observation
The presenter explicitly writes `Round level 2` and then shows numeric examples around `2500`, `3200`, and `3255/3250` while the TP1/TP2/Entry/SL construction remains on screen.

## Source-confirmed meaning boundary
`Round level` is a source concept used in the target-construction discussion.

## Unresolved selector semantics
The frames do not establish:
- the exact round-level increment;
- whether the number `2` is a level-count, selector, or example label;
- whether TP1 or TP2 must be placed on a round level;
- whether round level overrides point distance;
- whether round level is context/filter information rather than a target selector;
- how ties between candidate levels are resolved;
- SELL-side mirroring.

## Decision
Do not implement a round-number function, increment, nearest-level rule, or target-selection priority from this evidence.

Status: `ROUND_LEVEL_CONFIRMED__TARGET_SELECTOR_UNRESOLVED`
