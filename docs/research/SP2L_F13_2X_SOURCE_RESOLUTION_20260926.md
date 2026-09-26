# SP2L F13 2X Source Resolution

Date: 2026-09-26
Status: SOURCE-PARTIAL / RELATION CONFIRMED, EXECUTION UNRESOLVED

## Primary evidence

The author explicitly describes 2X as an optional second position. At 41:26 he says the second position can be entered as a choice; at 41:37 he explains the reward relationship using a second entry that has a larger remaining reward relative to its own risk. He gives an example where equal dollar risk on the two positions can produce materially different dollar reward because the second entry is closer to the target. At 42:17 he refers to a dedicated "2nd position" explanation.

At 56:44–57:24 another example states that a 2X outcome can produce approximately 4% reward against 2% initial risk, and shows a later Buy Limit activation in the ongoing structure.

## Source-confirmed boundary

The source supports:

1. 2X is an optional secondary position, not a mandatory component of every setup.
2. The second position is entered later/closer to the target than the first position.
3. The second position can have a larger reward relative to its own risk because its entry is closer to the target while the structural stop relationship is different.
4. 2X is a money-management / second-position concept, distinct from the existence of the primary SP2L setup.
5. TP1 and TP2 are discussed separately from the optional second position.

## What remains unresolved

The primary source available in this pass does not provide a universal executable equation for 2X.

Unresolved items:

- exact 2X entry anchor;
- whether the intended entry is always exactly 50% of Entry-to-SL distance, or only approximately/illustratively so;
- exact relation to target/Leg-2 completion;
- whether 2X uses the same stop price as position 1;
- exact position-sizing equation;
- whether dollar risk, percentage risk, lot size, or another sizing basis is canonical;
- activation/fill semantics;
- cancellation/replacement lifecycle for the 2X order;
- whether every source example uses the same 2X geometry;
- deterministic bearish mirror.

The public author description of a secondary entry around half the distance to the stop can support a relation-level research hypothesis, but it does not by itself resolve the complete lifecycle and sizing contract.

## Research-only discrimination fixtures

F13-001: exact half-distance secondary entry.

F13-002: non-half but closer-to-target secondary entry.

F13-003: same primary entry/SL with different 2X candidate anchors.

F13-004: equal dollar risk between position 1 and position 2.

F13-005: equal lot size between position 1 and position 2.

F13-006: same 2X price with different stop distances.

F13-007: pending 2X touched, filled, and unfilled lifecycle states.

F13-008: bearish mirror.

Fixtures must expose the unresolved choices; they must not choose a formula from backtest performance.

## Current research implementation boundary

The repository may represent the commonly described half-distance relation as a research-only candidate, e.g. a secondary entry halfway from primary entry toward the stop. That representation must remain labelled SOURCE_CONFIRMED_RELATION_ONLY and must not be promoted to a canonical execution rule without source evidence for the full contract.

No canonical sizing, order lifecycle, or exact 2X price formula is introduced by this checkpoint.

## Gate

F13 = SOURCE-PARTIAL / RELATION CONFIRMED, EXECUTION UNRESOLVED.

Frozen Geometry remains BLOCKED. Untouched Validation, Fresh Holdout, and Production remain locked/off.

## Reopen condition

Reopen F13 only if new primary author evidence explicitly binds 2X to an exact price equation, sizing rule, stop relationship, or deterministic order lifecycle.