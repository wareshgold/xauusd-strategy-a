# V3.1 local forward forensic (read-only)

This utility analyzes the private forward-evidence ZIP on the operator's PC.
It does not connect to MT5, inspect a live terminal, modify runner files/state,
cancel orders, alter SL/TP, or make BUY/SELL decisions.

## Run in Windows PowerShell

\`\`\`powershell
$py = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
$zip = Join-Path $HOME "SP2L_PRIVATE_AUDIT_20261102_20261107.zip"
$out = "artifacts\forensic\v31-local-20261108"

& $py scripts\sp2l_v31_forward_forensic.py --zip $zip --out $out 2>&1 |
    Tee-Object -Variable result
$result | Set-Clipboard
Write-Host "Compact report copied to Clipboard. Full reports: $out"
\`\`\`

Only the compact summary is copied. The ZIP, broker histories, event log and
detailed per-position CSV remain local.

## Outputs

- v31_forward_forensic_report.json: capture identity, hashes, manifest checks,
  realized closed-position statistics, exit reasons, trailing counts, limits.
- v31_closed_positions.csv: one row per broker position ID, joined to deals
  and V3.1 trailing events.

## Interpretation boundaries

- Realized P&L totals include only positions with at least one observed entry
  deal and one observed exit deal. Exit-only histories are flagged separately.
- Net sums broker deal profit + commission + swap + fee where present, in
  account currency.
- Broker-reported exit reason is descriptive evidence, not proof of causation.
- MFE/MAE requires synchronized price bars/ticks and is not inferred here.
- V3 vs V3.1 same-entry comparison requires frozen identical entries and a
  separately validated replay. No P-Gap, AB=CD, fill or SL-anchor semantics
  are invented.
- Unrecognized manifest formats are reported as unparsed, never verified.
