# SP2L Batch 24 — Primary Round-Level Forensic / F16 — 2026-09-16

## Scope

Forensic review of the user-supplied primary SP2L training artifact for the unresolved Strategy A rule **#11: Round-level algorithm**. The purpose is source discrimination only. No implementation or backtest performance is used to select a canonical round-level rule.

## Primary-artifact observations

### Frames 2640–2670 (~44:00–44:30)

The teaching slide is the SP2L Strategy diagram with Entry/TP1/TP2/SL. Handwritten annotations explicitly include **"Round level"** and visible price examples around the 3200/3250/3255 area. The following frame visibly writes spacing candidates including **"250 point"**, **"500 point"**, and **"1000"**.

These observations establish that round levels / round-number spacing are taught as contextual chart information and that multiple spacing magnitudes are discussed.

### Frames 2730–2820 (~45:30–47:00)

The instructor continues annotating the same SP2L diagram, including a large **2L** annotation and structural/order markings. These frames reinforce that round-level context is discussed alongside the two-leg setup, but they do not provide a deterministic round-level selection algorithm.

## What the artifact does NOT uniquely establish

The primary artifact does not, from these inspected frames alone, uniquely specify:

- whether 250/500/1000 are exact price-point increments, pip/tick conventions, or presentation shorthand;
- the instrument-specific scale or decimal normalization;
- whether all three spacings are simultaneously valid levels;
- which spacing is selected for a given price;
- how a level is anchored or rounded;
- the acceptable distance from price to a round level;
- whether round level is a filter, score feature, entry condition, or contextual annotation;
- whether bullish and bearish selection differs;
- session/timeframe-specific behavior.

## F16 status

**SOURCE-CONFIRMED CONCEPT / MULTIPLE SPACING CANDIDATES OBSERVED / EXACT ROUND-LEVEL ALGORITHM UNRESOLVED**

The synthetic F16 fixture records the observed candidate spacing family `[250, 500, 1000]` without selecting a canonical interpretation.

## Gate consequence

No canonical round-level formula, spacing, distance threshold, or selection algorithm is frozen.

**Frozen Geometry remains BLOCKED.**

**Untouched Validation remains LOCKED.**

**Robustness/Stability remains LOCKED.**

**Fresh Holdout remains LOCKED.**

**Production remains OFF.**

**125R remains UNTOUCHED.**

No profitability-based selection was performed and no production behavior was changed.
