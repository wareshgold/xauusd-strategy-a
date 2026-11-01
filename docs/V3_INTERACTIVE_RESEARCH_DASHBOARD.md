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

The UI supports both the original V3 RR/trailing replay and a deterministic trade-management policy matrix over the same frozen Entry population. Policies include fixed RR targets (1R, 1.5R, 2R, 3R), no fixed target, break-even triggers, trailing activation in R with distance in MT5 points, break-even plus trailing, and completed-M1-bar time exits. Each result retains the same session fingerprint and frozen trade identities; variants can be compared pairwise. The batch endpoint accepts at most 50 policies.

Management semantics are explicit research proxies: a break-even or trailing stop update derived from a completed bar applies only to the next bar; same-bar SL/TP and M1 gaps remain ambiguous; time exits use the completed bar close as a theoretical OHLC proxy. No spread, slippage, commission, tick-fill, partial-close, ATR, or broker execution semantics are inferred. Partial exits and ATR trailing are intentionally excluded pending separately specified execution/anchor semantics.

Session and variant handles live only in process memory and disappear when the server stops. The dashboard does not write source files or persist experiments. Tick replay, filters/EMA, persistent experiment storage, validation promotion, and production execution are not implemented. Management variants are exploratory only and remain NOT_VALIDATED; the matrix does not rank or promote a canonical winner.

All responses are marked research-only, non-canonical, and not validated. No BUY/SELL signal generation is provided.
