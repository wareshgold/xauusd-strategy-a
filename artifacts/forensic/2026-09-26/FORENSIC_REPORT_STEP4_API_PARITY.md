# Historical API Parity Forensic — Step 4 — 2026-09-26

## Objective

Compare the two MT5 historical acquisition APIs from the same terminal:

- `mt5.copy_rates_range()`
- `mt5.copy_rates_from()`

for the three unresolved 2026-09-24 Forward windows.

## Windows

1. 09:55–10:20 UTC
2. 11:40–12:10 UTC
3. 12:30–13:00 UTC

These deliberately surround the previously unresolved 10:07, 11:55 and 12:45 candidate times.

## Gate

The parity runner is manifest-gated and uses detector revision `AR-20260926-01` with the current research candidate parameters.

## Interpretation rules

- Exact equality of raw time/OHLC sequences is evidence of API parity for that observed window.
- Inequality is evidence of an acquisition-path difference for that observed window, but does not by itself prove that the historical Forward loop was alive, nor does it establish timezone semantics.
- No timestamp normalization is performed.
- No SP2L geometry, P-Gap formula, SL boundary, fill semantics, or execution rule is changed.

## Execution

Run on the Windows machine connected to the same MT5 terminal:

```powershell
& ".\.venv\Scripts\python.exe" .\scripts\run_sp2l_historical_api_parity_forensics.py
```

The resulting JSON is the required evidence artifact for Step 4.
