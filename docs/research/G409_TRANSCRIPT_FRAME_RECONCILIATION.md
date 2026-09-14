# G409 — Transcript ↔ Exact-Frame Reconciliation

## Purpose

G409 is the next source-resolution gate after G408. It reconciles the recovered timestamped transcript against the registered raw-video frame evidence without promoting visual similarity into deterministic geometry.

## Evidence hierarchy

1. Raw authoritative source video
2. Exact frame observations from the registered source asset
3. Provenance-identified transcript
4. Creator-published secondary web material
5. Research hypotheses

If transcript wording and frame geometry disagree or remain ambiguous, the result stays unresolved.

## Reconciliation matrix

| Window | Transcript evidence | Frame evidence | Current decision |
|---|---|---|---|
| 34:14–35:50 | P-Gap / pressure-gap construction; breakout + follow-through relationship | Registered frame window | **P-Gap semantic relation strengthened; executable OHLC formula unresolved** |
| 36:15–37:10 | 2Leg identified with AB=CD; Leg 2 expected equal to Leg 1 | AB=CD drawing registered | **AB=CD magnitude relation source-confirmed; A/B/C/D anchors and tolerance unresolved** |
| 38:18–39:48 | correction reaches below first low in bullish example; Buy Limit may be placed before next candle completes | Buy Limit + horizontal level + SL visible in registered window | **Pending-limit and first-low correction semantics strengthened; exact limit price/fill semantics unresolved** |
| 41:18–42:40 | activated Buy with SL; TP1/TP2 discussed | SL and TP1/TP2 visible | **SL/target semantics strengthened; executable stop boundary and TP1/TP2 geometry unresolved** |
| 1:04:19–1:04:32 | later example explicitly uses reward 1, reward 2 optional | Later source example | **1R primary target convention strongly corroborated; geometric mapping unresolved** |

## Source-confirmed conclusions after reconciliation

- SP2L = Spike → correction → 2Leg.
- Valid directional construction requires P-Gap / pressure-gap semantics; P-Gap remains distinct from generic gap taxonomy.
- AB=CD / Leg1 = Leg2 is explicitly source-confirmed.
- Bullish correction is described as reaching below the first low in the demonstrated example.
- Pending Buy Limit placement before completion of the next candle is explicitly described.
- Structural invalidation exists before activation.
- SL is associated with the spike-origin candle.
- TP1/TP2 are distinct targets; primary/default demonstrated reward is approximately 1R.

## Unresolved dimensions — deliberately not frozen

### P-Gap
- exact candle count;
- exact OHLC fields;
- exact boundary comparison;
- minimum price/tick magnitude;
- tolerance.

### AB=CD
- exact A anchor;
- exact B anchor;
- exact C anchor;
- exact D construction in executable price coordinates;
- equality tolerance.

### Entry
- exact pending-limit price;
- whether the order is exactly at the first-low reference or another source-defined point;
- fill/touch semantics;
- overshoot handling;
- pre-fill cancellation/invalidation rule.

### Stop
- exact spike-origin candle price field;
- wick/body boundary;
- buffer;
- executable stop versus structural reference.

### Targets
- exact TP1 price mapping;
- exact TP2 price mapping;
- relationship between TP1/TP2 and AB=CD projection;
- whether 1R is canonical for every setup or the default demonstrated target.

## Negative controls

The following are explicitly rejected as automatic source interpretations:

- generic three-candle imbalance = P-Gap;
- fill price = geometric C;
- arbitrary A/B/C anchors;
- arbitrary AB=CD tolerance;
- generic Fibonacci retracement as entry;
- market close-reclaim replacing pending Buy Limit;
- arbitrary wick/body stop selection;
- arbitrary TP2 extension formula.

## Gate decision

**G409 = SOURCE-RECONCILIATION PARTIAL / GEOMETRY STILL BLOCKED.**

The transcript and registered visual evidence are now reconciled at the semantic level. No executable geometry is frozen because the available frame register does not contain coordinate-level frame images for every required annotation transition.

G400 remains BLOCKED.

## Required next evidence

The next pass should obtain exact frame images (or a provenance-controlled frame extraction artifact) for the registered windows, especially:

- 34:14–35:50;
- 36:15–37:10;
- 38:18–39:48;
- 41:18–42:40;
- 1:04:19–1:04:32.

The frame extraction must preserve source asset SHA-256, timestamp, FPS, frame index, and extraction method so that observations are reproducible.
