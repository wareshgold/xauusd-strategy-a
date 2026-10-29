# Strategy V3 Operational Winner — Snapshot Record

Record date: 2026-10-29 (UTC snapshot filename timestamp: 20261029T045621Z)

## Selection

**Label:** Strategy Version 3 — RR2/TRAIL4 Pending Limit  
**Status:** OPERATIONAL_SELECTION_RESEARCH_ONLY  
**Canonical:** false  
**Statistically proven winner:** false  
**Production approved:** false

This record preserves the operator's operational selection and identifies the source code. It does not claim a statistically validated edge or canonically resolved SP2L geometry.

## Source identity

- Repository: https://github.com/wareshgold/xauusd-strategy-a
- Source HEAD: `dac76b09da01f022d745f51328ee703f6fb59851`
- Source branch observed locally: `fix/rr2-trail4-pending-lifecycle-list-local-20261008`
- Runner: `scripts/run_sp2l_v3_xauusd_forward_test.py`
- Config: `scripts/sp2l_v3_rr2_trail4_config.py`
- Exact source commit: https://github.com/wareshgold/xauusd-strategy-a/commit/dac76b09da01f022d745f51328ee703f6fb59851

## Frozen launch profile as observed

- Startup event time: `2026-10-27T05:56:24.848280+00:00`
- Mode: `RESEARCH_AUTHOR_REPLICA_MULTI_SYMBOL_FORWARD_TEST`
- Broker server: `OtetGroup-MT5`
- Broker symbol: `XAUUSD.ecn`
- P-Gap price: 1.0
- Spike multiplier: 1.5
- Maximum SL distance: 10.0
- TP: 2.0R
- Volume: 0.01
- Order mode: `PENDING_LIMIT_RESEARCH`
- SL anchor: `SPIKE_CANDLE_EXTREME_RESEARCH`
- Pending TTL: 30 minutes
- MT5 point/digits: 0.01 / 2
- Reported pip metadata: 0.01 (broker point-based)
- Source trailing distance: 0.4 price units, from `TRAIL_PIPS=4.0` × `XAU_PIP_SIZE_PRICE=0.1`
- Pending server offset override used: 2 hours
- Canonical: false

Do not treat broker/server offset or symbol mapping as universal. Verify these values on any other machine/account.

## Local snapshot file and integrity

The operator created and JSON-validated this local file:

`artifacts/v3/winner-snapshots/STRATEGY_V3_OPERATIONAL_WINNER_20261029T045621Z.json`

Reported SHA-256 of that exact local JSON file:

`E0FA0A2BF6888DFA6EF737D047B7249D6DA2C1F00911C634D8D6FCC31C3AF105`

This hash identifies the local JSON snapshot only. It is not the event-log hash.

## Runtime observations at snapshot time

- Runner-process matches: 2.
- Operator clarified that one runner commonly has a parent and child process. Therefore the count of two is **not** treated as evidence of duplicate runner instances.
- Dashboard: operator reported it was already running.
- Event log at the expected V3 path: present.
- Git worktree status entries: 63.

The process parent-child relationship and dashboard-to-V3 data-source wiring were not independently verified in this snapshot. The existing `scripts/live_dashboard.py` at the source commit is configured for generic multi-symbol state/event paths, not the V3-specific state/event paths. Do not assume its page is a V3-specific health monitor.

## Evidence limitations

The local snapshot output did not include the actual process details, event-log SHA-256, state-file mtime, dashboard process/port evidence, or current new-event tail. Those details are intentionally marked unverified rather than inferred.

The local JSON file itself has not been uploaded by this record; this GitHub file records its reported path/hash and the operator-supplied startup facts. To archive the exact JSON artifact in GitHub, review it for private account/runtime data first and use an explicit, privacy-safe archival step.

## Decision

Operationally selected as the current Strategy V3 forward-test candidate, **research/demo only**. This is not a performance ranking, not source confirmation, not permission to execute on a funded account, and not a production promotion. Required future gates include exact frozen rules, untouched validation, robustness/stability checks, and a fresh holdout.
