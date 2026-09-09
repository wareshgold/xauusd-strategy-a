# SP2L F11 Pending-Order Update Run V1 — 2026-09-09

## Scope

F11 isolates the lifecycle of a source-confirmed pending Limit while new structural candles develop. It is synthetic and does not freeze the unresolved replacement threshold.

## Source-aligned behavior

The source supports:

- placing a Limit order before the next candle when the structural correction provides the relevant level;
- retaining an existing pending order when the new structure does not materially alter the relevant risk distance;
- deleting/replacing the pending order when the new structure makes that distance materially different;
- keeping the execution model as a pending Limit rather than replacing it with a market-close reclaim.

The exact meaning of "materially different" is not numerically specified by the currently resolved source evidence.

## State machine

`PENDING → KEEP`

when the structural order remains unchanged.

`PENDING → UNRESOLVED`

when the candidate order changes but the source-level materiality threshold has not been established.

`PENDING → REPLACE`

is representable only after an explicit source-level qualitative determination that the distance is materially different. The fixture intentionally does not manufacture a numeric threshold.

## Test result

**PASS — lifecycle states are deterministic without inventing the missing threshold.**

The implementation proves that an unchanged order is KEEP, while a changed order cannot be automatically labelled REPLACE merely because its numeric distance changed.

## What remains unresolved

- exact materiality threshold;
- whether the comparison is based on absolute price distance, relative distance, R multiple, or another source-defined measure;
- exact anchor used for the updated Entry and structural Stop;
- whether every Spike variant follows the same update sequence.

## Gate decision

**F11 SYNTHETIC STATE-MODEL: PASS**

**SOURCE RESOLUTION: PARTIAL**

**FROZEN GEOMETRY: BLOCKED**

No historical optimization or live execution rule is authorized from this fixture.

## Next step

F12: discriminate the source's 1-candle / 2-candle / 3-candle trigger family without collapsing it into an invented universal trigger pattern.
