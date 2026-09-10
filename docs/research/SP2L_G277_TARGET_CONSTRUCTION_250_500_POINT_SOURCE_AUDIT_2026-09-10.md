# G277 — Target Construction: 250/500 Point Source Audit

Date: 2026-09-10
Source: primary SP2L video, target-construction sequence around 42:00–44:40; extracted frames g273/2560, 2580, 2600, 2620, 2640, 2660.

## Status
`SOURCE_CONFIRMED_CONCEPTS__NUMERIC_MAPPING_UNRESOLVED`

## Direct visual evidence
The source schematic explicitly labels `Entry`, `TP1`, `TP2`, and `SL` on one construction. The same sequence contains handwritten references to `Round level` and numeric examples including `250 point` and `500 point`.

The frame sequence therefore confirms that:
- TP1 and TP2 are source concepts;
- Round Level is a source concept in this construction discussion;
- Point Distance is a source concept;
- 250 point and 500 point are source-provided numerical examples.

## What the evidence does NOT establish
The frames do not uniquely establish any of the following executable mappings:
- `TP1 = Entry + 250 points`;
- `TP2 = Entry + 500 points`;
- `TP1/TP2` selected from round levels;
- 250/500 as absolute XAUUSD price units versus platform-specific point units;
- whether the numbers are examples, distances, or mandatory target selectors;
- whether the same construction is mirrored for SELL;
- rounding, tick-size, spread, or execution semantics.

The handwritten values around `2500`, `3200`, `3255/3250` are retained as source evidence only. They must not be converted into a target formula without an explicit source bridge.

## Research boundary
This audit may generate synthetic hypotheses for later rejection/testing, but no 250/500-point formula enters canonical Strategy A or production.

## Decision
Keep target geometry unresolved. Continue source resolution by finding a worked example where the source explicitly connects a named price level to TP1/TP2 or states how point distance/round level determines the target.