# Proposed review: fail closed on unavailable exposure inventory

Status: proposal only. No upstream branch, PR or merge created.

Suggested target: research/strategy-a-v3-1-magic-clock-guard-20261102, pinned base dc14a451669992d39bad559a125a7b0196e410e4. Re-check the current target and overlapping work before applying; this is not a recommendation to merge without review.

Local branch: audit/offline-independent-20261102
Commit: 5c6ab4b7de7db320c9a0019a1c97500c2d9e08f6

## Problem

positions_get or orders_get returning None was coerced to an empty list. active_exposure_count could then report zero exposure and permit a request path even though existing inventory was unknown.

## Narrow change

- Preserve valid empty tuples/lists as empty.
- Raise an internal ExposureInventoryUnavailable identifying the failed query.
- Convert it at execute_signal into ok=false, reason=EXPOSURE_INVENTORY_UNAVAILABLE before market access or order submission.
- Preserve existing magic-scoped exposure semantics.
- Add nine synthetic cases and make an existing fixture explicitly owned.

## Validation

Six new failure cases failed before the code change; all nine new cases passed after. The final gateway plus helper/recovery/lock suites pass45 tests offline. Broader repository failures/environment blockers are documented and not represented as green.

## Exclusions / residual risk

No strategy rules, thresholds, fills, configuration, production operations or data changed. The runner still has missing dependencies, trailing permission bypass, forming-bar/restart/clock/idempotency concerns. This patch does not make execution safe or validated, and does not create broker atomicity against external inventory changes.

## Required reviewer checks

Review the result schema and any consumers; confirm explicit failure events do not get treated as completed trades; review candidate-consumption behavior separately; rerun on the intended Python runtime and integrated runner branch with bounded fake-only wiring tests. Do not test by initializing MT5 or placing orders.
