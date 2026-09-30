# SP2L Strategy A — Research Snapshot
Date: 2026-09-30
Branch: `research/sp2l-legacy-mirror-backtest-20260929`
Snapshot commit: `f49b1c718b06eb9e4c1f6bca24ab27dafd62feaf`
Previous baseline-fix commit: `d9f9da937008cc163aefec24af0b102a442be9f4`

## Active Forward
Do not disturb the active V2 XAUUSD Forward in PowerShell 1.

Reference runner:
`scripts/run_sp2l_strategy_a_v2_forward_test_20260929.py`

Current V2 reference parameters:
- pGap: 1.0
- spike multiplier: 1.5
- max SL: 10.0
- TP: 1R
- entry mode: PENDING_LIMIT_RESEARCH
- initial SL: SPIKE_CANDLE_EXTREME_RESEARCH
- session filter: OFF / V2_REFERENCE_NO_SESSION_FILTER
- canonical: false / research demo

## Exact 3-month reference population
Artifact requested locally:
`artifacts/forensic/2026-09-30/V2_3MONTH_EXACT_FORWARD_BASELINE_TRAILING_USD.json`

Command used:
```powershell
& ".\.venv\Scripts\python.exe" `
  ".\scripts\run_sp2l_v2_xauusd_3month_rr_trailing_matrix.py" `
  --start "2026-06-28T00:00:00Z" `
  --end "2026-09-25T00:00:00Z" `
  --rr 1 `
  --trail-pips 0 10 20 30 50 `
  --mt5-path "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe" `
  --volume 0.01 `
  --output ".\artifacts\forensic\2026-09-30\V2_3MONTH_EXACT_FORWARD_BASELINE_TRAILING_USD.json"
```

Population:
- XAUUSD.ecn
- 87,881 M1 bars
- 1,508 signals
- RR=1
- 0 pip means explicit trailing OFF

## Frozen research result recorded before transition audit

| Variant | Decisive | W | L | BE | Ambiguous | WR | Net R | Net USD | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| OFF | 1505 | 1024 | 481 | 0 | 3 | 68.0399% | +543.0000R | $1,590.25 | 9R |
| 10p | 1450 | 1431 | 17 | 2 | 58 | 98.6897% | +657.9204R | $2,200.59 | 2R |
| 20p | 1474 | 1310 | 161 | 3 | 34 | 88.8738% | +602.9421R | $1,953.15 | 4R |
| 30p | 1497 | 1188 | 308 | 1 | 11 | 79.3587% | +580.9725R | $1,823.63 | 8R |
| 50p | 1505 | 1063 | 442 | 0 | 3 | 70.6312% | +552.4471R | $1,666.01 | 9R |

Accounting:
- volume = 0.01 lot
- USD formula = R × abs(entry − initial SL) × broker contract size × volume
- OFF reproduces the exact V2 Forward reference population/result: 1,508 signals / 1,505 decisive / 68.0399% WR / +543R.

## Next analysis
New script committed:
`scripts/audit_v2_trailing_transition_matrix.py`

Purpose:
Compare OFF against 10/20/30/50 pip trailing by exact signal identity and report:
- WIN→WIN
- LOSS→WIN
- WIN→LOSS
- LOSS→LOSS
- WIN/LOSS→BREAKEVEN
- transitions involving AMBIGUOUS or OPEN_OR_UNRESOLVED
- R delta per transition
- USD delta per transition
- population identity mismatches

This transition audit is NON_CANONICAL_FORENSIC only. It does not promote trailing to Strategy A and does not rank variants.

## Source-alignment guard
- Current Strategy A Forward remains RR=1.
- Trailing is not source-confirmed and remains research-only.
- No canonical P-Gap, fill semantics, or trailing rule is inferred from performance.
- Source meaning outranks backtest performance.
