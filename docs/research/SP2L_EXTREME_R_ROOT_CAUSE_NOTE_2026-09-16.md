# SP2L Extreme-R Root-Cause Note — 2026-09-16

## Finding

The persisted 1min baseline contains a SELL observation at `2026-08-20 20:54:00` with Entry `4521.5838`, Stop `4521.61331`, TP1 `4517.8892399999995`, risk distance `0.02951`, and reported `125.19688241535353R`.

## Deterministic reconstruction

`risk = abs(entry - stop) = 0.02951`.

`reward = abs(tp1 - entry) = 3.69456` approximately.

`R = reward / risk = 125.19688241535353`.

The result is therefore arithmetically reproducible from the persisted prices. It is not evidence by itself of a metric-engine arithmetic defect.

## Geometry chain requiring source review

The current baseline constructs Entry from `detectEntryTrigger(...).entryPrice`, where the trigger uses a post-correction candle close reclaim. It constructs Stop from `getInvalidationRule(...).invalidationLevel`, which is the correction extreme. TP1 is constructed from the correction extreme plus/minus the implementation's Leg-1 size. These are implementation-defined working rules and are not canonical frozen geometry.

## Gate interpretation

- Extreme-R arithmetic: reproducible.
- Metric clipping: none introduced by this finding.
- Implementation bug: NOT established.
- Geometry correctness: NOT established.
- Canonical Strategy A rule: NOT established.

## Required next work

Audit the actual candle sequence around the observation and source evidence for Entry/SL anchoring. If source evidence cannot discriminate the geometry, retain `UNRESOLVED`; do not add a minimum-risk filter merely to suppress the 125R observation.
