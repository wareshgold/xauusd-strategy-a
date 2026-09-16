# SP2L 125R Forensic Reconstruction — 2026-09-16

## Purpose

Record the deterministic reconstruction of the persisted 1min Strategy A observation at `2026-08-20 20:54:00` without changing, optimizing, or promoting any rule.

The reconstruction is implementation-forensic evidence only. Source meaning remains authoritative.

## Persisted observation

- direction: SELL
- entry: `4521.5838`
- stopLoss: `4521.61331`
- TP1: `4517.8892399999995`
- risk distance: `0.02951`
- R multiple: `125.19688241535353`

## Reconstructed chain

### 1. Breakout

- index: `449`
- timestamp: `2026-08-20 20:34:00`
- direction: SELL
- close: `4518.25215`

### 2. First follow-through

- index: `450`
- timestamp: `2026-08-20 20:35:00`
- close: `4517.36882`

This is the first qualifying follow-through under the current experimental detector semantics.

### 3. Spike candidate

Using the current experimental SpikeDetector window rule (`breakoutIndex - maxCandles + 1` through follow-through index, with `maxCandles = 8`):

- start index: `442`
- end index: `450`
- start timestamp: `2026-08-20 20:27:00`
- end timestamp: `2026-08-20 20:35:00`
- SELL startPrice (first candle high): `4521.12035`
- endPrice (last candle low): `4517.11988`
- directional fraction: `0.7777777777777778`
- overlap fraction: `0.3390934094045587`
- directional filter (`>= 0.5`): PASS
- overlap filter (`<= 0.8`): PASS

### 4. Correction / invalidation

Under the current experimental CorrectionDetector semantics for SELL, correction scanning begins after the spike and the first candle whose high exceeds the spike startPrice becomes the correction extreme.

- correction start scan: index `451`
- correction extreme index: `468`
- correction extreme timestamp: `2026-08-20 20:53:00`
- correction extreme high: `4521.61331`
- direction: SELL
- current experimental invalidation level: `4521.61331`

### 5. Trigger / entry

Under the current experimental EntryTrigger semantics for SELL, the first post-correction candle closing below the correction extreme supplies the trigger entry price.

- trigger index: `469`
- timestamp: `2026-08-20 20:54:00`
- OHLC: O `4520.89286`, H `4521.86617`, L `4520.0412`, C `4521.5838`
- condition `close < correctionExtreme`: TRUE
- trigger close: `4521.5838`
- persisted Entry: `4521.5838`
- Entry match: PASS

### 6. Risk distance

- Entry: `4521.5838`
- Stop: `4521.61331`
- absolute risk distance: `0.029509999999390857` (approximately `0.02951`)

### 7. Experimental Leg-1 projection / TP1

The current experimental projection implementation uses the spike window's first open and last close to derive Leg-1 size.

- spike first open (index 442): `4521.09289`
- spike last close (index 450): `4517.36882`
- Leg-1 size: `3.7240700000002107`
- projection origin: correction extreme `4521.61331`
- SELL TP1: `4521.61331 - 3.7240700000002107`
- reconstructed TP1: `4517.8892399999995`
- persisted TP1: `4517.8892399999995`
- TP1 match: PASS

### 8. R arithmetic

`(Entry - TP1) / (Stop - Entry)` reproduces the persisted result:

- reward distance: approximately `3.69456`
- risk distance: approximately `0.02951`
- R: `125.19688241535353`
- arithmetic reproduction: PASS

## Findings

1. The persisted 125R observation is arithmetically reproducible from the current experimental implementation chain.
2. Entry, Stop, TP1, and R all reproduce the persisted values.
3. The extreme R is not evidence by itself of a metric-engine defect.
4. No minimum-risk filter, stop buffer, wick/body preference, spread adjustment, alternate Entry anchor, or other suppression rule was introduced.
5. No profitability result was used to select the geometry.

## Geometry status

`UNRESOLVED` at source level.

This reconstruction does **not** establish that the current Entry, Stop, Spike, correction, trigger, or projection anchors are canonical. Source evidence must still discriminate the unresolved geometry questions before Frozen Geometry can pass.

## Gate status

- Source Resolution: PARTIAL PASS
- 125R forensic reconstruction: PASS
- Arithmetic integrity: PASS
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF
