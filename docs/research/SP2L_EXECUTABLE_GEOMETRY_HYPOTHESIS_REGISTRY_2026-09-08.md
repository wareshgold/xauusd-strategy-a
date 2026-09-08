# SP2L Executable Geometry Hypothesis Registry — 2026-09-08

This registry is a research catalogue, not a specification.

## Entry

| ID | Candidate interpretation | Status |
|---|---|---|
| E1 | BUY uses source-relevant previous Low / SELL previous High as pending-limit reference | SOURCE-CONFIRMED SEMANTIC; exact candle identity unresolved |
| E2 | Entry equals P-Gap boundary | REJECTED AS CANONICAL |
| E3 | Entry equals classical harmonic C | REJECTED AS CANONICAL |
| E4 | Entry equals 50% entry-to-SL retracement | REJECTED AS BASE ENTRY |
| E5 | Entry occurs only after market close-reclaim | REJECTED AS CANONICAL |

## Stop / invalidation

| ID | Candidate interpretation | Status |
|---|---|---|
| S1 | SL behind Spike-origin candle | SOURCE-CONFIRMED SEMANTIC; exact price unresolved |
| S2 | SL at origin wick extreme | UNRESOLVED |
| S3 | SL at origin body boundary | UNRESOLVED |
| S4 | SL at breakout candle extreme | UNRESOLVED / NOT SOURCE-CONFIRMED |
| S5 | SL with fixed numeric buffer | UNRESOLVED / NOT SOURCE-CONFIRMED |

## Leg 1

| ID | Candidate interpretation | Status |
|---|---|---|
| L1 | Spike-origin → Spike extreme | STRONGEST CURRENT CANDIDATE; NOT FROZEN |
| L2 | Breakout candle/level → Spike extreme | UNRESOLVED |
| L3 | First structural High/Low → Spike extreme | UNRESOLVED |

## AB=CD tolerance

No tolerance candidate is promoted. Exact equality is the semantic relationship; the executable tolerance remains unresolved.

## Research rule

A candidate may be eliminated by source evidence or synthetic geometry only when the source semantics actually discriminate it. A candidate must never be promoted because it improves historical P/L.

## Production boundary

None of E1-E5, S1-S5, or L1-L3 may be imported into production as an executable rule until the Frozen Geometry gate is passed.
