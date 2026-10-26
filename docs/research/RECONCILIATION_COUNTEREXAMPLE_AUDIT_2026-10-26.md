# Reconciliation Counterexample Audit — 2026-10-26

## Scope

This note documents adversarial synthetic cases for `reconcile_order_deals_positions`. These are structural correctness checks, not claims about MT5's complete broker lifecycle or execution semantics.

## Cases now covered

1. **Duplicate order ticket:** the order identity is not unique. The reconciliation emits a duplicate/ambiguous order group with no attached deals; matching deals remain explicit orphan observations because a unique order link cannot be established from the supplied rows.
2. **Duplicate deal ticket:** duplicate rows are retained and flagged. Repeated ticket values are not silently deduplicated or treated as proof of multiple unique deals.
3. **Duplicate position ticket:** duplicate identity remains explicitly marked. The reconciler must not describe that identity as simply absent from the supplied snapshot.
4. **Conflicting position IDs:** contradictory explicit identifiers remain conflicts.
5. **Missing deal or position rows:** the result describes only the supplied snapshot. It does not infer no fill ever occurred or that a query/history is complete.
6. **Invalid IDs:** invalid values remain unresolved instead of being repaired by inference.

## Invariants

- Join only by explicit identifiers.
- Preserve row-level duplicate evidence.
- Never attach one deal to two duplicate order identities as if the link were unique.
- Never infer fill volume, complete fill, or final position state from ticket linkage alone.
- Keep all issue codes visible even when status precedence selects one headline status.
- Identical inputs produce deterministic ordered output; no source rows are sorted or rewritten to imply chronology.

## Limits / follow-up

The function is a synthetic reconciliation aid. It does not model MT5-specific ticket reuse, netting/hedging semantics, partial-fill completion, history-query watermarks, temporal causality, or broker guarantees. Those require source and broker evidence before they can become canonical. These tests do not unblock replay by themselves.
