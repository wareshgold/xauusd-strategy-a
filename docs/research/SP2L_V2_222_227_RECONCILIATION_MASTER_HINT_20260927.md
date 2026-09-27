# SP2L V2 — 222 vs 227 Reconciliation Master Hint

## PURPOSE / FUTURE SEARCH HINT

If the repository becomes difficult to navigate, search these exact tokens first:

- `222_227_RECONCILIATION_MASTER_HINT`
- `REPRODUCED_222`
- `227_BASELINE`
- `multiplicity_preserving`
- `a836ed038ae84a401b32dfc27690ddb04044de01`
- `3cb93ad5cfb5b743213e8bceb1db2e440b57086a`
- `SP2L_V2_222_VS_227_RECONCILIATION_GATE_20260927`

## IMMUTABLE RESEARCH CHECKPOINTS

### Reproduced 222 reference

Window: 2026-09-14T00:00:00Z .. 2026-09-25T23:59:59Z  
Symbol: requested XAUUSD, resolved XAUUSD.ecn  
Timeframe: M1  
Runner contract: `a836ed038ae84a401b32dfc27690ddb04044de01`  
Detector blob: `3cb93ad5cfb5b743213e8bceb1db2e440b57086a`

Result:
- 222 signals
- 204 decisive
- 127 wins
- 77 losses
- +50R
- 62.254901960784316% decisive WR
- PF 1.6493506493506493
- max DD 6R
- max loss streak 5

Reproduced artifact:
`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260927T091652Z.json`

### Dedicated 227 baseline

Window: same  
Symbol: XAUUSD.ecn M1  
Result:
- 227 signals
- 220 decisive
- 124 wins
- 96 losses
- 5 ambiguous
- 2 no-fill
- +28R

Baseline artifact:
`artifacts/backtest-mt5-source-baseline/SP2L_MT5_SOURCE_BASELINE_V2_20260927T085954Z.json`

## KNOWN CONTRACT DIFFERENCES — DO NOT CALL THEM GEOMETRY DIFFERENCES

1. Reference runner deduplicates signals sharing the same entry index; dedicated baseline does not.
2. Reference runner permits only one active trade at a time; dedicated baseline evaluates signals independently.
3. Reference outcome handling uses entry-index activation, excludes entry candle from exit evaluation, resolves same-bar SL+TP as SL_FIRST, and marks unfinished final trade to market.
4. Dedicated baseline uses later pending fill semantics, excludes trigger candle from fill, has gap-sensitive fill search, classifies same-bar SL+TP as AMBIGUOUS, and separates NO_FILL.
5. Therefore 222 vs 227 must not be reconciled by changing P-Gap, spike multiplier, SL anchor, or any source geometry.

## SOURCE / CANONICAL STATUS

This document is a forensic navigation aid and checkpoint, not a canonical Strategy A specification.

Source meaning outranks backtest performance.

P-Gap exact source geometry, trigger acceptance semantics, SL boundary/buffer, 2X lifecycle, and AB=CD anchors/tolerance remain unresolved unless independently source-confirmed.

Neither the 222 nor 227 result authorizes a canonical rule.

## NEXT REQUIRED TEST

Use:
`scripts/run_sp2l_signal_ledger_forensics.py`

The tool now preserves duplicate fingerprint multiplicity and input order. It must be used to compare the reproduced 222 ledger against the 227 ledger.

Required classification:
- SIGNAL_POPULATION
- TRIGGER_OR_INDEXING
- GEOMETRY_OR_CONFIG
- FILL_OR_OUTCOME
- IDENTICAL

The final reconciliation must separately report:
signal population, duplicate entry indices, trigger/indexing, geometry/config, fill semantics, outcome evaluator, and data acquisition.

No cherry-picking, averaging, or performance-based rule selection.
