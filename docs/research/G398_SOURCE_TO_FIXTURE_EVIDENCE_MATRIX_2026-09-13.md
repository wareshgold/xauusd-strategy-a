# G398 — Source-to-Fixture Evidence Matrix

Date: 2026-09-13  
Gate: SOURCE RESOLUTION / FROZEN GEOMETRY  
Status: **SEMANTIC CORE FROZEN / EXECUTABLE GEOMETRY BLOCKED**

## Purpose

Map the existing authoritative source findings to the synthetic/research fixtures without allowing a fixture to manufacture a canonical rule.

G384 closed the current primary-source search loop. G398 therefore does **not** seek new source evidence and does not select a profitable interpretation. It establishes the evidence boundary for the existing G395/G397 research hypotheses.

## Source-to-fixture matrix

| Component | Source evidence | Fixture dimension exercised | Evidence status | Canonical executable rule |
|---|---|---|---|---|
| P-Gap | Source explicitly shows `Valid BO = P-Gap`; exact OHLC geometry unresolved | PG-H01/H02/H04 minimal-pair separation | SOURCE-CONFIRMED CONCEPT / GEOMETRY UNRESOLVED | NO |
| AB=CD | Source explicitly shows `AB=CD` and teaches Leg 2 matching Leg 1 magnitude | ABCD-H01/H02/H03 measurement separation | SOURCE-CONFIRMED CONCEPT / ANCHORS UNRESOLVED | NO |
| Pending-limit entry | Source explicitly describes a pending order during correction and movement until activation | EN-H01/H02/H03; entry-vs-C separation | SOURCE-CONFIRMED MECHANISM / EXACT PRICE SEMANTICS UNRESOLVED | NO |
| Structural invalidation | Source supports invalidation/stop concept before or around activation | SL-H01/H02 | SOURCE-SUPPORTED CONCEPT / EXACT BOUNDARY UNRESOLVED | NO |
| TP1/TP2 | Source labels TP1/TP2 and R1/R2 outcomes; numeric mapping remains unresolved | TP-H01/TP-H04 counterfactual target dimensions | SOURCE-CONFIRMED TERMINOLOGY / EXECUTABLE MAPPING UNRESOLVED | NO |

## Fixture interpretation rule

A fixture is evidence that two interpretations are computationally distinguishable. It is **not** evidence that either interpretation is the source meaning.

Therefore:

- a fixture may reject equivalence between two candidate formulas;
- a fixture may demonstrate that a candidate requires different source semantics;
- a fixture may not promote a candidate to canonical status;
- historical profitability may not be used to resolve the source tie.

## Explicit source boundaries

### P-Gap

The source establishes the concept/name association but does not provide executable A/B/C candle fields or a unique P-Gap formula. G397 may therefore distinguish candidate formulas but must leave all PG-H01..PG-H04 noncanonical.

### AB=CD

The source establishes the relationship and approximate equality of Leg 1 and Leg 2. G336 additionally records that exact A/B/C anchors, wick/body semantics, equality tolerance, and executable D construction remain unresolved. The fixture layer therefore tests measurement distinctions only.

### Entry / C

G333/G334 establish that the pending-limit marker is a separate execution object and that `fill_price = C` is not a source-safe shortcut. G397 may encode this distinction but may not choose a different C formula.

### TP

G335 establishes R1/R2 and TP1/TP2 as source terminology/outcomes, while rejecting fixed 1R/2R, 2R, or 250/500/1000 executable mappings. G397 therefore remains counterfactual only.

## Canonical promotion gate

A hypothesis may leave `UNRESOLVED` only if a later authoritative source bridge explicitly resolves the corresponding executable geometry. G398 itself does not provide such a bridge.

The current G396 provenance registry therefore remains authoritative for research isolation: all fourteen G395 hypotheses remain `UNRESOLVED`, have no source-rule IDs, and are `canonicalEligible=false`.

## Gate decision

`G398 = PASS`

`SOURCE RESOLUTION = CLOSED FOR CURRENT PRIMARY CORPUS`
`SEMANTIC CORE = SOURCE-CONFIRMED / SOURCE-SUPPORTED`
`EXECUTABLE GEOMETRY = UNRESOLVED`
`FROZEN GEOMETRY = BLOCKED`
`DEV = BLOCKED`
`VAL = BLOCKED`
`FRESH HOLDOUT = NOT AUTHORIZED`
`PRODUCTION = BLOCKED`

## Next permitted work

Proceed with the non-canonical research harness only: deterministic counterfactual evaluation, dataset provenance, and fixture coverage. Do not promote any G395 hypothesis to the Strategy Adapter, and do not begin canonical DEV optimization until a genuinely new authoritative source artifact resolves the remaining executable dimensions.
