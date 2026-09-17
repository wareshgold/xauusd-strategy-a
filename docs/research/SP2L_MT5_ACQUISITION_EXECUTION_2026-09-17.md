# SP2L MT5 Acquisition Execution — 2026-09-17

## Purpose

Turn the existing local Python → MT5 terminal connection into a reproducible historical acquisition step. This is data acquisition and provenance only; it does not define or alter Strategy A geometry or execution semantics.

## Command

From the repository root on the machine that has the local MT5 terminal and Python `MetaTrader5` package:

```bash
python scripts/mt5_acquire_xauusd_m1.py --dataset-id xauusd-ecn-m1-april-2026 --start 2026-04-01T00:00:00Z --end 2026-05-01T00:00:00Z --out-dir data/mt5-acquisition
```

Repeat for May and June with non-overlapping intervals. The command requests bars directly from the local MT5 terminal using `copy_rates_range` for `XAUUSD.ecn` / `M1`.

## Required output

The command creates:

- `<dataset-id>.csv` — exact returned bars, UTC-normalized;
- `<dataset-id>.manifest.json` — provenance, continuity audit, and SHA-256.

The manifest may only report `AUDITED_PASS` when the returned rows are chronologically ordered, have no M1 gaps, contain valid OHLC values, and required provenance/hash fields are present.

No missing candles are fabricated. A failed audit exits non-zero and must not be promoted into stability results.

## Important interpretation rule

`AUDITED_PASS` means the acquired artifact passed the defined data-quality/provenance gate. It does **not** mean Strategy A is validated, profitable, canonical, or production-ready.

## Expected environment

- local MT5 terminal available and initialized;
- server expected: `OtetGroup-MT5`;
- symbol: `XAUUSD.ecn`;
- timeframe: `M1`;
- Python package: `MetaTrader5`.

If MT5 returns no history, a zero-bar result, a different server, or a continuity failure, record the blocker rather than substituting another provider or symbol.
