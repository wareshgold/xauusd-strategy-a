# G335 — Risk/Reward and TP1/TP2 Source Audit

Date: 2026-09-12
Parent gate: G334
Source asset: full SP2L lesson video + transcript
Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Objective

Determine what the source means by `R1`, `R2`, `TP1`, `TP2`, and the spoken `2X/3X` references, and whether these terms establish an executable geometric target formula.

This gate is source-only. No historical performance, optimization, or backtest result is used.

## Source evidence

### 1. Target / reward discussion around 41:26–42:37

The presenter introduces TP1 and TP2 while discussing target selection and reward. The transcript includes references to `2X/3X` and to `R1/R2`, including the explanation that a first reward level corresponds to TP1 and a second reward level corresponds to TP2 when the trader wants the larger reward outcome.

The source therefore establishes that:

- `R1` and `R2` are reward-oriented outcomes;
- TP1 and TP2 are target/position-management levels associated with those outcomes;
- the trader may choose the larger reward outcome rather than treating TP1 as the only possible exit.

However, this passage does **not** uniquely specify a universal price formula such as:

`TP1 = Entry + 1R`
`TP2 = Entry + 2R`

nor does it establish a fixed `2R` target.

The spoken `2X/3X` references are likewise not sufficient to freeze a universal numeric multiple because the surrounding explanation concerns target/reward selection and does not provide a complete deterministic mapping from entry, structural stop, and AB=CD geometry to those labels.

### 2. Worked example around 01:04:19–01:04:32

The presenter places a pending order after the lower-high sequence and moves the order downward until activation. He then describes the parent Leg 1 from an earlier deep-leg origin to its later endpoint.

At approximately 01:04:32 he identifies the position TP at the lower level for `R1` and states that `R2` is also possible.

This is important because the measured parent Leg 1 is already described separately from the pending-limit execution marker. Therefore the R1/R2 labels cannot be used as evidence that the geometric Leg 1 is measured from the eventual fill price.

The combined G333/G334 evidence already established:

`pending_limit_entry != automatically geometric C`

and:

`parent Leg 1 geometry != pending-limit marker`

G335 does not weaken those distinctions.

### 3. Relationship to AB=CD

The source separately and explicitly teaches `AB=CD` and that Leg 2 should match Leg 1 in magnitude. This is the strongest source-confirmed geometric target relationship currently available.

The R1/R2 discussion does not replace that relationship with a fixed numeric target-distance rule.

Therefore the current source hierarchy is:

1. `AB=CD` / `|Leg2| = |Leg1|` — source-confirmed geometric concept.
2. `R1/R2` — source-confirmed reward/target outcomes.
3. Exact conversion from the geometric setup to TP1/TP2 price levels — unresolved.

## Candidate interpretations

### Candidate RR-1 — fixed 1R / 2R mapping

Interpretation:

`TP1 = 1R`
`TP2 = 2R`

Status: **NOT SOURCE-CONFIRMED**.

Reason: the source uses R1/R2 as reward outcomes but does not provide a sufficiently explicit universal equation tying the displayed targets to structural risk for all setups. Freezing this mapping would be an implementation assumption.

### Candidate RR-2 — selectable reward multiples such as 2X/3X

Interpretation: the trader may select a target according to a desired reward multiple.

Status: **SOURCE-SUPPORTED AS TARGET-SELECTION LANGUAGE, NOT AN EXECUTABLE CANONICAL FORMULA**.

Reason: the spoken 2X/3X terminology demonstrates reward selection, but does not define all required inputs, anchors, or precedence relative to AB=CD.

### Candidate RR-3 — R1/R2 are labels for geometrically derived target outcomes

Interpretation: the target(s) are derived from the source's leg geometry, while R1/R2 describe the resulting reward outcomes.

Status: **PLAUSIBLE / SOURCE-COMPATIBLE, BUT NOT YET UNIQUELY PROVEN**.

Reason: the worked example places R1/R2 after the parent Leg 1 is identified, and the source independently teaches AB=CD. But the exact relationship between the geometric endpoint, risk distance, and the R labels is not explicitly enumerated.

