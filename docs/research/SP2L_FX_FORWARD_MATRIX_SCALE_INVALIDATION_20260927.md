# SP2L FX Forward Matrix — Scale Invalidation Checkpoint

Date: 2026-09-27  
Branch: research/sp2l-strategy-a-v2-2026-09-27

## Purpose

Record the one-month major-FX Historical Forward Matrix as a negative research checkpoint so the same invalid experiment is not repeated.

## Experiment

Window: 2026-08-26T00:00:00Z .. 2026-09-25T23:59:59Z  
Timeframe: M1  
Mode: HISTORICAL_FORWARD_FX_MATRIX_RESEARCH  
Symbols: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD

Inherited XAUUSD Forward configuration:

- P-Gap = 1.0 absolute price unit
- Spike multiplier = 1.5
- Max SL distance = 10.0
- TP = 1R
- Pending TTL = 30 minutes
- Forward-style M1 fill/exit model

## Observed result

All 7 symbols resolved successfully and all downloaded approximately 33k M1 bars, with zero runner errors.

However:

- candidate_keys_seen = 0 for every symbol
- filled = 0 for every symbol
- netR = 0 for every symbol

Therefore this experiment produced no usable FX trade population.

## Interpretation

This does NOT establish that SP2L has no FX edge and does NOT establish that one FX symbol is better or worse than another.

It establishes only that the XAUUSD absolute P-Gap scale of 1.0 was not a valid basis for this FX experiment.

The FX P-Gap scale/geometry remains unresolved. No pip-, percentage-, ATR-, or other normalization is promoted or inferred from this result.

## Canonical status

Research-only negative checkpoint. No canonical Strategy A rule changed.

## Reuse rule

Do not use this artifact for FX performance ranking. Before another FX matrix, independently resolve the source-defined P-Gap scale/geometry for FX. Only source-confirmed rules may enter a subsequent matrix.

Artifact:
artifacts/forward-test-fx-matrix/SP2L_HISTORICAL_FORWARD_FX_MATRIX_20260927T123726Z.json
