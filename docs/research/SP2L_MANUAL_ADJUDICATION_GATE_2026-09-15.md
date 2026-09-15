# SP2L Manual Adjudication Gate — 2026-09-15

## Status

`GOVERNANCE_CONTRACT_ONLY`

This document defines the review boundary between source evidence intake and any future frozen-geometry decision. It does not adjudicate a geometry dimension and does not authorize execution.

## Gate sequence

```text
Tier-1 / Tier-2 Evidence
        ↓
Evidence Candidate Intake
        ↓
Discriminator Review
        ↓
Human Manual Adjudication
        ↓
SOURCE_DISCRIMINATED / REMAINS_BLOCKED
        ↓
Frozen Geometry Readiness Review
```

## Mandatory review questions

For every candidate, the human adjudicator must record:

1. Does the cited source actually contain the claimed discriminator?
2. Is the source reference precise enough to reproduce the observation?
3. Does the evidence distinguish the candidate geometry from the currently unresolved alternatives?
4. Is the interpretation based on source meaning rather than generic technical-analysis convention?
5. Does the candidate require an invented threshold, buffer, formula, candle indexing rule, or execution assumption?
6. If ambiguity remains, which hypotheses remain viable?

## Decision outcomes

### SOURCE_DISCRIMINATED

Allowed only when the source evidence materially and reproducibly discriminates the executable dimension and the adjudicator explicitly records the basis.

This outcome is a prerequisite for later freeze review; it is not itself production authorization.

### REMAINS_BLOCKED

Used whenever the source does not uniquely discriminate the executable geometry, the evidence is insufficient, or interpretation would require invention/inference.

## Non-negotiable prohibitions

Manual adjudication must not use:

- backtest performance;
- parameter optimization;
- generic market conventions;
- inferred symmetry;
- implementation convenience;
- undocumented buffers or thresholds;
- retrospective selection of the best-performing interpretation.

No adjudication record may introduce executable BUY/SELL logic.

## Current research boundary

The existing 10 executable geometry dimensions remain blocked until each has source-discriminating evidence and a corresponding human adjudication record. The current source-resolution stop is therefore preserved.

## Reproducibility requirement

Every adjudication record must retain the candidate ID and its immutable provenance so another reviewer can inspect the same evidence without relying on undocumented context.
