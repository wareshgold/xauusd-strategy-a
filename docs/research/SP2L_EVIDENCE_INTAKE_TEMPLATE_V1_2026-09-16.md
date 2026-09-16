# SP2L Deterministic Evidence Intake Template V1 — 2026-09-16

## Purpose

Provide one fixed audit format for introducing new primary-source evidence against a Frozen Geometry blocker. This template records evidence without silently converting interpretation into canonical geometry.

## Intake identity

- Evidence ID: `E-YYYYMMDD-NNN`
- Field: `entry | invalidation | limitRefresh | trigger | twoX | abcd | pGap`
- Source artifact:
- Source type: `primary_media | primary_transcript | primary_frame | worked_example`
- Source timestamp / frame:
- Artifact hash / immutable reference:
- Analyst:
- Date:

## Evidence payload

### Exact source observation

Record only what is directly observable or explicitly stated. Do not paraphrase an inferred formula as source fact.

### Structural meaning supported

State the narrowest meaning directly supported by the evidence.

### Executable detail exposed

List any price/structure/order semantics actually determined by the evidence.

## Competing interpretations

| Interpretation | Evidence support | What remains unresolved |
|---|---|---|
| A | | |
| B | | |
| C | | |

If only one interpretation survives, explain exactly why the source discriminates it from the alternatives.

## Discrimination test

- Does the evidence uniquely determine the relevant field?
- Does it apply universally or only to the demonstrated setup variant?
- Does it expose price-level semantics or only conceptual structure?
- Does it establish any tolerance/buffer/threshold?
- Does it establish execution/fill semantics?

## Promotion decision

Allowed values:

- `REMAINS_UNRESOLVED`
- `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED`
- `SOURCE_CONFIRMED`

### Decision

`REMAINS_UNRESOLVED`

### Rationale

Explain why the evidence does or does not uniquely determine executable meaning.

## Forbidden promotion basis

The following must never be used to promote a field:

- Backtest performance
- Optimization
- Curve fitting
- Matching a known trade outcome
- Majority vote among interpretations
- Secondary summaries
- Search snippets
- Unverified visual estimates

## Canonical safety check

Before promotion to `SOURCE_CONFIRMED`:

- [ ] Primary-source provenance verified
- [ ] Source timestamp/frame recorded
- [ ] Competing interpretations explicitly checked
- [ ] Universal-vs-variant scope resolved
- [ ] Exact executable semantics uniquely determined
- [ ] No invented formula/tolerance/buffer/threshold/fill semantics
- [ ] Geometry contract unchanged unless promotion is independently justified

## Gate consequence

A field not promoted to `SOURCE_CONFIRMED` keeps Frozen Geometry `BLOCKED`.

This intake record does not authorize BUY/SELL generation or downstream validation execution.
