# SP2L Same-Day Forward Reconciliation — 2026-09-21

## Finding

The first same-day audit found 2 research candidates and 0 forward matches:

- 02:13 UTC SELL, entry 4373.25, SL 4373.48, TP 4373.02
- 03:51 UTC SELL, entry 4365.99, SL 4370.63, TP 4361.35

However, these are NOT yet evidence that the running forward test missed live candidates.

PR #239 shows the author-replica forward-test branch was created/updated at approximately 06:05 UTC, while both candidates occurred earlier. Therefore the forward runner could not have observed those historical trigger events while it was running.

## Correct interpretation

Status of both candidates: PRE_FORWARD_START_CANDIDATE.

The audit must distinguish:

1. historical candidates occurring before forward-test start;
2. candidates occurring while the forward runner was active;
3. candidates after runner stop/restart;
4. genuine candidates present during runner uptime but absent from forward events.

Only category 4 is evidence of a forward-test detection miss.

## Research boundary

No claim is made about canonical Strategy A. The candidates come from the current research-only author replica and therefore do not resolve the source blockers or Frozen Geometry.

## Next diagnostic

Run the same reconciliation with an explicit forward-test start timestamp and compare only candidates whose trigger time falls inside the runner actual uptime window. Also inspect the forward event log START/STOP timestamps.

No production, canonical geometry, fill semantics, or trading authorization changes.
