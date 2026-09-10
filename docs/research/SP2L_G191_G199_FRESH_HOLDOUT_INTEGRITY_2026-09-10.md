# SP2L G191-G199 — Fresh Holdout Integrity

## Scope

This batch adds a research-only integrity boundary for the Fresh Holdout.

## Controls

- Fresh Holdout dataset identity is represented by an explicit fingerprint and window identifier.
- A dataset fingerprint mismatch blocks the integrity decision.
- Applying optimization to the Fresh Holdout blocks the decision.
- Missing identity or missing recorded results remain UNKNOWN rather than being treated as success.
- A recorded result without its result fingerprint blocks the decision.
- A complete, matching, non-optimized, recorded result passes this integrity boundary.

## Non-goals

This batch does not define Strategy A geometry, P-Gap geometry, Entry, Stop, AB=CD anchors/tolerance, trigger rules, TP projection, or BUY/SELL authorization.

Fresh Holdout integrity PASS is evidence hygiene only. It is not statistical validation and does not authorize production.
