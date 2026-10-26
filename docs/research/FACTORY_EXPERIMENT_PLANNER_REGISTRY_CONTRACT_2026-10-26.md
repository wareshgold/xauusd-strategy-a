# Factory Experiment Planner and Registry Contract — 2026-10-26

## Scope

The planner adds stable IDs for explicitly defined research questions and the existing synthetic test cases that discriminate among evidence-handling behaviors. These are not claims about canonical SP2L geometry, source-confirmed trading rules, broker execution, or profitability.

## Registries

- Hypothesis IDs are stable identifiers with explicit versions and question text.
- Fixture IDs map to a concrete test reference and one registered hypothesis.
- Duplicate IDs and unknown hypothesis/fixture references fail closed.
- The initial registry contains only three evidence-handling questions: preserving same-millisecond tick order, keeping OHLC SL/TP double-touch ambiguous without event ordering, and excluding a forming bar without explicit completion.
- Registry entries are not source citations and do not assert the hypothesis is true.

## Plan/execution boundary

The `plan_experiments` function produces deterministic `PLANNED` ledger records only. It binds caller-supplied SHA-256 values for frozen inputs and code, stable hypothesis/fixture IDs, and the prior record hash. It never executes a test or generates a PASS/FAIL outcome. A plan's summary explicitly states that it has not been executed.

Actual outcome records must be created by a separately controlled execution/reporting step using observed outputs and preserved evidence. A successful synthetic test means only that the test passed for its supplied fixture; it does not prove source meaning or real broker behavior.

## Integrity and authority

- Plans are deterministic for the same registry, selected fixture order, hashes, sequence, and prior tip.
- Fixture order is retained; it is not silently sorted.
- Duplicate fixture selections are rejected.
- Registry and plan records cannot authorize canonical rules or production decisions.
- No P-Gap formula, AB=CD anchor/tolerance, fill semantics, execution rule, BUY/SELL decision, or statistical edge is inferred.
