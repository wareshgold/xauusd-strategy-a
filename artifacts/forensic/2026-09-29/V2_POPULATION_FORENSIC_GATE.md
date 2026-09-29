# V2 Population Forensic Harness — 2026-09-29

## Purpose

This checkpoint isolates the population discrepancy behind the observed V2 XAUUSD MT5 result of 68.04%.

The harness:

- uses the existing V2 detector unchanged;
- uses the same MT5 `copy_rates_range()` acquisition path;
- counts every three-candle setup candidate before entry validation;
- classifies the first trigger as `VALID_ENTRY`, `INVALID_RISK`, or `NO_TRIGGER`;
- replays outcomes only for valid entries;
- emits a complete forensic ledger;
- compares the resulting populations with the previously recorded V2 reference counts.

It does **not** change Strategy A geometry and does **not** promote any rule.

## Execution

From the repository root:

~~~powershell
& ".\\.venv\\Scripts\\python.exe" .\\scripts\\run_sp2l_v2_population_forensics.py `
  --start "2026-06-28T00:00:00Z" `
  --end "2026-09-25T00:00:00Z" `
  --mt5-path "C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe"
~~~

## Reference population

Previously recorded V2 reference:

- bars: 87,673
- signals/setup population: 1,472
- trades/valid entries: 1,356
- wins: 836
- losses: 520
- win rate: 61.65191740412979%
- net R: +316R
- simplified PF: 1.6076923076923082

## Current observed run

The 2026-09-29 replay reported:

- bars: 87,881
- runner signals: 1,508
- decisive: 1,505
- wins: 1,024
- losses: 481
- win rate: 68.03986710963456%
- net R: +543R
- simplified PF: 2.128898128898129

The runner's `signals` field is not directly equivalent to the reference's `signals` field because the current runner appends a signal only after a valid first entry has been found.

## Gate

**PROMOTION GATE: BLOCKED.**

The next required evidence is the output of the population forensic harness on the same MT5 terminal/history. That output will establish whether the discrepancy begins at:

1. raw bar population/data window;
2. three-candle setup detection;
3. first-trigger detection;
4. risk validation;
5. trade outcome accounting.

No main-branch promotion is authorized by this checkpoint.

## Research boundary

A high win rate observed in a replay is an observation until deterministic population, data, geometry, and outcome parity are established. The harness is diagnostic infrastructure only and cannot make Strategy A canonical.
