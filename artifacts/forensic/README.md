# SP2L Forward vs Backtest Forensic Reproducibility

This directory is the dedicated evidence area for the XAUUSD SP2L forward/backtest mismatch investigation.

## Rule

Do not change detector geometry, session rules, fill semantics, or execution semantics to force agreement.

The investigation is split into:

1. **Signal identity** — prove that forward and backtest saw the same completed M1 trigger event.
2. **Data identity** — prove identical OHLC bars, timestamps, ordering, gaps, and window boundaries.
3. **Execution identity** — compare theoretical entry/SL/TP with broker execution separately.
4. **Outcome identity** — only evaluate WIN/LOSS after signal identity is established.
5. **Statistical validation** — only after the above are deterministic.

## Required signal classification

- EXACT_MATCH
- PRICE_MATCH_TIMESTAMP_MISMATCH
- SAME_EVENT_DIFFERENT_PRICE
- FORWARD_ONLY
- BACKTEST_ONLY
- UNRESOLVED

## Current known evidence

As of the checkpoint based on `ff08c9551d276f6cb312817ef07eabbc649f405f`:

- Forward and backtest both reported 13 signals for the investigated period.
- The 13 signal counts are **not** evidence of reproducibility.
- At least one apparent event has matching direction/entry/SL/TP but a materially different timestamp (~3 hours), so timestamp/data-window identity must be proven before outcomes are compared.
- Both paths now import the same research-only detector, so detector duplication is no longer the primary hypothesis.
- The backtest applies a research session filter; the forward runner consumes a rolling MT5 window. These acquisition paths must be reconciled.
- MT5 server-vs-UTC handling has previously been a known source of risk and must be tested from recorded evidence, not assumed.

## Evidence policy

Raw MT5/backtest artifacts should be committed under `artifacts/forensic/2026-09-26/` when available. Generated summaries must include source filenames, commit SHA, generation time, and a deterministic input fingerprint.

No result in this directory is canonical Strategy A geometry or an execution rule.
