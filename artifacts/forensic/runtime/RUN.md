# SP2L Forward Forensic Telemetry

Research-only. No orders, modifications, closes, or Telegram.

Run from repo root:

```powershell
& ".\\.venv\\Scripts\\python.exe" .\\scripts\\run_sp2l_forward_forensic_telemetry.py
```

Default duration: 900 seconds. To run one hour:

```powershell
$env:FORENSIC_DURATION_SECONDS="3600"
& ".\\.venv\\Scripts\\python.exe" .\\scripts\\run_sp2l_forward_forensic_telemetry.py
```

The JSONL output is created in `artifacts/forensic/runtime/`. Push that generated file to GitHub after the observation window so it can be reconciled with Backtest candidates.
