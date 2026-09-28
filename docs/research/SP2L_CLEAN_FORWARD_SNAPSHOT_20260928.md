# SP2L Clean Forward Snapshot — 2026-09-28

## Purpose

Frozen operational checkpoint before the next one-month weekly-decomposed research backtest.

## Repository

- Repository: `wareshgold/xauusd-strategy-a`
- Branch: `research/sp2l-clean-forward-xau-eurusd-usdjpy-20260928`
- Snapshot commit: `e87f627c669f2082c26e4e5a80975d5aca62fbe5`
- Forward runner: `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`
- Forward mode: `RESEARCH_AUTHOR_REPLICA_MULTI_SYMBOL_FORWARD_TEST`
- Canonical: `false`

## Forward-test configuration at snapshot

| Symbol | P-Gap price | Spike multiplier | Max SL price | TP |
|---|---:|---:|---:|---:|
| XAUUSD.ecn | 1.0 | 1.5 | 10.0 | 1R |
| EURUSD.ecn | 1.0 | 1.25 | 10.0 | 1R |
| USDJPY.ecn | 1.0 | 1.25 | 50.0 | 1R |

Common execution/session settings:

- M1
- Pending Limit Research mode
- SL anchor: `SPIKE_CANDLE_EXTREME_RESEARCH`
- Pending TTL: 30 minutes
- London open → New York close
- Volume: 0.01 per configured symbol
- Demo-only account guard
- Research-only / non-canonical

## MT5 environment observed at snapshot

- Server: `OtetGroup-MT5`
- Account: demo
- XAUUSD.ecn: trade mode FULL, min volume 0.01
- EURUSD.ecn: trade mode FULL, min volume 0.01
- USDJPY.ecn: trade mode FULL, min volume 0.01
- Forward runner startup and Python compilation succeeded on 2026-09-28.

## Research boundary

This snapshot does **not** promote any of the above parameters or geometry to canonical Strategy A rules.

The source-boundary blockers remain:

- exact P-Gap formula/numeric threshold unresolved
- trigger touch/penetration/close semantics unresolved
- spike-start SL exact anchor/buffer unresolved
- pending-order fill/bar-order semantics unresolved
- AB=CD anchors/tolerance unresolved
- spike magnitude definition/numeric threshold unresolved

## Next research step

Run a one-month M1 research backtest for the same three forward-test symbols, decomposed by week, using the recorded selected configurations exactly as configured. Results are diagnostic only and must not modify the running forward configuration.
