# G375 — Hypothesis Execution Protocol

Date: 2026-09-13
Status: RESEARCH-ONLY / NON-CANONICAL
Gate: SOURCE RESOLUTION remains unresolved; FROZEN GEOMETRY remains BLOCKED.

## Objective
Execute the already-defined G368/G369 hypothesis layer without promoting any interpretation to canonical Strategy A.

## Guardrails
1. Every candidate remains `canonical=false`.
2. Historical profitability cannot resolve source meaning.
3. Generic gap geometry cannot be promoted to P-Gap.
4. `C = fill_price` is prohibited unless independently source-confirmed.
5. Fixed 2R/3R targets, invented tolerances, offsets, candle counts, MA/session gates are prohibited as canonical rules.
6. Trigger, pending-order state, and fill are distinct research states.
7. Parent and nested/deeper legs must remain separate candidate scales.
8. Any result that cannot discriminate two hypotheses is recorded as `UNDERDETERMINED`, not selected.

## Execution matrix
The existing 16 minimal-pair adversarial fixtures are the authoritative research fixture set for this phase. They cover:
- P-Gap endpoint indexing;
- wick/body separation;
- pressure context;
- breakout/FT versus higher-structure timing;
- A/B/C/D anchor choices;
- parent versus nested leg scale;
- trigger versus fill;
- pending-limit unfilled cases;
- SL origin boundary versus extreme/structural boundary;
- AB=CD versus fixed 1R and target hierarchy.

## Required result classes
For each hypothesis pair:
- DISTINCT: candidate rules produce different deterministic outputs;
- EQUIVALENT: candidates produce identical outputs for the fixture;
- SOURCE-CONFLICT: candidate contradicts authoritative evidence;
- UNDERDETERMINED: fixture/source cannot distinguish candidates.

## Promotion rule
No result in this protocol is sufficient for canonical promotion by itself. A candidate may move toward a frozen specification only after source confirmation of the corresponding geometry.

## Current disposition
G370 already established that the adversarial design distinguishes the major competing interpretations conceptually, while the source remains insufficient to select the intended executable geometry. Therefore this phase is a controlled hypothesis-execution layer, not a canonical strategy-development/backtest gate.

## Next required artifact
Produce a machine-executable fixture runner whose output is a versioned JSON result matrix. The runner must implement candidate hypotheses as separate research adapters and must preserve the source-status metadata for every output.
