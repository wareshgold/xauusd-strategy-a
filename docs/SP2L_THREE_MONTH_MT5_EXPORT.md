# SP2L Three-Month MT5 Historical Export — Stage 1

Status: research-only acquisition utility. No trade-management engine is run by this stage.

## Safety contract

- Connects to the already-running MetaTrader 5 terminal through the Python API.
- Reads terminal metadata, the exact symbol specification, Tick ALL and M1 history.
- Does **not** call `symbol_select`, send orders, read or modify positions, inspect Runner event files, or stop/restart the terminal.
- Calls `mt5.shutdown()` only to release this Python API connection; it does not close the terminal.
- Does not record account login or credentials.
- If the symbol is unavailable through `symbol_info`, it fails closed and asks the operator to verify the exact symbol in Market Watch. It will not silently change Market Watch.

Run from the repository root using the project's Python 3.12 environment:

```powershell
Set-Location D:\Mirzaei\Private\1\xauusd-strategy-a
.\.venv\Scripts\python.exe .\scripts\acquire_sp2l_three_month_mt5_data.py `
  --symbol XAUUSD.ecn `
  --start-utc 2026-08-09T00:00:00Z `
  --end-utc 2026-11-10T00:00:00Z `
  --out-dir D:\SP2L_RESEARCH_DATA\20261109
```

The interval is UTC and half-open: start included, end excluded. The chosen end includes all of 2026-11-09. This is a requested window, not a claim that MT5 has complete history for it. The exporter streams rows to disk in daily chunks rather than retaining the three-month Tick corpus in memory. It refuses to overwrite existing output files; use a new output directory for each acquisition attempt.

## Synthetic tests\n\nRun without connecting to MT5:\n\n\`\`\`powershell\n& .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p test_mt5_research_exporter.py -v\n\`\`\`\n\nThe tests cover UTC parsing, same-millisecond Tick handling, crossed quotes, M1 gap reporting, symbol-spec extraction, streaming gzip output, and no-overwrite behavior. They do not validate MT5 connectivity or broker history availability.\n\n## Outputs

- `*_ticks.csv.gz`: raw Tick ALL records, including Bid, Ask, Last, Volume and flags.
- `*_M1.csv.gz`: raw M1 bars with OHLC, tick volume, spread points and real volume.
- `*_symbol_specs.json`: current terminal symbol properties, not a historical specification archive.
- `*_acquisition_manifest.json`: requested interval, observed coverage, per-artifact SHA-256, quality counters and safety assertions.
- `*_SHA256SUMS.txt`: hashes for exported artifacts and manifest.

Daily chunks are queried in UTC. Provider order is preserved. No sorting, deduplication, interpolation, gap filling, or silent exclusion is performed. Tick observations sharing the same millisecond are retained and counted separately from decreasing timestamps. M1 interval gaps are reported but are not automatically called missing bars because market closures and session schedules must be classified independently.

## Important interpretation limits

1. MT5 epoch timestamps are rendered as UTC. This does not prove historical broker-server UTC offset or DST behavior.
2. The symbol specification is the current terminal response; historical contract/tick specifications may have changed.
3. M1 `spread_points` is not a substitute for historical tick Bid/Ask.
4. A zero-length result or incomplete interval is evidence of unavailable history, not permission to fabricate coverage.
5. The export is an input snapshot only. It does not generate entries, fills, P/L, BUY/SELL decisions, or canonical Strategy A rules.

## First-stage acceptance gate

Do not start the management matrix until the operator returns the manifest summary and we verify:

- actual first/last tick and M1 timestamps;
- row counts and SHA-256;
- out-of-order timestamps, same-millisecond ticks, crossed/missing quotes;
- M1 OHLC errors and interval gaps;
- symbol identity, point, tick size/value, contract size, volume limits, stop/freeze levels;
- whether the requested three-month coverage is actually present.

A later historical-entry freeze must be separately source-audited. This exporter does not resolve entry geometry, the two entry points, system-SL semantics, pending-order fill semantics, commission, or slippage.
