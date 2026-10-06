# SP2L Strategy Research Factory — Snapshot 2026-10-06

## Purpose

This snapshot freezes the first architectural foundation of the Strategy Research Factory.

The Factory is a research and validation orchestrator. It is not a production signal generator, broker executor, or autonomous strategy selector.

## Workflow

SOURCE RESOLUTION → STRATEGY ENGINE → TEST FACTORY → OPTIMIZATION / ROBUSTNESS → UNTOUCHED VALIDATION → FRESH HOLDOUT → FORWARD VALIDATION → PRODUCTION ELIGIBILITY

A failed validation gate returns the candidate to research rather than silently changing the strategy.

## Initial repository placement

- src/strategy_factory/models.py
- src/strategy_factory/gates.py
- src/strategy_factory/factory.py
- src/strategy_factory/__init__.py
- tests/test_strategy_factory.py

## Governance rules

1. Source meaning outranks backtest performance.
2. Unresolved geometry is not silently invented by the Factory.
3. Optimizer output is a research candidate, never a canonical rule.
4. Python historical simulation and MT5 forward execution have separate roles.
5. Python ↔ MT5 reconciliation is a forward-validation gate.
6. The Factory does not generate production BUY/SELL decisions.
7. A candidate cannot become production-eligible without all required gates.
8. Live forward-test runner/config are outside this change.

## Current status

- Factory foundation: IMPLEMENTED.
- Strategy compiler: NOT IMPLEMENTED.
- Canonical SP2L geometry compiler: NOT IMPLEMENTED.
- Historical test engine: NOT IMPLEMENTED.
- Optimizer: EXISTING RESEARCH TOOL, NOT YET INTEGRATED.
- Robustness engine: NOT IMPLEMENTED.
- Fresh holdout gate: NOT IMPLEMENTED.
- Forward-validation adapter: NOT IMPLEMENTED.
- Production promotion: BLOCKED BY DESIGN.

## Next planned increments

1. Define Strategy Manifest schema.
2. Build source-evidence registry and unresolved-question ledger.
3. Build deterministic strategy compiler interface.
4. Add synthetic fixtures and contract tests.
5. Build test-engine adapter around frozen event semantics.
6. Integrate optimizer as a candidate generator only.
7. Add robustness and stability gates.
8. Add untouched and fresh-holdout dataset controls.
9. Add MT5 reconciliation adapter.
10. Build a research dashboard and CLI after the engine contracts are stable.

## Branch

research/sp2l-strategy-research-factory-20261006

## Base

Created from forward-reconciliation branch head 171c1d7b687f04b0f282e8db2a0e1f53f378eaa5.

## Safety

No live runner files, forward state, event logs, or production execution rules are modified by this factory foundation.
