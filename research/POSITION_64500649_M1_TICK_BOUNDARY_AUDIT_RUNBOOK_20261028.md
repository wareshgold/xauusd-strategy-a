# Position 64500649 — offline M1/tick boundary audit

Research-only helper for comparing the supplied tick text with an existing MT5 M1 OHLC CSV. It does not connect to MT5, alter runner files, modify evidence, or place orders.

## Local invocation (PowerShell)

Run from the Strategy A repository root. Replace only the two input paths with the actual local paths; the defaults encode the recorded entry/exit timestamps.

```powershell
$py = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
$ticks = "C:\PATH\TO\Pasted text(20261028-050455).txt"
$m1 = "D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv"
$out = "artifacts\research-audits\position_64500649_m1_tick_boundary_audit.json"
& $py scripts\audit_position_m1_tick_boundaries.py --ticks $ticks --m1 $m1 --output $out 2>&1 | Tee-Object -Variable auditOutput | Out-String | Set-Clipboard
$auditOutput
```

The command copies the concise console report to the clipboard while also displaying it. The JSON report is written to a new, separate output path. If that output file already exists, choose a new filename rather than overwriting prior evidence. **Important:** the M1 CSV must actually contain bars for 2026-10-27 12:55–13:02 UTC. The previously identified acquisition folder dated 2026-10-24 may be stale; do not use it unless its timestamp coverage includes this incident. The script fails closed if no bars are found in the incident window.

## Interpretation rules

- Treat timestamps as UTC only when the input CSV uses Unix epoch seconds or explicitly offset-bearing ISO-8601 timestamps.
- A minute marked `NO_TICKS_IN_SUPPLIED_FILE` means the supplied tick dump does not cover it; it does not mean no market ticks occurred.
- M1 OHLC alone cannot prove whether an extreme happened before or after the entry timestamp within the entry minute.
- The known tick dump has 1,139 rows and reports a minimum post-entry Bid of 4006.06 at 12:56:06.140 UTC, a 0.05 favorable move from the reported SELL entry of 4006.11. The 0.40 activation threshold was not reached in that supplied tick sample.
- This is an incident-specific diagnostic, not a canonical Strategy A rule or evidence of strategy-wide performance.
