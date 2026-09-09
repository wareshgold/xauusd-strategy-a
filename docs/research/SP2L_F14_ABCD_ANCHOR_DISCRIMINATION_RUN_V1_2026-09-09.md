# SP2L F14 AB=CD Anchor Discrimination Run V1 — 2026-09-09

## Scope

F14 isolates the explicit source-confirmed AB=CD relationship and tests whether candidate A/B/C/D anchor models can be represented without silently selecting one.

## Source boundary

The source explicitly teaches `AB=CD` and relates the second leg to the magnitude of the first leg. Current visual evidence does not uniquely label A/B/C/D with candle-level OHLC semantics. Therefore this fixture is a discrimination tool, not a production detector.

## Candidate anchor models

1. **WICK** — anchors use wick extremes.
2. **BODY** — anchors use candle-body edges.
3. **STRUCTURAL_PIVOT** — anchors correspond to structural swing/pivot prices.
4. **MIXED** — deliberately inconsistent anchor selection, included as a negative control.

## Synthetic result

The first three candidate models can satisfy exact `|AB| = |CD|` on the same abstract movement, while the mixed model does not. Therefore equality alone cannot identify which anchor model the source intended.

A small synthetic perturbation also breaks exact equality. No tolerance is introduced.

## Result

**PASS — AB=CD anchor ambiguity preserved.**

The fixture proves that:

- AB=CD is a measurable magnitude relationship;
- multiple plausible anchor semantics can satisfy it;
- exact equality does not reveal the canonical source anchor;
- no numerical tolerance can be inferred from the relationship alone.

## Unresolved source questions

- exact A/B/C/D points;
- wick vs body vs structural pivot semantics;
- whether anchors are candle-level or swing-level;
- whether C is related to Entry, correction endpoint, or another structural point;
- whether D is a projected target or an observed second-leg endpoint;
- exact equality tolerance, if any;
- timeframe dependence of the construction.

## Gate decision

**F14 SYNTHETIC AB=CD DISCRIMINATION: PASS**

**SOURCE RESOLUTION: PARTIAL**

**FROZEN GEOMETRY: BLOCKED**

No AB=CD production formula, anchor model, or tolerance is authorized.

## Next step

F15: construct mirrored bearish fixtures and test whether the source-confirmed structural sequence, pending-limit model, invalidation separation, trigger family, Leg-2 relationship, and AB=CD semantics remain directionally symmetric without assuming symmetry where the source has not demonstrated it.
