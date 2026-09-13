# G378 — Source Resolution Gate Decision

Date: 2026-09-13  
Based on: G377 official-source geometry reconciliation  
Decision: **FROZEN GEOMETRY BLOCKED**

## Gate result
The authoritative source material establishes the semantic SP2L framework but does not provide enough executable geometry to freeze every deterministic Strategy A rule.

### Resolved enough for semantic freeze
- SP2L = Spike → 2 Leg / AB=CD.
- Valid Spike requires P-Gap; P-Gap is the Pressure Gap concept.
- Correction follows the first directional movement.
- Entry direction follows the Spike.
- Pending-limit entry during correction is source-supported.
- Structural invalidation/SL exists and references the Spike-origin candle.
- 50% secondary entry is explicitly described by the official page.
- Official default TP is 1:1.

### Still not executable/frozen
- P-Gap endpoints, wick/body treatment, overlap and minimum size.
- A/B/C/D OHLC/structural anchors.
- Canonical parent-vs-nested leg selection.
- Exact pending-limit price and complete trigger/fill semantics.
- Exact SL boundary/offset.
- Deterministic mapping of AB=CD vs TP1/TP2/R1/R2 vs official 1:1.
- Whether the 50% secondary entry is mandatory core logic or optional add-on.

## Promotion decision
No unresolved hypothesis may become canonical merely because it backtests well. G376 classifications remain `canonical:false`.

## Gate transition
SOURCE RESOLUTION remains open for targeted primary-source acquisition only. The project must **not** transition to FROZEN GEOMETRY, canonical synthetic fixtures, DEV, VAL, robustness, fresh holdout, or production until the missing executable geometry is authoritative and deterministic.

## Research safety
This decision explicitly rejects:
- generic three-candle gap → P-Gap promotion;
- pixel-derived endpoints;
- C = fill-price assumption;
- fixed 2R/3R target assumptions;
- invented SL offsets/tolerances;
- generalized candle-count/session/MA gates.
