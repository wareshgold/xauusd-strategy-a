# SP2L Research Factory — Brain Start Snapshot 2026-10-07

## Snapshot identity

- Branch: `research/sp2l-starnet-engine-integration-20261007`
- Snapshot purpose: freeze the starting point before advancing the Factory "brain" while the StarNet visual/world layer remains a presentation spike.
- Latest visual/world commit: `4027b3af052211d08bc79139d769c2b5c497fc41`
- Upstream StarNet commit: `e0a36dcd31787248b877aea01a6e53741012bc46`
- Production BUY/SELL authority: **LOCKED**
- Strategy A geometry: **UNCHANGED**
- Live MT5 forward runner: **UNCHANGED**

## Current world state

The StarNet-derived world is rendering successfully.

Current authored research rooms:

1. DISCOVERY LAB
2. STABILITY LAB
3. ROBUSTNESS LAB
4. HOLDOUT VAULT
5. FORWARD OPS

A visual workflow spine / handoff topology has been added using StarNet corridor and belt infrastructure:

`DISCOVERY → STABILITY → ROBUSTNESS → HOLDOUT → FORWARD`

This is currently presentation infrastructure. It must not invent research jobs, worker activity, metrics, or production decisions.

## What is intentionally not finished

- Worker-to-station physical routing is not yet fully bound to live telemetry.
- Job/artifact handoff animation is not yet authoritative.
- The visual conveyor network is not yet the source of Factory state.
- The StarNet world remains a renderer/runtime layer over the Factory contracts.

## Brain-first next phase

The next work should advance the Factory control/research brain before spending more effort on visual polish.

Target architecture:

```
Source / Frozen Contracts
        ↓
Research Job
        ↓
Factory Queue
        ↓
Worker Dispatch
        ↓
Execution Adapter
        ↓
Evidence / Provenance / Gates
        ↓
Research Record
        ↓
Telemetry
        ↓
StarNet World
```

The world must consume this state; it must never create it.

## Brain invariants

The Factory must remain:

- deterministic;
- provenance-bound;
- research-only;
- source-aligned;
- auditable;
- unable to define Strategy A geometry by itself;
- unable to authorize production BUY/SELL;
- unable to convert visual animation into evidence.

Canonical Strategy A promotion remains blocked until source resolution and the defined validation workflow are satisfied.

## Scope boundary

Do not modify the active live forward-test runner as part of this Factory phase.

Do not mass-clean unrelated local artifacts.

Do not promote any discovered backtest result to canonical strategy logic merely because it performs well.

## Snapshot declaration

**This document is the baseline for the next Factory-brain implementation phase.**

The StarNet visual layer can be improved later without changing the research contracts or production lock.
