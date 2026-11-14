# MA Filter Week Export & Research

This branch stages a research-only MA filter study.

## 1. Export from the correct local MT5 terminal

Run on Factory PC using the same Python environment and exact terminal executable used by the active runner. Supply the expected account login and server as independent safety checks.

```powershell
$root = "D:\Mirzaei\Private\1\xauusd-strategy-a"
$py = "$root\.venv\Scripts\python.exe"
$terminal = "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"
& $py "$root\scripts\research\export_mt5_ma_filter_week.py" `
  --terminal $terminal `
  --symbol "XAUUSD.ecn" `
  --magic 26092301 `
  --expected-login YOUR_LOGIN `
  --expected-server "YOUR_SERVER_NAME" `
  --start-utc "2026-11-09T00:00:00Z" `
  --end-utc "2026-11-14T00:00:00Z" `
  --out "$root\artifacts\ma_filter_week_20261109"
```

Replace the two account placeholders locally; do not commit credentials or account identifiers. If runner history begins/ends at different UTC times, set the interval to the exact observed runner window. Extend M1 export with at least 250 warm-up bars before the first entry before calculating long-period MAs.

## 2. Output

- `runner_deals.csv`: deal-level broker history filtered by symbol + magic.
- `xauusd_m1.csv`: M1 bars for the requested UTC interval.
- `manifest.json`: terminal/account identity checks, row counts and SHA-256 hashes.

Do not commit raw account data to this public repository. Share the files through the intended private project/file channel for analysis.

## 3. Scope

The first pass compares actual runner outcomes with MA-filter pass/fail on the same entry population. Fixed-RR replay and ACT40/TRAIL40 replay are gated on exact source semantics; unresolved fill/SL/intrabar behavior must remain blocked, not guessed.
