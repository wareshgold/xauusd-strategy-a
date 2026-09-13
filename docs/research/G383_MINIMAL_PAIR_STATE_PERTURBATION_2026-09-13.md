# G383 — Minimal-Pair State Perturbation Coverage

Status: RESEARCH ONLY / NON-CANONICAL

## Objective

Extend G382 by changing one state transition at a time across six unresolved dimensions: trigger timing, pending persistence, fill timing, invalidation-before-fill, C timing, and target mapping.

## Coverage

12 controlled minimal pairs were encoded. Each pair records a baseline path, one perturbed path, the changed transition, and a deterministic classification.

### Classification summary

- 5 `OBSERVABLE_DISTINCTION`
- 7 `SOURCE_REQUIRED`
- 0 canonical promotions

## Findings

1. Some event-order changes are structurally observable: trigger/pending ordering, fill/C ordering, explicit fill presence, invalidation-before-fill, and target terminal presence.
2. Several questions remain source-defined rather than inferable from state paths: exact trigger timing, pending persistence/expiry, fill semantics, post-fill invalidation behavior, C timing, and canonical target mapping.
3. A state distinction is not evidence that either candidate is the canonical Strategy A interpretation.
4. Synthetic equality or divergence cannot replace missing authoritative geometry.

## Gate

`FROZEN-GEOMETRY-BLOCKED` remains unchanged.

G383 does not authorize DEV, historical optimization, live signals, or production.

## Next permitted research

Use the resulting coverage map to prioritize only authoritative-source acquisition for the `SOURCE_REQUIRED` dimensions, while retaining the observable distinctions as executable research constraints. Do not convert any candidate into canonical geometry without source evidence.
