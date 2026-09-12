# SP2L G321 — Target-Ratio vs R Audit

**Date:** 2026-09-12
**Status:** `RATIO_AND_R_SEMANTICS_SEPARATED`

## Finding

The source schematic's apparent equal intervals are a geometric relationship, while the worked order panel supplies concrete Entry/SL/TP prices. These must not be conflated.

Example A:
- Risk = |3237.12 - 3229.08| = 8.04
- Reward to shown TP = |3229.08 - 3213.44| = 15.64
- Reward/Risk ≈ 1.9453R

Example B:
- Risk ≈ |3235.50 - 3223.84| = 11.66
- Reward to shown TP ≈ |3223.84 - 3213.33| = 10.51
- Reward/Risk ≈ 0.9014R

The terminal target therefore cannot be declared universally 1R or 2R from these examples.

## Consequence

The source schematic may describe a construction ratio independently of the worked order's terminal TP. The current evidence does not establish whether TP1/TP2 are intermediate levels, alternatives, projections, or a ladder later filtered by another rule.

No R-based target formula is frozen.
