# SP2L Evidence Gap Closure Plan V1 — 2026-09-16

## Objective

Define the exact primary-source evidence package required to move each of the seven Frozen Geometry blockers from current partial/structural coverage toward `SOURCE_CONFIRMED`.

This plan does not define missing geometry. It defines only the evidence required to resolve it.

## Evidence packages

| ID | Field | Minimum acceptable primary package | Required audit outcome | If incomplete |
|---|---|---|---|---|
| EG-01 | `entry` | One or more primary worked examples showing the correction structure, exact Limit/entry level, and the structural event that defines that level. | Unique executable entry anchor and scope are established. | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| EG-02 | `invalidation` | Primary worked example exposing the invalidation/stop level at price resolution, including wick/body semantics and any explicit buffer. | Unique invalidation anchor and buffer semantics. | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| EG-03 | `limitRefresh` | Primary example showing an order before/after a later candle and explicitly demonstrating the condition for retain/move/delete/re-place. | Deterministic refresh condition and action. | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| EG-04 | `trigger` | Primary examples covering the stated trigger variants with explicit acceptance logic or source wording that resolves classification/precedence. | Deterministic trigger classifier and acceptance semantics. | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| EG-05 | `twoX` | Primary worked 2X example exposing second-entry anchor, target-distance reference, sizing, stop, and fill/order semantics. | Unique 2X executable semantics. | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| EG-06 | `abcd` | Primary worked AB=CD example with A/B/C/D endpoints, measurement convention, and explicit tolerance/non-equality treatment if applicable. | Unique AB=CD anchors and acceptance rule. | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| EG-07 | `pGap` | Primary frame/transcript evidence exposing the P-Gap candle relationship, OHLC/index semantics, location, and P-Gap vs E-Gap boundary. | One deterministic P-Gap classification survives competing formulas. | `REMAINS_UNRESOLVED` |

## Evidence package acceptance

Each package must enter through the Evidence Intake Template and Register.

The package is accepted for promotion review only if:

1. Primary provenance is immutable/auditable.
2. Timestamp/frame or exact transcript location is recorded.
3. Raw observation is separated from interpretation.
4. Competing interpretations are explicitly listed.
5. The evidence discriminates the alternatives without relying on performance.
6. Universal-vs-example-specific scope is resolved.
7. Exact executable semantics are exposed where required.
8. No formula, tolerance, threshold, buffer, precedence, sizing, or fill behavior is invented.

## Stop conditions

Immediately stop promotion review if:

- the evidence is secondary;
- the frame is ambiguous between multiple geometries;
- the example only demonstrates a special case but universal scope is claimed;
- the missing detail can only be selected by backtest performance;
- the evidence requires an unstated execution assumption.

## Promotion sequence

`SOURCE MATERIAL → INTAKE → RAW OBSERVATION → COMPETING INTERPRETATIONS → DISCRIMINATION → SCOPE CHECK → EXECUTABLE SEMANTICS CHECK → PROMOTION DECISION`

No field skips a stage.

## Current state

All seven packages are open. No package currently satisfies the complete promotion standard.

`SOURCE_CONFIRMED = 0/7`.

## Gate consequence

Frozen Geometry remains `BLOCKED` until all seven fields independently reach `SOURCE_CONFIRMED`.

## Integrity boundaries

- This plan does not modify geometry.
- It does not authorize validation execution.
- It does not generate BUY/SELL decisions.
- It does not use backtest performance to resolve source meaning.
- The 125R observation remains untouched, unmodified, unclipped, and unreclassified.
