# SP2L Candle-Level Evidence Acquisition Protocol — 2026-09-19

## Purpose

Define the next evidence-acquisition step required for assumption dependency analysis.

This protocol acquires immutable candle-level evidence for the already archived research window. It does not alter, infer, or promote Strategy A source geometry.

## Frozen research target

Historical window represented by the archived weekly artifact:

- Symbol: XAUUSD.ecn
- Timeframe: M1
- Signal window: 2026-09-14 00:00:00 UTC through 2026-09-18 23:59:59 UTC
- Existing research configuration:
  - P-Gap = 1.0
  - Spike multiplier = 1.5
  - Max SL = 10.0
  - TP = 1.0R

The acquisition target must preserve the original research path and must not rerun optimization.

## Required evidence

For every archived signal, retain enough preceding and following M1 candles to reproduce the candidate runner's four-candle detection context and subsequent outcome scan.

Minimum fields per candle:

- timestamp as returned by MT5
- open
- high
- low
- close
- symbol
- timeframe
- acquisition method
- retrieval timestamp
- source/revision identifier

Minimum signal mapping:

- signal timestamp
- direction
- Entry
- SL
- TP
- source signal index in the candle artifact
- detection-context candle indices
- outcome scan start index
- archived outcome

## Integrity requirements

1. Do not convert terminal timestamps into a new historical timezone interpretation during acquisition.
2. Preserve raw MT5 timestamp values and separately record any display conversion.
3. Do not fill missing candles synthetically.
4. Do not substitute Twelve Data or another feed into the same artifact.
5. Do not modify the frozen research configuration.
6. Do not change signal logic while producing the evidence.
7. Record acquisition gaps explicitly.
8. Preserve the exact archived signal list so signals cannot be selected after inspecting candle data.
9. Store a content hash for the resulting artifact.
10. Record the repository revision of the acquisition script.

## What this enables

Once the artifact exists, the project can perform deterministic research diagnostics for:

- spike/body-multiplier dependency;
- candidate P-Gap measurements;
- trigger-candle relationships;
- candidate SL/swing relationships;
- outcome-path reconstruction;
- detection of which archived signals depend on specific candidate conditions.

It does **not** by itself resolve the source meaning of any unresolved rule.

## What remains prohibited

The resulting candle artifact must not be used to:

- choose a P-Gap formula because it improves results;
- choose an AB=CD anchor or tolerance;
- invent swing/pivot rules;
- define fill semantics;
- define pending-order deletion/refresh rules;
- promote a parameter;
- generate production BUY/SELL decisions;
- unlock Frozen Geometry.

AB=CD attribution specifically remains unavailable unless A/B/C/D information is independently source-confirmed or explicitly represented by the existing research implementation.

## Acquisition result status

This document is a protocol, not evidence that the candle artifact has already been acquired.

Required next execution:

1. Run the frozen MT5 acquisition.
2. Verify first/last timestamps and gap inventory.
3. Hash and archive the candle artifact.
4. Produce signal-to-candle mapping.
5. Only then run the assumption dependency analysis.

## Gate impact

- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Assumption Dependency: WAITING FOR CANDLE-LEVEL EVIDENCE
- Parameter Robustness: POSITIVE RESEARCH EVIDENCE
- Parameter Stability: INCONCLUSIVE
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Production: BLOCKED
- Live Trading: DISABLED

## Deterministic boundary

The next analysis must operate only on this frozen evidence artifact. If an expected field is absent, the correct disposition is a data-gap finding, not an inferred value.
