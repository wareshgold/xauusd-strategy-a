# SP2L G285 — Target Fixture Provenance Correction

Date: 2026-09-12
Status: CORRECTIVE / RESEARCH-ONLY

## Finding

The earlier G251 target-reference fixture encoded TP1 and TP2 as exact one-R and two-R calculations. That encoding was stronger than the current source evidence permits.

## Correction

The fixture has been revised so that the source schematic is represented only as an ordered bullish relationship:

`SL < Entry < TP1 < TP2`

No exact distance equation is encoded.

## Why

The source visual strongly suggests successive target intervals, but visual spacing alone does not establish that the intervals are numerically identical to Entry-to-SL risk, nor does it establish point units or terminal target selection.

## Safety boundary

The fixture remains research-only. It cannot authorize:

- TP1 = 1R;
- TP2 = 2R;
- 250/500 point mapping;
- Round Level selection;
- terminal TP selection;
- SELL mirroring.

`FIXTURE_PROVENANCE = CORRECTED`
`CANONICAL_TARGET_ENGINE = NOT_AUTHORIZED`
