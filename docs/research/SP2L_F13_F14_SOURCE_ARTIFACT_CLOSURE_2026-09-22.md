# SP2L F13/F14 Source Artifact Availability & Traceability Closure — 2026-09-22

## Audit scope
Final availability/traceability pass for F13 (2X) and F14 (AB=CD), using the archived primary video audit, transcript, Batch17/21/22 evidence, and the existing source-resolution records on the current branch.

## Artifact availability finding
The repository does contain traceable primary-video evidence for the relevant teaching windows, including the direct frame audit from 2026-09-20. The artifact is sufficient to confirm concepts and visual relationships, but the sampled primary frames do not expose machine-resolvable A/B/C/D labels, OHLC endpoint semantics, or an AB=CD tolerance.

Likewise, the 2X evidence is sufficient to confirm an optional secondary-position concept and a demonstrated half-target / 50%-of-reference-distance relationship, but it does not uniquely specify a universal executable lifecycle across pending, filled, refreshed, and unfilled states.

## F14 closure test
Primary evidence confirms:
- SPIKE-2LEG ↔ 2Leg / AB=CD;
- Leg2 expected to match Leg1 in magnitude;
- target associated with completion of Leg2;
- nested leg structures can occur.

Primary evidence does NOT uniquely determine:
- A/B/C/D endpoint identities;
- observed versus projected D;
- wick/body/open/close/structural-pivot measurement;
- candidate precedence when multiple structural points exist;
- equality tolerance or rounding.

Result: **F14 remains PARTIAL / UNRESOLVED.**

## F13 closure test
Primary evidence confirms:
- 2X is a distinct secondary-position concept;
- 2X can be optional;
- one demonstrated context associates 2X with approximately half-target progression;
- author-associated source material supports a 50%-of-entry-to-SL relation.

Primary evidence does NOT uniquely determine:
- universal activation predicate;
- reference state when entry is pending/refreshed/filled;
- mandatory versus optional behavior in every setup;
- sizing rule;
- pending versus immediate execution lifecycle;
- fill/touch/close/Bid/Ask semantics;
- interaction with TP1/TP2.

Result: **F13 remains PARTIAL / UNRESOLVED.**

## Search exhaustion / evidence boundary
The current repository contains the relevant archived source windows and multiple forensic passes. The 2026-09-20 raw-video audit explicitly sampled the key F13/F14 timestamps and recorded the negative finding that no executable AB=CD geometry was visible. Re-reading the same evidence cannot legitimately create a missing endpoint label, tolerance, or lifecycle predicate.

This is therefore an **evidence boundary**, not an implementation gap to be filled by inference.

## Consequence for workflow
Do not continue repeating the same frame-level audit as if it could close F13/F14 without a genuinely new primary artifact or author statement.
Instead:
1. retain the source-confirmed semantic layer;
2. keep deterministic discrimination fixtures active for regression protection;
3. reconcile research-only implementation candidates against the source boundary;
4. continue source resolution only when new discriminating primary evidence becomes available;
5. keep Frozen Geometry and downstream validation gates locked.

## Gate
| Gate | Result |
|---|---|
| F13 semantic layer | SOURCE-CONFIRMED |
| F13 executable lifecycle | UNRESOLVED |
| F14 AB=CD magnitude | SOURCE-CONFIRMED |
| F14 executable anchors/tolerance | UNRESOLVED |
| Source artifact availability | SUFFICIENT FOR SEMANTICS / INSUFFICIENT FOR EXECUTABLE CLOSURE |
| Frozen Geometry | BLOCKED |
| Untouched Validation | LOCKED |
| Fresh Holdout | LOCKED |
| Production | OFF |

No canonical production code changed.