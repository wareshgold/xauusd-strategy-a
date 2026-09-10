# SP2L G254 — Target Decision Matrix

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `REFERENCE_GEOMETRY_PARTIAL__SELECTOR_BLOCKED`

## Purpose

Consolidate target-related source evidence into a deterministic decision matrix without promoting unresolved interpretations.

| Concept | Source status | Canonical now? | Executable rule? |
|---|---|---:|---:|
| TP1 reference | bullish schematic source-confirmed | YES, semantic/reference only | YES for reference calculation once Entry/SL are known |
| TP2 reference | bullish schematic source-confirmed | YES, semantic/reference only | YES for reference calculation once Entry/SL are known |
| Round level | source-taught concept | YES as concept | NO |
| Point distance | source-taught concept | YES as concept | NO |
| AB=CD | source-confirmed relationship | YES as semantic relationship | NO, anchors unresolved |
| Terminal TP | explicit in worked orders | YES as field/concept | NO selector unresolved |
| TP1 vs TP2 selection | not uniquely demonstrated | NO | NO |
| Round-level override | not demonstrated | NO | NO |
| AB=CD override | not demonstrated | NO | NO |
| Point-distance selector | not demonstrated | NO | NO |

## Forbidden promotion

No backtest result may be used to select among the unresolved target hypotheses. In particular, do not choose the hypothesis with the highest historical expectancy and label it source-confirmed.

## Minimum evidence for target freeze

A target selector can be frozen only when source evidence establishes both:

1. the reference/projection geometry; and
2. the rule that selects the terminal executable TP from the available references.

If source evidence never provides that selector, the correct production design is to represent terminal TP as unresolved rather than silently choosing a default.

## Gate decision

- SOURCE RESOLUTION: `PASS_PARTIAL`
- TARGET REFERENCE GEOMETRY: `PARTIALLY FROZEN`
- TERMINAL TP SELECTOR: `BLOCKED`
- FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`
- DEV: `BLOCKED`
- UNTOUCHED VALIDATION: `PROTECTED`
- ROBUSTNESS/STABILITY: `BLOCKED`
- FRESH HOLDOUT: `PROTECTED`
- PRODUCTION: `BLOCKED`
