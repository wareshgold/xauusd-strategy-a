# SP2L Historical Evidence Archive — 2026-09-22

This archive consolidates information worth retaining from old branch families before redundant refs are removed.

## Source-resolution evidence retained

### 2026-09-08 source-resolution checkpoint
Source video evidence confirmed:
- SP2L Strategy / Spike-2Leg.
- AB = CD is explicitly shown.
- Valid BO = P-Gap is explicitly shown.
- 1M / 5M notation is visible.

Still unresolved from the available raster evidence:
- exact A/B OHLC anchors;
- exact C anchor;
- executable P-Gap OHLC formula;
- exact deterministic Spike grammar;
- AB=CD tolerance.

Therefore the correct state remained: G4 BLOCKED, G5 BLOCKED, P-Gap formula BLOCKED, G6 RESOLVED, canonical geometry freeze BLOCKED.

Important negative evidence:
- pending-limit fill price is not established as C;
- generic three-candle imbalance is not established as the teacher's P-Gap;
- historical performance must not select among geometric interpretations.

Original branch family: research/sp2l-gate-preparation-v19 and related gate-preparation snapshots.

### Source-to-code synchronization conclusion

The historical source-aligned audit established that legacy deterministic modules were not a canonical implementation of the source semantics.

Retained distinctions:
- P-Gap semantic relationship is source-confirmed, but its executable formula was unresolved.
- Spike detector heuristics are research heuristics, not source grammar.
- Legacy correction-extreme reclaim is not a substitute for demonstrated pending-limit entry semantics.
- AB=CD may be preserved as a relationship only after A/B/C anchors are source-confirmed.
- Fill price must not be silently substituted for C.

Historical source-aligned implementation was deliberately guarded against promotion.

## MT5 execution-layer evidence retained

The 2026-09-15 MT5 execution work is retained as an execution-layer boundary, not Strategy A geometry.

Confirmed engineering boundaries:
- position modification request carries position identity, direction, current SL and proposed SL;
- invalid identity/non-finite prices are rejected;
- unknown broker stop/freeze constraints cause refusal;
- proposed SL must not loosen an existing SL;
- no native .mq5 EA was authorized;
- no trailing distance, activation threshold, step, tick/bar convention, broker numeric limits, or fill semantics were frozen;
- no production BUY/SELL generation was introduced.

Trailing-stop validation remained planned/off:
- unit tests for disabled/invalid configurations and favorable-direction SL movement;
- MT5 tester/runtime validation only after execution parameters are frozen;
- baseline must remain trailing OFF;
- treatment, if ever enabled, must be separately frozen and compared without optimizing from realized performance.

Historical branch family: checkpoint/session-snapshot-2026-09-15* plus research/mt5-trailing-stop-execution-2026-09-15.

The old implementation/test files are not required by the current forward-test runtime; their durable engineering constraints are preserved here.

## Cleanup decision rule

Historical raw code, duplicate reports, generated outputs, and temporary workflows are not copied merely because they differ by path. They are preserved only when they contain unique evidence, a gate decision, a reproducibility identifier, or an unresolved research conclusion still relevant to SP2L.

Duplicate branch names pointing to the same commit do not provide additional evidence.

## Canonical-status safeguard

Nothing in this archive:
- freezes P-Gap geometry;
- chooses A/B/C/D anchors;
- defines AB=CD tolerance;
- defines fill semantics;
- promotes research parameters;
- authorizes production execution.

The active forward-test branch remains the operational research anchor.
