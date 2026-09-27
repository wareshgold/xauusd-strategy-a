# SP2L Strategy A V2 — Signal Reconciliation Implementation Checkpoint

Date: 2026-09-27

## Purpose

Implement the deterministic signal-set reconciliation experiment required before any V2 parameter optimization or canonical promotion.

## GitHub implementation

Branch: `research/sp2l-strategy-a-v2-2026-09-27`

Latest reconciliation implementation commit: `dae8a9bd79f8c03fc079c483694cc99b4ecb3c6a`

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

## Next action

Pull the branch, compile the new reconciliation script, then run the fixed-window reconciliation. No optimization before the resulting artifact is reviewed.
