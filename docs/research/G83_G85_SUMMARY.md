# G83-G85 Summary

- G83: append-only recovery journal with monotonic sequence numbers.
- G84: strict event ordering; sequence gaps/reordering fail closed.
- G85: deterministic restart reconstruction from known lifecycle events; unknown events are never interpreted as success.

Demo/research infrastructure only. Strategy A geometry and production authorization remain unchanged.