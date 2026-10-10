# XAUUSD Tick Bid/Ask acquisition — Factory

## Purpose and safety

`scripts/acquire_xauusd_tick_bidask.py` downloads research-only MT5 `COPY_TICKS_ALL` data for the configured broker symbol, writes compressed CSV plus a SHA-256 sidecar manifest, and does not place or manage orders. It is independent of the RR2/TRAIL4 forward runner.

## Known data inventory

The branch currently contains historical M1 OHLC artifacts and manifests, but no checked-in raw Tick Bid/Ask dataset or tick artifact hash was found. Existing M1 manifests record missing timestamps/gaps, so they cannot substitute for a complete tick stream.

## First requested development acquisition

Use the historical development window already represented by the repository's M1 evidence:
- Symbol: `XAUUSD.ecn`
- Provider/server: Otet Group MT5 / `OtetGroup-MT5`
- Start inclusive: `2026-08-21T00:00:00Z`
- End exclusive: `2026-09-19T00:00:00Z`
- Fresh Holdout boundary: `2026-09-19` — do not include or inspect it for candidate tuning.
- Data: all MT5 ticks, retaining millisecond time, Bid, Ask, Last, Volume, and flags.
- Output: local ignored path `data/raw/ticks/xauusd-ecn-ticks-20260821_20260919.csv.gz` and sidecar `xauusd-ecn-ticks-20260821_20260919.manifest.json`.

The acquisition writes to `data/raw/`, which is ignored by Git; raw market data should not be committed by default. The manifest records artifact SHA-256, byte size, count, interval, first/last tick, Bid/Ask quality counts, and retrieval metadata. Review the manifest before registering the dataset in Factory.

## Run on the MT5 host

From the repository root, in the same Python environment that has the `MetaTrader5` package and access to the intended terminal:

```powershell
..venvScriptspython.exe .\scripts\acquire_xauusd_tick_bidask.py `
  --start "2026-08-21T00:00:00Z" `
  --end "2026-09-19T00:00:00Z" `
  --symbol "XAUUSD.ecn" `
  --terminal-path "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe" `
  --output ".\data\raw\ticks\xauusd-ecn-ticks-20260821_20260919.csv.gz"
```

If the terminal does not have the requested history cached/available, the script may return a small or empty dataset. `ACQUIRED` only means there are ticks and some valid non-crossed Bid/Ask quotes; it does not certify completeness. Review:
- `tick_count`, first/last timestamps and requested interval;
- `valid_non_crossed_bidask_tick_count`, missing/crossed quote counts;
- duplicate/out-of-order millisecond timestamp count;
- broker session closures, holidays, and gaps;
- `artifact_sha256` and `artifact_size_bytes`.

Do not interpolate ticks, fill missing periods, or infer quotes. If the requested range is unavailable, report the exact actual interval and gaps, then reacquire a clearly delimited range. Do not silently switch to OHLC and call it exact parity.

## Current blocker

This environment cannot access the user's local MT5 terminal/history. Therefore the raw dataset and its SHA-256 cannot be truthfully claimed as acquired yet. Run the command above on the MT5 host and provide the generated manifest (and the compressed file if available) to continue with integrity checks and adapter fixtures.
