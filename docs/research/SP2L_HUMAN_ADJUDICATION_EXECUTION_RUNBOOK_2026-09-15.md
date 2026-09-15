# SP2L Human Adjudication Execution Runbook — 2026-09-15

## Purpose

Operational checklist for Issue #175. This runbook records human decisions; it does not make source decisions autonomously.

## Review order

1. C01 — P-Gap semantic discriminator
2. C02 — corrective Buy Limit / SL visual separation
3. C08 — correction / invalidation relationship
4. C03 — AB=CD / Leg-2 magnitude semantics
5. C04 — TP1 / TP2 / 2X semantics
6. C05 — bearish continuation example
7. C06 — pending-order deletion/update behavior
8. C07 — trigger family

## Mandatory questions for every candidate

- Does the cited Tier-1/Tier-2 source itself contain a discriminator?
- Is the discriminator precise enough to reproduce independently?
- Does it uniquely eliminate competing hypotheses?
- Does applying it require an invented formula, threshold, buffer, candle index, fill rule, execution rule, or symmetry assumption?
- What hypotheses remain unresolved after the review?

## Allowed outcomes

### SOURCE_DISCRIMINATED

Use only when the source materially and reproducibly determines the dimension and no invention is required.

### REMAINS_BLOCKED

Use when evidence is insufficient, ambiguous, non-unique, or would require invention. Preserve the remaining hypotheses explicitly.

## No partial freeze

A successful adjudication of one dimension does not authorize that dimension for production or freeze it independently. The ten-dimension readiness gate remains blocked until all executable dimensions have valid human source-discriminated records.

## Evidence discipline

Do not use backtest performance, optimization, generic technical-analysis conventions, inferred symmetry, or implementation convenience to adjudicate source meaning.

## After adjudication

Submit valid records to the post-adjudication readiness gate (#179). Only `READY_FOR_FREEZE_REVIEW` permits the separate canonical freeze decision gate (#180). A readiness result is not itself a freeze or execution authorization.
