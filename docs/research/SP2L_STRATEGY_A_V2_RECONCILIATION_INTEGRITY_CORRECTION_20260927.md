# SP2L Strategy A V2 — Reconciliation Integrity Correction — 2026-09-27

## Finding

The first signal reconciliation used entry_time + direction deduplication inside the V2 setup collector.

Integrity audit artifact:

artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_RECONCILIATION_INTEGRITY_20260927T054525Z.json

The audit established:

- SOURCE_ALIGNED_ONLY total: 2
- Direct V2 setup detected: 2/2
- Direct V2 entry found: 2/2
- Present in the deduplicated V2 collector output: 0/2
- Entry key already present in V2 output: 2/2
- Cases likely removed by entry-key deduplication: 2/2

Therefore both prior SOURCE_ALIGNED_ONLY classifications were reconciliation artifacts. They were not evidence that the V2 detector could not detect those setups.

## Correction

Commit:

81611d5f90fbf9bbf21b4b713afb8ade9179f6c6

The reconciliation V2 collector now preserves every setup record that has a valid V2 entry.

Geometry reconciliation identity remains:

(direction, before_spike_time, spike_time, after_spike_time)

Entry-key deduplication is excluded from geometry reconciliation because it is an execution/backtest lifecycle concern.

## Scope boundary

- V2 detector rules unchanged.
- Source-aligned detector rules unchanged.
- No P-Gap interpretation changed.
- No SL anchor was selected.
- No trigger semantics were canonicalized.
- No optimization was performed.
- No production BUY/SELL decision was produced.

## Required rerun

Rerun the exact fixed-window reconciliation for 2026-09-14 through 2026-09-25 after pulling commit 81611d5f90fbf9bbf21b4b713afb8ade9179f6c6.

Only the corrected artifact should be used for subsequent forensic geometry analysis.
