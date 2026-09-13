# G381 — Discrimination Matrix Consolidation

Date: 2026-09-13  
Layer: `NON_CANONICAL_HYPOTHESIS`  
Gate: `FROZEN-GEOMETRY-BLOCKED`

G381 consolidates source evidence and synthetic execution without treating synthetic output as source truth.

| Dimension | Consolidated status |
|---|---|
| P-Gap endpoints | SOURCE-UNDERDETERMINED |
| P-Gap pressure context | IMPLEMENTATION-DISTINCT; semantic concept is source-confirmed |
| P-Gap timing | IMPLEMENTATION-DISTINCT |
| A/B/C/D anchor field | IMPLEMENTATION-DISTINCT |
| Parent vs nested leg | IMPLEMENTATION-DISTINCT |
| Entry price vs fill | IMPLEMENTATION-DISTINCT |
| C timing | SOURCE-UNDERDETERMINED |
| SL boundary | IMPLEMENTATION-DISTINCT |
| TP mapping | SOURCE-CONFLICT |

## Important distinction

`IMPLEMENTATION-DISTINCT` means candidate encodings can produce different machine outputs. It does **not** mean the source has selected one encoding.

`SOURCE-UNDERDETERMINED` means the current authoritative corpus does not provide enough executable information to choose among candidates.

`SOURCE-CONFLICT` means two authoritative statements/concepts still require reconciliation before a canonical implementation can be frozen (notably AB=CD versus the official default 1:1 target statement).

## Gate

The consolidated evidence strengthens the case for keeping geometry frozen rather than weakening it. No canonical Strategy A rule is promoted, and no historical optimization is authorized.

## Next research stage

Expand synthetic fixtures to cover the remaining pairwise combinations and state transitions, especially:

1. parent vs nested/deeper leg selection;
2. trigger vs pending-limit fill timing;
3. entry/C/target coupling;
4. SL boundary under wick/body divergence;
5. target mapping under different risk distances.

The purpose is to identify exactly which dimensions can be separated by observable market states and which remain fundamentally source-underdetermined.
