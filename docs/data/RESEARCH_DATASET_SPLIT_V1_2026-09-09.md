# Research Dataset Split v1 — 2026-09-09

## Purpose

Freeze the temporal research split policy before Strategy A backtesting or parameter optimization. This document defines dataset roles; it does not claim that the underlying full historical dataset has yet been acquired.

## Principles

- Raw provider data is immutable research input and is never modified in place.
- Strategy interpretation, parameter selection, and source resolution must not use the Fresh Holdout.
- The split is chronological; no random shuffling is permitted.
- Any transformation derived from future candles must remain within the same temporal boundary as the observation.
- Development results may influence implementation refinement only before the validation gate is declared frozen.
- Validation is used for confirmation, not repeated tuning.
- Fresh Holdout remains untouched until the strategy specification, geometry, implementation, fixture suite, and DEV/VAL results are frozen and approved.
- Dataset versions are identified by provider, symbol, interval, timezone, acquisition manifest, and SHA-256 provenance.

## Current dataset status

The validated acquisition artifacts currently cover a limited 2026 window. Coverage sampling also confirms returned M1 data in sampled windows beginning in 2020, but this is not evidence of continuous 2020-present coverage.

Therefore this policy is **structural and pre-registration only**. It does not designate any incomplete window as the final DEV/VAL/HOLDOUT dataset.

## Required temporal roles

Once the full research dataset is acquired and audited, it must be assigned three contiguous chronological roles:

1. **DEV** — source-aligned implementation development, synthetic-to-historical verification, debugging, and limited parameter work after the rule itself is source-confirmed.
2. **VALIDATION** — one-time confirmation of the frozen candidate specification. No threshold fishing or repeated retuning against this period.
3. **FRESH HOLDOUT** — completely untouched until the previous gates are passed. Used once for final out-of-sample confirmation.

## Boundary policy

- Boundaries are timestamp-defined in UTC.
- A candle belongs to exactly one split.
- The split definition must be recorded before any strategy performance is computed on the full dataset.
- If a setup begins in one split and requires future candles from another split, the setup is evaluated only according to the information legitimately available at the split boundary; it must not leak future observations backward.
- Derived M5 bars must be generated from the raw M1 source using deterministic aggregation, with provenance linking the derived dataset to the exact raw dataset version.

## Proposed planning convention

Until full coverage and feed audit are complete, use the following planning convention only:

- DEV: earliest ~60% of the usable continuous research period
- VALIDATION: next ~20%
- FRESH HOLDOUT: latest ~20%

These percentages are planning defaults, **not yet frozen calendar dates**. Calendar boundaries will be frozen only after the actual acquired coverage is known.

## Promotion rule

No Strategy A implementation may be promoted to production from historical profitability alone. Promotion requires, in order:

SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.

## Explicit non-decisions

This document does not define:

- P-Gap formula;
- A/B/C/D anchors;
- AB=CD tolerance;
- entry price formula;
- stop/target formula beyond source-confirmed concepts;
- session filter;
- trigger taxonomy;
- broker execution semantics.

Those remain source-resolution questions.
