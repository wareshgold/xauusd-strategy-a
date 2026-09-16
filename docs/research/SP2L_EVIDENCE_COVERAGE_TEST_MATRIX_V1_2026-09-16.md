# SP2L Evidence Coverage Test Matrix V1 — 2026-09-16

## Purpose

Define deterministic questions that any future primary evidence must answer before a Frozen Geometry field can be promoted.

| Field | Required discrimination test | Pass condition | Failure consequence |
|---|---|---|---|
| `entry` | Does the evidence uniquely identify the entry anchor and its defining structural event? | One executable interpretation survives, including scope across setup variants. | Remains `PARTIAL`. |
| `invalidation` | Does the evidence uniquely identify the invalidation price semantics? | Exact anchor plus any buffer/offset is source-explicit. | Remains `PARTIAL`. |
| `limitRefresh` | Does the evidence uniquely determine when an order must be refreshed/replaced/retained? | Condition and resulting action are deterministic. | Remains `PARTIAL`. |
| `trigger` | Does the evidence uniquely classify trigger form and acceptance/precedence? | Every covered trigger case has deterministic classification. | Remains `PARTIAL`. |
| `twoX` | Does the evidence uniquely determine the 2X anchor and execution semantics? | Anchor, reference distance, sizing/stop/fill semantics are explicit. | Remains `PARTIAL`. |
| `abcd` | Does the evidence uniquely identify A/B/C/D and equality tolerance? | Anchors, measurement, and tolerance are explicit. | Remains `PARTIAL`. |
| `pGap` | Does the evidence uniquely determine P-Gap OHLC/index/location semantics? | One deterministic formula/classification survives all discriminators. | Remains `UNRESOLVED`. |

## Cross-field tests

A promotion candidate must also pass:

1. **Primary-source test** — evidence originates in auditable primary material.
2. **Scope test** — evidence is not merely a special-case example unless the source explicitly states universal scope.
3. **Discrimination test** — competing interpretations are ruled out by source evidence, not by performance.
4. **Execution-semantics test** — price/structure semantics required by the canonical contract are actually exposed.
5. **No-invention test** — no tolerance, buffer, threshold, fill, formula, or precedence is added by the implementation.

## Stop condition

If any cross-field test fails, the field cannot be promoted to `SOURCE_CONFIRMED`.

## Gate consequence

The seven-field Frozen Geometry gate remains `BLOCKED` until every required field passes its field-specific and cross-field tests.
