# SP2L Batch 28 — Temporal Pending-Order State Reconstruction — 2026-09-16

## Purpose

Perform a temporal reconstruction of the primary SP2L teaching sequence around **39:00–41:00**, using the dense 5-second frame sequence, to separate directly observed state transitions from interpretations that remain unresolved.

Source meaning outranks implementation convenience and backtest performance.

## Observed sequence

| Time | Visible event | Evidence level | Deterministic meaning established? |
|---|---|---|---|
| ~39:00 | `BO` annotation appears beside bullish candle sequence; multiple horizontal references are visible | Direct primary-artifact observation | BO concept is taught; exact trigger semantics unresolved |
| ~39:05–39:15 | `Buy Limit` annotation is developed while the bullish sequence and reference levels remain visible | Direct primary-artifact observation | Pending Buy Limit concept is taught; exact price construction unresolved |
| ~39:20–39:25 | Simplified bullish candle sequence remains; horizontal reference level remains | Direct observation | A level remains associated with the setup; exact mapping unresolved |
| ~39:30–39:40 | `Buy Limit` is explicitly tied to a horizontal level; a lower `SL` reference is added | Direct primary-artifact observation | Entry and risk references are distinct; exact OHLC semantics unresolved |
| ~39:45–39:55 | Setup is circled/annotated; editing handles appear on the drawing | Direct observation | Diagram is being modified/managed; no executable fill event is proven |
| ~40:00 | Original horizontal level remains visible while price is represented above it | Direct observation | Pending-level persistence after placement is supported |
| ~40:05 | `delete` is written; a second sloped/blue reference annotation appears near the newer price structure while the original horizontal level remains visible | Direct observation | Deletion is taught; a possible new-candidate/refresh context is visible, but replacement is not explicitly stated |
| ~40:10–40:20 | `delete` remains; the newer reference is emphasized with an arrow/measurement annotation | Direct observation | Old-order deletion is part of the illustrated management sequence; causal condition remains unresolved |
| ~40:25–41:00 | Numbered `money` / management annotations continue around the same setup | Direct observation | Management/risk discussion continues; no deterministic lifecycle transition is exposed |

## Key temporal finding for F11

The dense sequence provides stronger evidence than a single frame because the **same setup evolves through time**:

`Buy Limit level shown → level persists → delete annotation appears → a newer structural reference is also drawn`

This is **consistent with** a stale-order deletion / candidate-refresh workflow, but the source does not explicitly say that the newer reference replaces the old pending order. Therefore the strongest source-aligned statement is:

> **A pending Buy Limit is maintained, and deletion is explicitly taught later in the same evolving setup; a possible new-level/refresh context is visible, but replacement causality is not source-complete.**

This does not authorize `delete = replacement`, `delete = invalidation`, `delete = timeout`, or any other specific condition.

## F12 temporal boundary

The sequence establishes an ordering between the teaching concepts:

`BO / Valid-BO context → Buy Limit placement → pending level persistence → later management`

It does **not** establish the exact event semantics of BO. In particular, the frames do not prove:

- wick break vs candle close;
- touch vs break;
- next-candle confirmation;
- a 1/2/3-candle taxonomy;
- intrabar vs bar-close evaluation.

Therefore F12 remains concept-confirmed but taxonomy-unresolved.

## F9 activation boundary

The sequence clearly distinguishes **placement of a pending Buy Limit** from subsequent order management. There is no visible frame showing price returning to the level and an execution event being explicitly labeled as the fill.

Therefore:

- pending-entry existence: confirmed;
- exact Buy Limit price: unresolved;
- activation/fill trigger: unresolved;
- intrabar/bar-close fill semantics: unresolved.

## F10 boundary

The sequence visually separates a Buy/entry reference and a lower SL reference. It does not expose the exact rule determining whether SL is structural, wick-based, body-based, or another boundary, nor does it expose the precise invalidation event.

## State-machine ledger

The following state labels are safe as **research observations**, not canonical execution rules:

1. `CANDIDATE/SETUP` — bullish structure and BO annotations are visible.
2. `PENDING-LEVEL-SHOWN` — Buy Limit level is explicitly drawn.
3. `PENDING-LEVEL-PERSISTS` — the level remains visible as the diagram advances.
4. `DELETE-TAUGHT` — deletion is explicitly annotated later.
5. `NEW-REFERENCE-VISIBLE` — a newer reference/line is drawn during the deletion sequence.
6. `POST-MANAGEMENT` — numbered money-management annotations continue.

Transitions that remain unresolved for deterministic replay:

- exact event that creates the pending order;
- exact price used for the order;
- exact fill condition;
- exact delete condition;
- whether the newer reference replaces the old order;
- whether multiple pending orders can coexist;
- expiry/timeout;
- cancellation on invalidation;
- priority when several candidate levels exist.

## Resolution impact

**F11:** evidence is strengthened from a static `Buy Limit + delete` observation to a temporal sequence showing persistence followed by deletion and a visible newer reference. Replacement/refresh remains a hypothesis, not a source-confirmed rule.

**F12:** temporal ordering is strengthened, but trigger taxonomy remains unresolved.

**F9:** pending-order placement is strongly evidenced; activation/fill remains unresolved.

**F10:** entry/risk separation remains evidenced; exact invalidation/price semantics remain unresolved.

## Explicit non-promotion boundary

No canonical rule is introduced for:

- Buy Limit price construction;
- BO confirmation;
- P-Gap indexing or formula;
- delete/replacement/expiry;
- fill semantics;
- SL boundary;
- position sizing.

No backtest result is used to select an interpretation.

## Gate impact

- Source Resolution: **PARTIAL PASS — temporal order-management evidence strengthened**
- F11: **temporal persistence + delete observed / replacement causality unresolved**
- F12: **temporal ordering strengthened / exact trigger taxonomy unresolved**
- F9: **pending placement confirmed / activation unresolved**
- F10: **entry/risk separation observed / exact price and invalidation unresolved**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**
