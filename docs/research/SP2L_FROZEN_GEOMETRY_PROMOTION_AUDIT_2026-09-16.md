# SP2L Frozen Geometry Promotion Audit — 2026-09-16

## Purpose

Record the deterministic promotion audit after the SP2L validation harness became typecheck-clean and 8/8 tests passed locally.

This is an evidence-control artifact. It does not define trading geometry and does not promote any candidate interpretation to canonical status.

## Harness prerequisite

- `tsconfig.sp2l-harness.json` typecheck: PASS on the local verification performed for this session.
- SP2L harness tests: 3 files, 8 tests, 8 passed.
- Full repository `npm run build` remains outside this gate and is not used as evidence for source geometry.

## Promotion rule

A required geometry field may be promoted only when primary-source evidence uniquely determines its executable meaning. Fixture behavior, backtest performance, conventional technical-analysis definitions, or visual preference cannot substitute for missing source evidence.

The frozen gate requires all seven fields to be `SOURCE_CONFIRMED` before validation can unlock.

## Field-by-field audit

| Field | Current evidence state | Canonical status | Blocking question | Promotion evidence required |
|---|---|---|---|---|
| Entry | PARTIAL | BLOCKED | Exact executable entry anchor and its relation to Leg-2 origin are not uniquely fixed across setups. | Worked primary-source example exposing entry level and Leg-2 origin together. |
| Invalidation / SL | PARTIAL | BLOCKED | Exact OHLC/wick/body anchor and any buffer/spread treatment are not uniquely fixed. | Worked primary-source stop/invalidation example with price-level semantics. |
| Limit refresh | PARTIAL | BLOCKED | Source describes delete/re-place/new sizing behavior, but no deterministic mandatory replacement condition is fixed. | Explicit threshold or deterministic structural transition, or repeated non-contradictory worked examples. |
| Trigger | PARTIAL | BLOCKED | One-, two-, three-candle and Bar/Key-Bar variants are described, but acceptance/classification/precedence is unresolved. | Primary-source setup uniquely mapping observable structure to accepted trigger and precedence. |
| 2X | PARTIAL | BLOCKED | Optional second position and larger-R concept are supported, but anchor, sizing/risk and fill semantics are unresolved. | Worked 2X source example exposing target reference, entry anchor, stop/risk, sizing and fill semantics. |
| AB=CD | PARTIAL | BLOCKED | Leg-2≈Leg-1 concept is supported, but A/B/C/D endpoints, measurement convention and tolerance are unresolved. | Worked source example exposing all four endpoints and measurement convention. |
| P-Gap | UNRESOLVED | BLOCKED | Exact candle/OHLC construction remains unspecified; P-Gap cannot be substituted with a generic gap formula. | Primary-source candle/OHLC evidence that uniquely defines P-Gap and distinguishes it from E-Gap/common gap. |

## Current gate decision

`BLOCKED`

No field is promoted by this audit. The current evidence boundary remains consistent with the source-resolution matrix and frozen-geometry gate.

## Explicit non-promotions

The following remain non-canonical:

- any invented P-Gap equation;
- conventional AB=CD A/B/C/D anchors or tolerance;
- any universal 2X formula;
- any universal trigger classifier or precedence rule;
- any numeric Limit-refresh threshold inferred from discretionary wording;
- any exact stop-loss buffer or OHLC anchor not uniquely stated by the source;
- any execution/fill semantics inferred from backtest outcomes.

## Downstream lock

Because the gate remains blocked:

- canonical historical validation stays locked;
- performance metrics must not use blocked/candidate observations as denominators;
- robustness/stability stays locked;
- fresh holdout stays locked;
- production BUY/SELL generation stays off;
- the 125R observation remains untouched.

## Next actionable evidence work

The next productive work is not additional backtesting. It is targeted primary-source evidence acquisition only if genuinely new primary media/transcript/frame evidence becomes available. Broad source hunting remains closed.

Until such evidence appears, engineering work should remain focused on deterministic harness integrity, provenance preservation, fixture coverage, and auditability without defining missing geometry.
