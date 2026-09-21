# MT5 Demo Execution Safety Checkpoint — 2026-09-21

## Status

The MT5 infrastructure pre-flight is READY on account 812930 / OtetGroup-MT5 for XAUUSD.ecn.

Observed operator check:
- terminal connected: true
- Algo Trading: true
- account trade allowed: true
- account expert trading: true
- XAUUSD.ecn trade mode: FULL
- XAUUSD.ecn openable: true
- real execution flags: false

## Safety hardening

This checkpoint adds:
- Correct MetaTrader5 symbol trade-mode mapping: LONGONLY=1, SHORTONLY=2, CLOSEONLY=3, FULL=4.
- Demo-only guard immediately before any real order submission.
- Regression tests preventing a REAL account from reaching `order_send`.
- Strategy A geometry/signal generation remains inactive.
- Only externally supplied, human-approved signals can reach the gateway.

## Execution boundary

No `--mode real` execution is authorized by this checkpoint.

The next operator test requires explicit confirmation that the connected account is a DEMO account, then a single human-approved 0.01 test signal can be used to validate the execution chain.

## Commits

- `35ce59d7eaa7c4891edcda33e118c732ea97586f` gateway safety hardening
- `bbfbc98c47533df71af3c3b9cc5b07d67297f903` readiness demo-account guard
- `db481af5952a067a8e3d523d9907ce7ab6c52f8c` test fixes / checkpoint head

## Explicit non-goals

This checkpoint does not freeze or promote any SP2L geometry, P-Gap formula, AB=CD rule, entry semantics, or production BUY/SELL logic.
