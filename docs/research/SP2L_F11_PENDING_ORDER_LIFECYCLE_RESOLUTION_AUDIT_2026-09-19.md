# SP2L F11 — Pending-Order Lifecycle / Delete-Refresh Resolution Audit — 2026-09-19

## Purpose

Resolve F11 using only source-aligned evidence already archived in the repository. This audit tests whether the source uniquely determines when a pending Buy Limit must be kept, deleted, moved, or replaced.

No numeric timeout, candle-count rule, state machine, or refresh threshold is inferred from implementation or backtest performance.

## Evidence reviewed

- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `docs/research/SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `docs/research/SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`
- `docs/research/SP2L_SOURCE_RESOLUTION_GAP_REGISTER_F11_F14_PGAP_2026-09-16.md`
- `docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`

## Source-confirmed lifecycle observations

### 1. Pending Buy Limit is explicitly demonstrated

The primary sequence shows a Buy Limit level being established after the breakout/correction sequence. The source therefore confirms that a pending Limit order can exist before activation.

**Status:** pending-order concept = SOURCE-CONFIRMED.

### 2. Existing order can be deleted and a new order placed

The transcript at approximately 39:48 states that when a subsequent candle forms, the existing order may be deleted and a new order placed according to the changed distance to the stop.

Batch34 independently records persistence of the represented order level followed by an explicit `delete` annotation.

**Status:** delete/replace behavior = SOURCE-CONFIRMED at concept level.

### 3. The source does not define the mandatory predicate

The evidence does not uniquely establish what observable event makes deletion/re-placement mandatory.

Possible interpretations remain distinct:

- a subsequent candle changes the structural setup;
- a new candidate level supersedes the old one;
- the stop distance changes;
- the order becomes invalid;
- a time/candle expiry occurs;
- discretionary/manual management is being illustrated.

The source wording and inspected frames do not uniquely discriminate these possibilities.

Therefore a deterministic state transition cannot yet be frozen.

### 4. No numeric timeout is source-confirmed

The reviewed evidence does not provide a universal rule such as:

- delete after 1 candle;
- delete after 2 candles;
- delete after N candles;
- delete after a fixed number of minutes;
- delete at session close.

Any such rule would be an invented execution convention unless separately supported by primary evidence.

### 5. No deterministic replacement-price rule is source-confirmed

The source says a new order can be placed according to the changed distance to the stop, but does not uniquely specify:

- the new entry-price formula;
- the exact stop anchor;
- whether the original order is modified in place or cancelled/re-created;
- whether the new level must correspond to a newly formed structural point;
- whether the newest candidate always supersedes the previous one;
- what happens if several candidates appear.

Thus the complete pending-order state machine remains unresolved.

### 6. Fill semantics remain separate and unresolved

The source confirms that a Buy Limit is used and that the second leg triggers entry, but it does not uniquely define platform-level fill semantics such as touch, wick penetration, close, next-bar activation, spread/bid-ask handling, partial fill, or slippage.

These should not be silently embedded into F11.

## Deterministic F11 test

| Required lifecycle element | Source status |
|---|---|
| Pending Buy Limit can exist | SOURCE-CONFIRMED |
| Existing order may be deleted | SOURCE-CONFIRMED |
| Replacement/new order may follow | SOURCE-CONFIRMED |
| Exact mandatory deletion predicate | UNRESOLVED |
| Numeric candle/time timeout | UNRESOLVED |
| Exact replacement condition | UNRESOLVED |
| Exact replacement-price construction | UNRESOLVED |
| Multiple-candidate precedence | UNRESOLVED |
| Fill/activation semantics | UNRESOLVED |

## Deliberate non-inferences

This audit does **not** promote:

- the previously discussed 1–2 candle deletion idea into canonical behavior;
- any fixed candle timeout;
- any fixed time expiry;
- `delete = invalidation`;
- `delete = newer candidate`;
- `delete = stop-distance threshold`;
- automatic modification versus cancel/re-place;
- newest-candidate-wins precedence;
- any broker-specific fill behavior.

## F11 result

**PARTIAL / UNRESOLVED**

The source is strong enough to confirm that pending-order deletion/replacement is part of the demonstrated management behavior. It is not strong enough to determine the universal executable predicate or complete state machine.

Therefore F11 cannot be promoted to SOURCE_CONFIRMED executable status.

## Gate impact

- F11: **PARTIAL / UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- No new backtest or robustness run is justified by this pass.
- No canonical pending-order lifecycle is promoted.
- `LIVE_TRADING_ENABLE=false` remains unchanged.

## Next source-resolution priority

F11 is not closed. The next highest-value blocker remains **F10 — exact invalidation/SL price anchor**, followed by F12 trigger acceptance/precedence and F13 complete 2X lifecycle semantics.

P-Gap exact indexing/boundary/mirror semantics remains the highest-severity unresolved geometry item overall.

## Decision

**F11 remains PARTIAL / UNRESOLVED.**

The existing research implementation must not be reclassified as canonical based on this evidence.
