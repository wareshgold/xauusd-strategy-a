# SP2L Unified Forward Trade + Telegram Checkpoint — 2026-09-21

## Status
RESEARCH-ONLY / DEMO / OBSERVABILITY INTEGRATION

## Change
Commit `d702c543b48b18f0758c7db84a03f7e92f409ab8` integrates Telegram trade-lifecycle monitoring into the existing `run_sp2l_author_replica_forward_test.py` process.

The single runner now performs both:
1. research candidate detection and demo pending-order execution;
2. MT5 deal lifecycle observation and Telegram reporting.

Lifecycle reporting covers:
- OPEN/fill;
- CLOSE;
- TAKE PROFIT;
- STOP LOSS;
- actual MT5 profit, commission, swap and net;
- entry/exit, SL/TP, volume, deal/order/position identifiers.

A separate Telegram monitor process is no longer required for this forward-test workflow.

## Safety boundary
- Demo-only guard remains active.
- `canonical=false`.
- Strategy geometry was not changed.
- No production BUY/SELL generation was enabled.
- This remains a research forward test.

## Local reset
Stop the old forward-test and standalone Telegram monitor processes before starting the unified runner, so duplicate Telegram messages are not generated.

Then pull the branch and start only the unified runner.
