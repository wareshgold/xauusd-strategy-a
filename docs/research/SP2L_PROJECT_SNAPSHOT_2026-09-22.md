# SP2L Strategy A — Official Project Snapshot
## 2026-09-22

> Checkpoint type: research / engineering / forward-test continuity
> Branch: `research/sp2l-f13-demo-forward-slfixed-2026-09-21`
> HEAD at snapshot update: `126e32952e44ab27e5125fe3848b2983d6206252`

## 1. Project objective

Reconstruct XAUUSD Strategy A as a deterministic, reproducible SP2L (Spike → 2 Leg) system using source-first evidence.

Canonical workflow:

```
SOURCE RESOLUTION
→ SYNTHETIC FIXTURES
→ FROZEN GEOMETRY
→ DEV
→ UNTOUCHED VALIDATION
→ ROBUSTNESS / STABILITY
→ FRESH HOLDOUT
→ PRODUCTION
```

Source meaning outranks backtest performance. No unresolved geometry, execution semantics, or fill assumptions may become canonical because they improve results.

AI may assist research, engineering, validation, documentation and analytics, but must not autonomously define canonical Strategy A rules or generate production BUY/SELL decisions.

## 2. Source / geometry status

- SP2L remains the working Strategy A hypothesis.
- P-GAP has been explicitly separated from ordinary/common GAP in the research record.
- Source-confirmed findings are recorded separately from research candidates.
- Unresolved items remain non-canonical rather than being filled by inference.
- No invented AB=CD anchor/tolerance, fill=C rule, pivot rule, or production execution rule is permitted.
- Frozen Geometry is not considered complete merely because a backtest performs well.

## 3. Research implementation status

The repository contains a research author-replica implementation used for controlled testing.

Current forward-test configuration recorded in the runner:

- mode: `RESEARCH_AUTHOR_REPLICA_FORWARD_TEST`
- canonical: `false`
- P-GAP price parameter: `1.0`
- spike multiplier: `1.5`
- maximum SL distance: `10.0`
- TP: `1R`
- demo volume: `0.01`
- SL anchor: `SPIKE_CANDLE_EXTREME_RESEARCH`
- demo order mode: `PENDING_LIMIT_RESEARCH`

Important: these values are research/replica parameters, not canonical Strategy A declarations.

The forward runner explicitly records the difference between theoretical historical trigger price and the executable forward-test order. This execution difference is experimental and must not be promoted to canonical fill semantics.

## 4. Forward-test / MT5 work completed

The MT5 demo path has been implemented and exercised as a research-only forward-test path.

Implemented/recorded components include:

- MT5 readiness and symbol-openability checks.
- Demo-only guards.
- Author-replica forward runner.
- Pending-limit research execution mode.
- Forward event logging.
- Persistent lifecycle state.
- Trade lifecycle monitoring.
- Telegram signal/lifecycle output.
- Entry, SL, TP, risk/pip and result reporting.
- Multi-symbol forward-test runner.
- Human-facing MT5 timestamp conversion to Iran time in the latest branch update.

The forward runner has since received two execution-state reliability fixes: failed orders are retryable without permanently suppressing the trigger, and restart reconciliation rebuilds successful execution/notification state from the event log. These changes do not alter Strategy A geometry, source interpretation, or canonical status.

## 5. Validation evidence already obtained

The research record includes:

- 4-week MT5 author-replica stability testing.
- An 81-combination parameter grid used as diagnostics.
- Baseline research result: 158 signals, 103 wins, 51 losses, 4 ambiguous; 66.88% win rate and +52R under that research configuration.
- Across the 81 diagnostic combinations, all were positive-R in that historical study and 80/81 exceeded 60% win rate.

These results are evidence for further validation only. They do not promote any parameter or geometry to canonical status.

Earlier non-overlap weekly testing also showed meaningful week-to-week variation. This remains a stability/robustness concern and is not treated as proof of production edge.

## 6. Data / observation infrastructure

A source-feature observation layer was built and validated.

Recorded validation result:

- 28,815 observation rows.
- `geometry_changed=false`.

This layer is intended to preserve reproducibility while separating feature observation from canonical strategy promotion.

## 7. Current research gates

The project remains governed by these gates:

- Source resolution before canonicalization.
- Deterministic synthetic fixtures for disputed geometry.
- Explicit blocked/unresolved status where source evidence is incomplete.
- Untouched validation only after geometry is frozen.
- Robustness/stability before fresh holdout.
- Fresh holdout before production.
- No backtest-driven source reinterpretation.
- No AI-decided canonical rules.
- No autonomous production trade decisions.

## 8. Telegram / execution architecture status

Telegram is an output/monitoring adapter, not the strategy definition.

The current research path supports:

```
Research candidate
→ research/demo execution
→ MT5 lifecycle
→ journal/event record
→ Telegram notification
```

Production architecture must remain separated from this research path until the strategy has passed the required evidence gates.

## 9. Future VIP Trader App — RESERVED / NOT YET IMPLEMENTED

The project has a reserved future product concept for a local VIP Trader App. This idea is intentionally recorded here so it is not lost, but implementation is deferred until the current SP2L forward-test/research work is completed.

### Product concept

A local Windows trading application for authorized VIP users that:

- detects an installed MT5 terminal automatically;
- detects available broker symbols;
- lets the user select which approved symbols to trade;
- connects to the user's MT5 account;
- executes only an already-approved deterministic strategy;
- provides a local dashboard for MT5 connection, account/environment status, selected symbols, trading ON/OFF and open-trade monitoring;
- communicates with a Telegram-based VIP licensing/bot layer;
- generates or provisions a unique VIP activation code;
- validates license status, expiration, allowed symbols and potentially device limits;
- supports remote revoke/disable as a licensing control;
- records execution/journal history locally for later review;
- can eventually be packaged as a Windows application/installer.

### Intended architecture

```
SOURCE
  ↓
FROZEN STRATEGY
  ↓
VALIDATED ENGINE
  ↓
SIGNAL
  ↓
EXECUTION ENGINE
  ↓
MT5
```

The future application must NOT become:

```
AI → BUY/SELL → MT5
```

AI is not the production decision-maker.

### Planned future phases

- F1 — Local Trader Core: MT5 detection, connection, symbol discovery, execution and journal.
- F2 — Windows GUI/dashboard.
- F3 — VIP license service + Telegram bot/code provisioning.
- F4 — Telegram trade lifecycle and account notifications.
- F5 — Windows packaging, installer and controlled distribution.

Status: `RESERVED — DO NOT IMPLEMENT YET`.

## 10. Immediate next checkpoint

The next active work remains the SP2L F13 multi-symbol demo forward-test/research path. Current branch HEAD is `126e32952e44ab27e5125fe3848b2983d6206252`.

Before any production consideration:

1. Continue collecting forward observations/trades.
2. Audit the resulting event/journal records.
3. Measure execution-vs-theoretical-entry differences.
4. Measure pending-order lifecycle behavior and expiry/cancellation behavior.
5. Keep all unresolved execution semantics explicitly research-only.
6. Complete robustness/stability and fresh-holdout gates.
7. Only source-confirmed rules may later enter a frozen canonical specification.

## 11. Snapshot integrity statement

This checkpoint is a continuity record, not a declaration that Strategy A is complete or production-ready.

The future VIP Trader App is preserved as a product idea only and does not alter the current research/canonical status of SP2L.
