# SP2L Frozen Geometry Readiness Gate V1 — 2026-09-16

## Purpose

Define the deterministic research gate between source resolution and canonical validation. This artifact is an engineering control, not a trading-rule definition.

## Governing rule

Source meaning outranks backtest performance. A field may become canonical only when primary-source evidence uniquely determines its executable meaning. Candidate interpretations and unresolved geometry must remain non-canonical.

## Required geometry fields

The gate evaluates exactly these seven fields:

1. Entry
2. Structural invalidation / stop anchor
3. Limit refresh / replacement
4. Trigger taxonomy and precedence
5. 2X
6. AB=CD
7. P-Gap

## Provenance states

- `SOURCE_CONFIRMED`: primary evidence uniquely determines executable meaning.
- `CANDIDATE`: deterministic interpretation exists for research discrimination only; it is not canonical.
- `UNRESOLVED`: source evidence does not uniquely determine executable meaning.

## PASS condition

Frozen Geometry may become `READY` only if **every** required field is `SOURCE_CONFIRMED` and has source provenance sufficient to audit the decision.

Formally:

`READY := all(required_fields.provenance == SOURCE_CONFIRMED)`

No field may be silently promoted because of backtest performance, fixture behavior, visual preference, or secondary-source wording.

## BLOCK condition

Frozen Geometry remains `BLOCKED` if any required field is `CANDIDATE` or `UNRESOLVED`.

When blocked:

- canonical historical validation MUST NOT run;
- robustness/stability analysis MUST remain locked;
- fresh holdout MUST remain locked;
- production signal generation MUST remain off;
- unresolved source questions MUST remain visible in the evidence ledger.

## Current 2026-09-16 gate result

`BLOCKED`

Current F09–F14 matrix status is PARTIAL across all six fields, while P-Gap remains UNRESOLVED. Therefore no canonical geometry is frozen.

## Evidence requirements before promotion

| Field | Minimum promotion requirement |
|---|---|
| Entry | Source example uniquely identifies the executable entry anchor and its relation to Leg-2 origin. |
| Invalidation | Source uniquely identifies structural invalidation/stop OHLC semantics, including any required buffer treatment. |
| Limit refresh | Source uniquely defines when an existing pending order must be retained, moved, deleted, or replaced/re-sized. |
| Trigger | Source uniquely defines accepted trigger forms and classifier/precedence. |
| 2X | Source uniquely defines target reference, second-entry anchor, sizing/risk, and execution semantics. |
| AB=CD | Source uniquely defines A/B/C/D endpoints, measurement convention, and any tolerance. |
| P-Gap | Source uniquely defines the candle/OHLC construction and distinguishes it from E-Gap/common-gap substitutions. |

## Current evidence boundary

The project already has deterministic fixtures and a research-only geometry contract. Those artifacts are allowed to represent candidates and unresolved fields, but they cannot promote canonical geometry by themselves.

## Validation lock

The canonical fixture runner must fail closed while this gate is blocked. A blocked fixture is not a failed strategy result and must not contribute to win-rate, expectancy, drawdown, or any other performance metric.

## 125R preservation

The previously reconstructed 125R extreme trade remains untouched. This gate does not modify, clip, exclude, reclassify, or optimize that observation.

## Production boundary

This gate contains no BUY/SELL generation and no execution rule. Its sole purpose is to prevent unresolved source geometry from entering canonical validation.

## Next transition

`SOURCE RESOLUTION PARTIAL → SOURCE_CONFIRMED for all required fields → FROZEN GEOMETRY READY → UNTOUCHED VALIDATION`

Until the first transition is source-evidenced, downstream stages remain locked.
