# SP2L Evidence Gap Closure Acceptance V1 — 2026-09-16

## Purpose

Turn the Evidence Gap Closure Plan into deterministic acceptance criteria so that new primary evidence can be evaluated without discretionary rule invention.

## Field acceptance gates

### EG-01 Entry

PASS only if a primary source uniquely identifies the entry price anchor and the structural event that defines it, and the source scope is known.

FAIL if the anchor is inferred from chart appearance, outcome matching, or one variant is silently generalized.

### EG-02 Invalidation

PASS only if the primary source uniquely identifies the invalidation/stop anchor and any explicit buffer semantics.

FAIL if wick/body choice, spread, or buffer is inferred.

### EG-03 Limit Refresh

PASS only if primary evidence uniquely determines the condition under which an existing order is retained, moved, deleted, or replaced.

FAIL if a numeric threshold must be invented.

### EG-04 Trigger

PASS only if primary evidence deterministically maps each covered trigger form to acceptance semantics and any precedence.

FAIL if multiple trigger interpretations remain compatible with the source.

### EG-05 2X

PASS only if primary evidence uniquely determines the second-entry anchor and all execution semantics required by the contract.

FAIL if the half-target concept must be converted into an unstated equation, tolerance, or fill assumption.

### EG-06 AB=CD

PASS only if primary evidence uniquely determines A/B/C/D, measurement convention, and any equality tolerance.

FAIL if endpoints or tolerance are selected from implementation convenience or backtest fit.

### EG-07 P-Gap

PASS only if primary evidence uniquely determines P-Gap OHLC/index/location semantics and the boundary versus E-Gap.

FAIL if more than one formula remains compatible with the evidence.

## Cross-package acceptance

A package may be marked `SOURCE_CONFIRMED` only if all of these are true:

- primary provenance verified;
- source location recorded;
- raw observation preserved;
- alternatives explicitly tested;
- scope resolved;
- executable semantics uniquely determined;
- no invented formula/tolerance/buffer/threshold/fill/precedence;
- no dependency on backtest outcome.

## Promotion rule

A passing package is a candidate for source promotion review. Promotion must still be reflected in the canonical source-resolution status and frozen-geometry gate; this acceptance document itself does not promote a field.

## Global gate

Even one failing field keeps Frozen Geometry `BLOCKED`.
