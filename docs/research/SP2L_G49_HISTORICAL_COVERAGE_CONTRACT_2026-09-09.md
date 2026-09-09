# SP2L G49 — Historical Coverage Contract

Date: 2026-09-09

## Objective

Prepare a deterministic, strategy-neutral multi-window historical dataset acquisition plan for later research.

## Rules

- Use explicit chronological date windows.
- Windows must be contiguous and non-overlapping.
- Each acquisition request records provider, symbol, interval, bounds, source timezone, and retrieval provenance.
- Raw responses remain immutable and separately fingerprinted.
- Normalized UTC candles are separately fingerprinted.
- Missing bars, duplicates, cadence anomalies, and OHLC violations are measured; bars are never fabricated.
- Provider feeds remain separate; no feed is selected because it improves backtest performance.
- DEV, VAL, and FRESH_HOLDOUT boundaries are chronological and fixed before Strategy A validation.
- No Strategy A geometry, BUY/SELL detection, optimization, or profitability claim is introduced by G49.

## Current boundary

G48 demonstrated one real 5,000-row Twelve Data sample can pass the quality pipeline. G49 extends the infrastructure to reproducible historical coverage planning. Actual long-range acquisition remains a separate execution step and must produce its own manifests and quality results.

## Gate

G49 can only be marked PASS after the planned historical windows are actually acquired, audited, fingerprinted, and shown to satisfy the coverage contract. Planning alone is not a data-quality PASS.
