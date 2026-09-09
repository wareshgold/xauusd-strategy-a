# SP2L G49 — Historical Coverage Contract

Date: 2026-09-09

## Objective
Prepare deterministic, strategy-neutral multi-window historical coverage acquisition for later research.

## Rules
- Explicit chronological windows.
- Windows contiguous and non-overlapping.
- Each request records provider, symbol, interval, bounds, source timezone, and retrieval provenance.
- Raw responses immutable and separately fingerprinted.
- Normalized UTC candles separately fingerprinted.
- Missing bars, duplicates, cadence anomalies, and OHLC violations measured; no fabrication.
- Provider feeds remain separate; no feed selected by backtest performance.
- DEV, VAL, and FRESH_HOLDOUT boundaries chronological and fixed before Strategy A validation.
- No Strategy A geometry, BUY/SELL detection, optimization, or profitability claim.

## Gate
Planning is not a PASS. G49 becomes PASS only after historical windows are actually acquired, audited, fingerprinted, and coverage-checked.
