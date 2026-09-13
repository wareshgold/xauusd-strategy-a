# G382 — State Transition Counterfactuals

Status: RESEARCH ONLY / NON-CANONICAL

## Purpose
G382 expands pairwise synthetic discrimination into a state-transition view: `Parent Leg → Correction → Trigger → Pending → Fill → C → TP`, with invalidation as an alternate terminal state.

## Results
- 8 controlled scenarios.
- 5 implementation-distinct.
- 2 source-underdetermined.
- 1 equivalent.
- All remain `canonical=false`.

## Findings
1. Entry/fill: the state path demonstrates why a trigger cannot silently be treated as the fill or geometric C. The source confirms a pending-limit mechanism, but the exact price/fill/C relationship remains unresolved.
2. SL: wick/body choices can change risk and therefore cannot be normalized without source evidence.
3. TP: AB=CD projection and official 1:1 default can disagree or coincide. Coincidence is not evidence of source equivalence.
4. Parent/nested leg: both scales are preserved without selecting one; no universal selection rule is source-defined.
5. P-Gap: pressure/timing candidates can diverge, but synthetic divergence cannot determine which encoding is canonical.

## Gate
`FROZEN-GEOMETRY-BLOCKED` remains the only valid decision. G382 does not authorize DEV, historical optimization, live signals, or production.

## Next
Proceed to minimal-pair state perturbations: change exactly one transition at a time (trigger timing, pending persistence, fill timing, invalidation-before-fill, C timing, target mapping) and identify which dimensions remain structurally underdetermined without new authoritative evidence.
