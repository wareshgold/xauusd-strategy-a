# G331 — Candidate Discrimination Matrix

Date: 2026-09-12
Inputs: G327 synthetic fixtures, G329 direct source-video audit, G330 numeric-annotation semantic audit.

## Objective

Record what the source evidence can and cannot discriminate among the surviving target mappings without using historical performance.

| Candidate | Source visual compatibility | Unique numeric bridge present? | Status |
|---|---|---|---|
| C1 | Strong | No | LEADING / NOT FROZEN |
| C2 | Compatible | No | ALIVE / NOT FROZEN |
| C3 | Compatible | No | ALIVE / NOT FROZEN |
| C4 | Only as unresolved/non-mappable | No | NON-MAPPABLE |

## Evidence constraints

### Evidence that supports C1

- The target schematic contains TP2, TP1, Entry and SL.
- Three ruler intervals are visibly represented.
- Handwritten 250 / 500 / 1000 annotations occur during the explanation.
- C1 can account for these values coherently as composite distances.

### Evidence that prevents freezing C1

- No explicit arrow/equation ties each number to a specific interval.
- The handwritten annotations are not printed labels of the original schematic.
- The inspected worked examples do not establish a universal point-distance rule.
- No source-confirmed statement establishes a target as a fixed multiple of stop risk.

## Decision rule

A candidate may become canonical only after source evidence uniquely identifies the executable mapping. Relative visual plausibility is insufficient.

Historical backtesting must not be used to break this tie.

## Gate result

`G331 = PASS (candidate discrimination recorded)`

`C1 = LEADING HYPOTHESIS`
`C2 = ALIVE`
`C3 = ALIVE`
`C4 = NON-MAPPABLE`
`CANONICAL_TARGET_MAPPING = UNRESOLVED`
`FROZEN_GEOMETRY = BLOCKED`
`DEV = BLOCKED`

The next productive action is source acquisition/inspection aimed specifically at an explicit numeric bridge or an executable order example containing enough price/entry/SL/TP information to discriminate C1/C2/C3.
