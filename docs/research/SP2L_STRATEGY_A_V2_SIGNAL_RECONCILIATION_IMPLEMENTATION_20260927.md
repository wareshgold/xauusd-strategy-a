# SP2L Strategy A V2 — Signal Reconciliation Implementation Checkpoint

Date: 2026-09-27

## Purpose

Implement the deterministic signal-set reconciliation experiment required before any V2 parameter optimization or canonical promotion.

## GitHub implementation

Branch: `research/sp2l-strategy-a-v2-2026-09-27`

Latest reconciliation implementation fix commit: `81611d5f90fbf9bbf21b4b713afb8ade9179f6c6`

Tool:

`scripts/run_sp2l_strategy_a_v2_signal_reconciliation.py`

## Fixed comparison

The tool uses the same MT5 M1 history and compares:

- V2 research detector
- Existing source-aligned research detector
- P-Gap research threshold = 1.0 price unit
- Spike multiplier = 1.5
- Max SL distance = 10.0
- TP = 1R
- prior source-aligned research session window: London open -> New York close
- contiguous M1 segments are isolated so session/weekend/data gaps cannot become synthetic adjacent candles

## Matching rule

A COMMON setup requires:

- same direction
- identical before-spike timestamp
- identical spike timestamp
- identical after-spike timestamp

For COMMON setups the artifact separately compares:

- trigger/entry timestamp
- entry price
- SL
- risk
- TP

Non-common signals are classified as V2_ONLY or SOURCE_ALIGNED_ONLY.

## Evidence boundary

This experiment explains detector-level signal divergence. It does not decide which geometry is canonical, does not optimize parameters, and does not emit production BUY/SELL decisions.

The P-Gap threshold and session filter remain research-only.

## Integrity correction

The first reconciliation implementation deduplicated V2 records by `(entry_time, direction)`. The 2026-09-27 integrity audit proved that both prior SOURCE_ALIGNED_ONLY cases were directly detectable by V2 and had valid V2 entries, but were removed by that deduplication. This was a reconciliation-methodology defect, not evidence of geometry divergence.

The fix preserves every V2 setup in the reconciliation set. The existing V2 detector and execution/backtest behavior are unchanged.

## Next action

Pull the branch, compile the reconciliation script, rerun the fixed window, then inspect the new counts and common-case SL/trigger differences. No optimization before the resulting artifact is reviewed.
