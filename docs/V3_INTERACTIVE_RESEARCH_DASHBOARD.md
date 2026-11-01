# V3 Interactive Research Dashboard

Research-only local workbench for replaying the existing frozen V3 Entry population against an immutable M1 artifact.

## Start on Windows PowerShell

Configure only the directories that contain the source artifacts you intend to expose to the local dashboard:

```powershell
$env:SP2L_V3_RESEARCH_DATA_ROOTS = "D:\Mirzaei\Private\1\sp2l-mt5-market-data;D:\Mirzaei\Private\1\sp2l-evidence"
$env:SP2L_V3_RESEARCH_PORT = "8791"
python scripts/run_v3_research_dashboard.py
```

Open `http://127.0.0.1:8791/`. The server binds to loopback only. Stop it with Ctrl+C.

The catalog scans configured roots to a bounded depth and exposes eligible files:
- M1 artifact: JSON with embedded identity metadata, or CSV using the existing validated M1 CSV schema (filename must contain `m1` or `ohlc`).
- Frozen entry population: CSV whose filename contains `entr`, `population`, or `candidate`.

## Session setup

Choose the M1 artifact and frozen Entry CSV. Enter the declared symbol, inclusive UTC start/end window, MT5 point, contract size, volume, and engine revision. The service calculates SHA-256 from the exact selected file bytes and creates a provenance-bound session. M1 validation reports missing-minute gaps; it does not fill or classify them.

**CSV provenance limitation:** the current M1 CSV schema contains no embedded symbol or declared-window metadata. When CSV is selected, the symbol and window are caller assertions, not independently verified source metadata. The session manifest explicitly records this as `CALLER_ASSERTED_CSV_IDENTITY_NO_EMBEDDED_SYMBOL_OR_WINDOW` and `symbol_identity_verified=false`. Prefer the JSON artifact when embedded identity metadata is available.

## Replay and interpretation

The UI exposes only V3 exit parameters currently supported by the extracted engine: target RR, trailing activation points, and trailing distance points. It does not change the frozen Entry population. M1 OHLC replay retains the existing ambiguity rules: M1 gaps while open and same-bar SL/TP are unresolved; completed-bar trailing changes apply to the next bar. No spread, slippage, commission, tick-fill, or broker execution semantics are inferred.

Session and variant handles live only in process memory and disappear when the server stops. The dashboard does not write source files or persist experiments. Tick replay, filters/EMA, persistent experiment storage, validation promotion, and production execution are not implemented.

All responses are marked research-only, non-canonical, and not validated. No BUY/SELL signal generation is provided.


## Trade-management experiments

The dashboard also exposes a first-stage management experiment panel. It replays `FIXED_RR`, `NO_TARGET`, `BREAK_EVEN`, `TRAILING_R`, `BREAK_EVEN_TRAILING`, and `TIME_EXIT` modes over the same frozen entries. Results can be compared pairwise with the existing comparison control, including net/gross USD at the session's declared volume and contract size.

See [V3 Trade-Management Experiment Matrix](V3_TRADE_MANAGEMENT_MATRIX.md) for the supported parameter contract and explicit exclusions. Partial exits, scale-outs, ATR trailing, spread, commission, slippage, and broker fills remain unsupported; no cost is silently assumed or deducted.
