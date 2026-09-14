# G403 — Pending-Limit Entry Execution Source Resolution

## Purpose
G403 is the next source-resolution gate after G401 P-Gap and G402 AB=CD anchor research. It addresses the remaining G400 blocker covering executable pending-limit entry semantics.

## Source-first boundary
The source confirms a pending-limit entry during the correction, but the executable details remain unresolved. G403 therefore does **not** freeze:

- the pending-limit price;
- whether that price equals geometric C;
- the activation/trigger event;
- touch versus close semantics;
- order persistence/cancellation;
- fill semantics under an intrabar overshoot;
- structural invalidation before the pending order fills.

No production entry formula is introduced.

## Research hypotheses
Four interpretations remain explicitly non-canonical:

1. A source-defined correction/reference price.
2. Geometric C as the executable limit price.
3. A source-defined level distinct from geometric C.
4. A source-defined temporal/persistence condition governing activation or fill.

These are research labels, not Strategy A rules.

## Minimal-pair discrimination
Five targeted pairs isolate:

- limit price versus geometric C;
- touch versus close-through activation;
- order persistence across invalidation;
- pre-fill versus post-fill structural invalidation;
- price overshoot through the pending level.

The fixtures are designed to identify what authoritative source wording or source visuals actually distinguish. They do not select a winner from backtest performance.

## Evidence required to resolve G403
A status change requires traceable authoritative source material, source visual evidence, or a source-derived artifact whose provenance can be audited. Common trading conventions, implementation convenience, and profitable historical hypotheses are insufficient.

## Gate status
**UNRESOLVED / RESEARCH-ONLY**

G403 does not clear G400, does not authorize executable geometry, and does not authorize optimization or production deployment.
