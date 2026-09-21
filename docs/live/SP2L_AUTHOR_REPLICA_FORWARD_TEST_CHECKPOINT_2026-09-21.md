# SP2L Author-Replica Demo Forward Test Checkpoint — 2026-09-21

Status: READY_TO_START

## Scope
This forward test runs the existing research-only author-replica implementation in MT5 DEMO in parallel with source-resolution work.
It is NOT canonical Strategy A and does not promote or freeze any geometry.

## Reused research implementation
Source implementation:
- research/harness/sp2l_author_replica_candidate.ts
- research/harness/sp2l_author_replica_v1.ts

Observed implementation parameters:
- fixed four-candle window: -4 / -3 / -2 / -1
- P-Gap price: 1.0
- spike multiplier: 1.5
- origin-candle SL
- TP: 1R
- max SL distance: 10.0

## Forward execution boundary
The research backtest records the trigger candle's theoretical entry extreme. A live process cannot know that final candle extreme before the candle closes.
Therefore the forward runner:
1. evaluates completed M1 candles using the research implementation;
2. records the theoretical entry;
3. executes a market order at the first observed tick after the completed trigger;
4. records the actual entry separately.

This is an experimental forward execution semantic, not a canonical fill rule.

## Safety
- MT5 account must be DEMO (trade_mode == 0).
- Real-account execution is rejected.
- Symbol: XAUUSD.ecn.
- Maximum open positions: 1.
- Volume: 0.01.
- No AI-generated discretionary signals.
- No Strategy A canonical geometry changes.
- Manual gateway tests are excluded from forward-test statistics.

## Artifact
Runtime events are appended to:
artifacts/forward-test/SP2L_AUTHOR_REPLICA_FORWARD_EVENTS.jsonl

## Start
Run locally from the repository root:

$env:LIVE_TRADING_ENABLE="true"; $env:ALLOW_REAL_EXECUTION="true"; python scripts\run_sp2l_author_replica_forward_test.py; Remove-Item Env:LIVE_TRADING_ENABLE,Env:ALLOW_REAL_EXECUTION -ErrorAction SilentlyContinue

Optional bounded smoke test:

$env:FORWARD_TEST_SECONDS="60"; python scripts\run_sp2l_author_replica_forward_test.py; Remove-Item Env:FORWARD_TEST_SECONDS -ErrorAction SilentlyContinue

Keep the process running on the MT5 machine for continuous DEMO observation.

## Interpretation
Forward-test performance must not be used to decide canonical geometry. Source resolution and Frozen Geometry continue independently.
