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


## 2026-09-15 session snapshot — unique checkpoint

Commit `3682250ec551ac84fcac07ea7a658a9d5c7e8a2e` recorded a distinct 2026-09-15 session snapshot that is not represented by the other duplicate snapshot refs.

Durable items preserved:
- C01 P-Gap was classified SOURCE_DISCRIMINATED, while executable geometry remained governed rather than frozen.
- C02 SL was a working fixed test rule (50/60/70/80 pips; RR 1:2), explicitly non-canonical.
- C03 AB=CD / Leg-2 equality remained blocked at that checkpoint.
- C04 TP1/TP2/2X was source-discriminated.
- C05 M15/MA50 was a working fixed test rule, non-canonical.
- C06 pending-order behavior was source-discriminated.
- C07 trigger classifier and C08 correction/invalidation remained blocked.
- MT5 trailing stop was explicitly optional execution/position management, production OFF and absent from the no-trailing research baseline.
- No trailing distance, activation threshold, step, tick/bar convention, broker numeric constraint, fill semantics, or production BUY/SELL rule was frozen.
- PR #196 was an open draft at that checkpoint; its GitHub-reported head was `a49fa5134336c0c9bb78bf3693afe13494da95c5`, with an explicit synchronization/CI verification item preserved.

The unique checkpoint does not authorize canonical geometry or production execution.

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


## 2026-09-09 source-resolution evidence

The 2026-09-09 entry/trigger/P-Gap research established durable source boundaries:
- pending-limit entry is source-confirmed; exact Entry price anchor and wick/body edge remain unresolved;
- structural invalidation is source-confirmed; exact anchor and deterministic replacement threshold remain unresolved;
- source examples include 1-, 2-, and 3-candle trigger constructions, but no universal trigger taxonomy/acceptance rule is frozen;
- 2X is source-confirmed terminology/concept, but its exact formula/reference levels remain unresolved;
- P-Gap is source-confirmed as a valid-breakout concept distinct from E-Gap/Common-Gap, but its executable formula and price/candle anchors remain unresolved;
- AB=CD is source-confirmed as the Leg-2 relationship, while A/B/C/D anchors and equality tolerance remain unresolved;
- Entry = Leg2Start is not authorized as a canonical assumption;
- market-close reclaim, fixed-distance stop, arbitrary ATR/pip/percentage replacement thresholds, generic BOS/MSS, generic FVG/three-candle imbalance, and unconfirmed bearish mirrors remain non-canonical.

These findings came from the 2026-09-09 source ledger and discrimination fixtures. They preserve evidence boundaries only and do not freeze Strategy A geometry.

## F11 pending-order refresh evidence — 2026-09-14

F11 established that the source demonstrates pending-order refresh/replacement behavior when subsequent structure materially changes the risk relationship, while the deterministic retain-versus-replace condition remains unresolved.

Preserved boundary:
- market-entry-on-close/reclaim is not a substitute for the source-confirmed pending-Limit model;
- no pip/tick/ATR/percentage/candle-count refresh threshold is source-confirmed;
- no rule requiring movement on every swing is frozen;
- no universal bearish mirror is assumed.

F11 remains SOURCE-DOES-NOT-DISCRIMINATE; it authorizes no engine change and leaves frozen geometry blocked.
