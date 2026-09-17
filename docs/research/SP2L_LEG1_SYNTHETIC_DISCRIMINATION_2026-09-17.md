# SP2L Leg 1 Synthetic Discrimination — 2026-09-17

## Status

`RESEARCH_ONLY / NON-CANONICAL`

This pass tests whether source-compatible Leg-1 A/B hypotheses can be discriminated by deterministic synthetic fixtures. It does **not** select a canonical geometry and does not authorize execution.

## Source boundary

The Tier-1 evidence confirms that SP2L uses a parent first leg and a second leg of approximately equal magnitude, and that the parent Leg 1 is visually distinct from the pending-limit execution marker. Exact A/B candle anchors, wick/body semantics, and an executable formula remain unresolved.

The manual-adjudication contract requires source meaning to discriminate the executable dimension before `SOURCE_DISCRIMINATED` can be recorded. Synthetic fixtures may eliminate internally inconsistent hypotheses, but they may not manufacture missing source semantics.

## Hypothesis set under test

The following are retained only as **source-compatible candidates**, not as proposed rules:

| ID | Candidate A/B interpretation | Status before fixtures |
|---|---|---|
| H1 | structural origin → spike extreme | viable |
| H2 | spike origin → spike extreme | viable |
| H3 | candle open → spike extreme | viable but source-weak |
| H4 | structural point → structural point | viable only when the source-visible structural points coincide with the parent-leg description |

No hypothesis is assigned a preference.

## Fixture design

Fixtures are semantic discriminators, not profitability tests. Each fixture contains a deliberately constructed price path where competing interpretations produce different Leg-1 measurements.

### Fixture F1 — distinct structural origin vs spike origin

- Structural origin: 100
- Spike origin: 102
- Spike extreme: 112
- Candidate magnitudes:
  - H1 = 12
  - H2 = 10
- Observation: the fixture proves the candidates are mechanically distinguishable.
- Source implication: **none**. The source must identify which point is the parent-leg origin before either value can be canonical.

### Fixture F2 — candle open differs from structural origin

- Structural origin: 100
- Relevant candle open: 101
- Spike extreme: 110
- Candidate magnitudes:
  - H1 = 10
  - H3 = 9
- Observation: open-based and structural-origin measurements are distinguishable.
- Source implication: no source statement found in the registered evidence uniquely promotes the candle-open interpretation.

### Fixture F3 — structural point differs from spike extreme anchor

- Structural point: 100
- Spike extreme: 110
- Later wick extension: 112
- Candidate measurements differ depending on whether the source intends the first visible extreme or later wick extreme.
- Observation: wick/body/extreme selection is independently material.
- Source implication: exact price-field semantics remain unresolved.

### Fixture F4 — nested SP2L structure

- Inner structural movement occurs inside a larger parent movement.
- The same local candle sequence can support both an inner and parent structural interpretation.
- Observation: a generic swing/fractal rule cannot be promoted merely because it produces a deterministic result.
- Source implication: scenario-specific parent/child identification remains required.

## Discrimination result

### What the fixtures establish

1. A/B candidate geometries are genuinely distinguishable on controlled data.
2. Candle-open, spike-origin, structural-origin, and structural-point interpretations cannot be treated as mathematically equivalent.
3. Wick/body and nested-structure choices can materially change the measured Leg 1.
4. Therefore, implementation can remain deterministic **only after** the source supplies the missing semantic discriminator.

### What the fixtures do NOT establish

- They do not prove H1, H2, H3, or H4 is the intended source rule.
- They do not establish an A or B candle index.
- They do not establish wick versus body semantics.
- They do not establish a universal swing/fractal algorithm.
- They do not establish a P-Gap formula.
- They do not establish the Leg-2 projection origin.
- They do not justify historical backtest selection.

## Gate decision

`LEG1_SYNTHETIC_DISCRIMINATION = PASS`

Meaning: the fixture harness successfully demonstrates that the unresolved hypotheses are mechanically distinguishable and that deterministic tests can detect accidental substitutions.

`LEG1_SOURCE_DISCRIMINATED = NO`

Reason: synthetic data cannot supply missing source semantics. The evidence remains insufficient to select a canonical A/B endpoint interpretation.

`FROZEN_GEOMETRY = BLOCKED`

`DEV = LOCKED`

`UNTUCHED_VALIDATION = LOCKED`

`ROBUSTNESS/STABILITY = LOCKED`

`FRESH_HOLDOUT = LOCKED`

`PRODUCTION = OFF`

## Next source-resolution target

Do not implement a Leg-1 calculator from these hypotheses. Move to the next independent Tier-1 source discriminator, with priority on the **Leg-2 projection origin / AB=CD relationship** in the 00:36:30–00:37:00 and 01:02:41–01:04:32 source examples.

If new visual evidence uniquely identifies A/B, return to this matrix and perform a human adjudication before any geometry freeze.
