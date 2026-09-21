# Live Research Journal

The live system keeps three append-only JSONL streams:

- `runtime/journal/signals.jsonl` — every approved signal observed by the gateway.
- `runtime/journal/trades.jsonl` — execution attempts and broker reconciliation facts.
- `runtime/journal/market_snapshots.jsonl` — gateway market/account snapshots.

These raw files are the audit layer. They should not be edited manually.

## Export

Run:

```powershell
python scripts/export_live_journal_xlsx.py
```

Output:

`runtime/exports/SP2L_Live_Trade_Journal.xlsx`

Sheets:
- Summary
- Signals
- Trades
- Market Snapshots

CSV export is also available:

```powershell
python scripts/live_journal.py
```

## Broker reconciliation

Run while MT5 is connected:

```powershell
python scripts/reconcile_mt5_journal.py
```

This attaches broker-side facts to journal records using the configured magic number and SP2L comment convention.

## Research discipline

The journal records observations and outcomes. It does not change Strategy A rules.

Any later strategy modification must go through the existing source-resolution, frozen-geometry, validation, robustness, and holdout gates.
