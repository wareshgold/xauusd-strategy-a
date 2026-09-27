# SP2L V2 — 222 vs 227 Baseline Reconciliation Gate — 2026-09-27

Status: RESEARCH FORENSICS — NOT CANONICAL

## Finding

The 2026-09-27 05:22Z reference result (222 signals / 204 decisive / 127W / 77L / +50R) used the V2 runner at commit a836ed0 and the V2 detector blob 3cb93ad5cfb5b743213e8bceb1db2e440b57086a.

The later dedicated source-baseline runner produced 227 signals / 220 decisive / 124W / 96L / +28R on the same requested window.

The code comparison identifies two concrete contract differences that can explain the aggregate-count divergence without changing detector geometry:

1. Signal population de-duplication
   - Reference V2 runner build_signals() suppresses multiple signals sharing the same entry_index.
   - Dedicated baseline runner does not apply that entry_index de-duplication.
   - Therefore the +5 signal difference is directly testable as duplicate-entry population.

2. Trade lifecycle / overlap handling
   - Reference V2 runner runs a single active trade at a time. While a trade is active, later signal entries are not activated.
   - Dedicated baseline evaluates every signal independently with its own pending-fill lifecycle.
   - Therefore the decisive-count difference can arise even when the underlying setup/trigger signal population is the same.

## Additional outcome difference

Reference V2:
- no pending-fill stage; entry signal becomes an active trade at its entry index;
- trigger/entry candle is not also used as an exit candle;
- same-bar SL+TP is resolved SL-first;
- an unfinished final trade is marked to market at end of data.

Dedicated baseline:
- entry is theoretical pending-limit;
- trigger candle cannot fill;
- later candle must touch entry;
- same-bar SL+TP is AMBIGUOUS;
- no-fill is retained separately;
- no independent single-active-trade restriction.

These are outcome-contract differences, not evidence that either contract is canonical.

## Deterministic next test

Do NOT modify geometry.

Re-run the exact reference runner at commit a836ed0 against the connected MT5 terminal for:
2026-09-14T00:00:00Z through 2026-09-25T23:59:59Z
requested symbol XAUUSD, resolved symbol expected XAUUSD.ecn.

The command must explicitly provide the MT5 terminal path.

Then preserve the generated JSON and compare its full signal/trade ledger against the 222 reference checkpoint and the 227 dedicated baseline.

## Gate

Until the reproduced reference ledger is obtained:
- 222 remains a preserved reference checkpoint, not independently reproduced;
- 227 remains a separate controlled baseline;
- neither result is canonical;
- no performance-based geometry change is permitted.

## Repository evidence

Reference runner commit:
a836ed038ae84a401b32dfc27690ddb04044de01

Reference provenance:
docs/research/SP2L_V2_20260927_0522_RUN_PROVENANCE.md

Dedicated baseline runner:
scripts/run_sp2l_mt5_source_baseline_v2.py

Existing ledger tool:
scripts/run_sp2l_signal_ledger_forensics.py

The ledger tool must use multiplicity-preserving matching before a final parity verdict.
