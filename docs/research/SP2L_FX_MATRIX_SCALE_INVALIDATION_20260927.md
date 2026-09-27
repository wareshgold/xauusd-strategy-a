# SP2L FX Matrix Scale Invalidation — 2026-09-27

## Status

Research-only finding. The one-month MT5 FX parameter matrix artifact
`SP2L_MT5_FX_MATRIX_20260927T115710Z` executed successfully for 7 FX majors,
189 rows, and 0 runtime errors, but it is **not valid evidence of FX strategy
performance**.

## Reason

The matrix reused XAUUSD-style absolute price-unit P-Gap values (0.5, 1.0, 1.5)
across FX symbols. Those values are not source-confirmed to be the correct
cross-symbol unit for P-Gap. On FX pairs this produces a scale mismatch and the
observed matrix contains no usable signal population.

This does not establish that the source P-Gap is pip-based, point-based,
percentage-based, or volatility-normalized. No such interpretation is promoted
to canonical geometry.

## Preserved artifact

- Matrix commit: `4dc17ee`
- Period: 2026-08-26 through 2026-09-25 UTC
- Timeframe: M1
- Symbols: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD
- Rows: 189
- Errors: 0

The artifact remains preserved as a negative/invalid experimental checkpoint;
it must not be used to claim that SP2L has no FX signals or no FX edge.

## Forward-test alignment work

The research forward runner was also corrected to separate setup detection from
the subsequent trigger. The forward detector now mirrors the V2 reference
geometry for the completed 3-candle setup and uses the first later lower-low /
higher-high trigger, while keeping research-only pending execution semantics
separate.

This change does **not** declare pending-order fill semantics canonical and
does not promote the runner to production.

## Next research step

A new FX sensitivity experiment must first define an explicitly documented,
source-neutral scale transformation for P-Gap. If the source cannot resolve the
unit, each transformation remains a research hypothesis and cannot become
canonical solely because it improves backtest performance.
