# Order–Deal–Position Reconciliation Fixture Contract — 2026-10-26

## Purpose

The previous lifecycle contract classified one supplied order/deal observation. This follow-up adds a deterministic research-only reconciliation pass that joins supplied records only by explicit identifiers and reports broken or ambiguous links.

## Matching rules

- An order links to deal records only through the supplied `order_ticket`.
- Deal records are kept as individual tickets, including repeated ticket values; the fixture does not deduplicate evidence.
- Position linkage uses supplied nonzero `position_id` values and supplied position-ticket snapshots.
- Orphan deals, duplicate identifiers, conflicting position IDs, missing position snapshots, orders without linked deals, and unreferenced positions are surfaced as issues.
- A linked group is not a statement that an order was fully filled or that the supplied history is complete. No volume aggregation, completion inference, timestamp ordering, or fill synthesis occurs.

## Status meanings

- `LINKED`: supplied identifiers agree and the group has no detected issue.
- `INCOMPLETE`: one or more expected links/snapshot records are absent or unreferenced; this is not proof the broker record never existed.
- `CONFLICT`: the same group contains contradictory position identifiers.
- `DUPLICATE`: duplicate order/deal/position identifiers were observed.
- `UNRESOLVED`: an invalid identifier prevents a trustworthy classification.

## Tests

Synthetic tests cover multiple deal tickets linked to one order/position, missing deals, orphan deals, conflicting position IDs, duplicate order/deal IDs, unreferenced positions, invalid IDs, missing position snapshots, and the explicit non-claim that reconciliation does not establish fill completion.

## Limits / replay gate

This is not a live MT5 adapter and has not been run against broker history. It does not reconcile delayed history windows, partial-fill volume arithmetic, order/deal lifecycle race conditions, timestamps or event sequence, costs/commission allocation, netting versus hedging behavior, or broker-specific identifier semantics. Those remain unresolved and replay stays blocked until supported by source and broker evidence.