## What G335 establishes

The following statements are now source-safe:

- `R1` and `R2` are not arbitrary implementation names; they are source language for reward/target outcomes.
- TP1 and TP2 are associated with those reward outcomes.
- `2X/3X` is source language about reward/target selection, not evidence for fixed price distances.
- No canonical `TP = 2R` rule may be frozen from this evidence.
- No canonical `Entry → TP1 = 250` or `Entry → TP2 = 500` rule may be frozen; G332 already rejected the 250/500/1000 annotation as a target-distance bridge.
- The source-confirmed geometric target concept remains `AB=CD` / Leg 2 approximately equal to Leg 1.
- Exact executable TP1/TP2 construction remains unresolved.

## What G335 does NOT establish

G335 does not establish:

- a fixed R1 multiple;
- a fixed R2 multiple;
- a universal 1R/2R ladder;
- a universal 2R target;
- a fixed numeric TP1/TP2 distance;
- that TP1 is always the AB=CD endpoint;
- that TP2 is always a second AB=CD projection;
- that R1/R2 are independent of geometric target construction;
- any new P-Gap geometry;
- any wick/body convention;
- any A/B/C/D anchor convention.

## Deterministic-rule impact

The implementation must therefore keep target construction explicitly unresolved rather than substituting a convenient risk-multiple formula.

Prohibited at the current gate:

```text
TP1 = entry ± 1R
TP2 = entry ± 2R
TP = entry ± 2R
TP1 = entry ± 250
TP2 = entry ± 500
```

unless a later authoritative source bridge establishes the corresponding rule.

The production specification must also preserve the distinction between:

`geometric target`

and

`reward label / position-management outcome`

until the source uniquely resolves their relationship.

## Updated source ledger

| Concept | Status after G335 |
|---|---|
| R1/R2 reward terminology | SOURCE-CONFIRMED |
| TP1/TP2 target terminology | SOURCE-CONFIRMED |
| 2X/3X reward-selection language | SOURCE-SUPPORTED |
| Fixed 1R/2R formula | UNSUPPORTED |
| Fixed 2R target | UNSUPPORTED |
| 250/500/1000 as TP constants | REJECTED / UNSUPPORTED |
| AB=CD concept | SOURCE-CONFIRMED |
| Leg2 ≈ Leg1 | SOURCE-CONFIRMED |
| Exact TP1 construction | UNRESOLVED |
| Exact TP2 construction | UNRESOLVED |
| Exact A/B/C/D anchors | UNRESOLVED |
| Wick/body semantics | UNRESOLVED |
| P-Gap executable geometry | UNRESOLVED |
| FROZEN_GEOMETRY | BLOCKED |
| DEV | BLOCKED |
| VALIDATION | PROTECTED |
| FRESH_HOLDOUT | NOT AUTHORIZED |
| PRODUCTION | BLOCKED |

## Gate result

`G335 = PASS (R1/R2 semantics classified; executable target construction remains unresolved)`

`R1/R2 = SOURCE-CONFIRMED REWARD/TARGET OUTCOMES`
`2X/3X = SOURCE-SUPPORTED REWARD-SELECTION LANGUAGE`
`FIXED_R_MULTIPLE = NOT SOURCE-CONFIRMED`
`TP1_EXECUTABLE_FORMULA = UNRESOLVED`
`TP2_EXECUTABLE_FORMULA = UNRESOLVED`
`FROZEN_GEOMETRY = BLOCKED`
`DEV = BLOCKED`
`VALIDATION = PROTECTED`
`FRESH_HOLDOUT = NOT AUTHORIZED`
`PRODUCTION = BLOCKED`

## Next source-resolution target

G336 should return to the highest-value unresolved geometry: exact A/B/C/D anchor semantics in the worked source example, using the source frames and transcript together. The key question is whether the presenter gives an unambiguous price/candle reference for the Leg 1 endpoints and the correction origin that can be translated into deterministic anchors without inventing wick/body rules.
