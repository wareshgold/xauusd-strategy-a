# SP2L Strategy A V2 Reconciliation Forensics — 2026-09-27

## Purpose

This checkpoint records the next research step after the first deterministic
signal reconciliation. The purpose is to decompose the non-common cases at
rule level without changing any Strategy A geometry.

## Fixed reconciliation evidence

Artifact:

`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_SIGNAL_RECONCILIATION_20260927T053636Z.json`

Results:

- V2: 136
- Source-aligned: 53
- Common setup: 51
- V2-only: 85
- Source-aligned-only: 2
- Common trigger time identical: 51/51
- Common entry identical: 51/51
- Common SL identical: 0/51

## Rule-level evidence already established

For the 51 common setups, trigger timestamp and entry price agree exactly,
while the SL anchor differs for every case.

The current research implementations use different SL anchors:

- V2: Low/High of the candle before Spike.
- Source-aligned detector: Low/High of the Spike candle.

The official source description does not resolve the exact wick/body/open/close
boundary sufficiently to make either implementation canonical.

The source-aligned detector also requires the Spike body to exceed 1.5x the
Trigger candle body. V2 does not apply this Trigger-body comparison during its
three-candle setup test.

## New forensic tool

`scripts/run_sp2l_strategy_a_v2_reconciliation_forensics.py`

The tool:

1. Reuses the same MT5 M1 history and research session window.
2. Loads the fixed reconciliation artifact.
3. Diagnoses representative V2-only cases against the immediate Trigger candle
   using the existing source-aligned conditions.
4. Counts failed source-aligned conditions.
5. Inspects both Source-aligned-only cases against the V2 entry/SL construction.
6. Writes a deterministic JSON artifact.

## Interpretation boundary

This checkpoint does **not** choose between the competing SL anchors,
Trigger-body requirements, or other unresolved source semantics.

No optimization, parameter selection, canonical promotion, or production
BUY/SELL decision is permitted from this diagnostic.

## Next gate

Run the forensic tool, inspect the failed-condition distribution and the two
Source-aligned-only cases, then register the evidence before deciding whether
any additional source resolution is required.

Forward-test readiness remains a later gate. The market opening does not change
the research/source hierarchy.


## Reconciliation integrity correction

The first artifact at 20260927T053636Z contained an entry-key deduplication defect. The integrity audit at 20260927T054525Z showed both SOURCE_ALIGNED_ONLY cases were directly detectable by V2 and were removed by `(entry_time, direction)` deduplication. Therefore that artifact is superseded for geometry conclusions.

The reconciliation collector was corrected in commit `81611d5f90fbf9bbf21b4b713afb8ade9179f6c6` to preserve every setup with a valid V2 entry. A new fixed-window reconciliation must be generated before further forensic interpretation.
