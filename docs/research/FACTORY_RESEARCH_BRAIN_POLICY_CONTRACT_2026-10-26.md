# Factory Research Brain Policy Contract — 2026-10-26

## Goal

The Factory research brain must actively reduce uncertainty through deterministic evidence evaluation, counterexamples, synthetic fixtures, and repeatable tests. It must not fill gaps by invention. This first policy engine is deliberately narrow: it routes a stated hypothesis based only on explicitly supplied, content-hashed evidence.

## Deterministic contract

- Every evidence item has a unique ID, reference, SHA-256 digest, role, and explicit outcome.
- Evidence roles are separated: SOURCE, DATA, TEST, EXECUTION, and STATISTICAL_VALIDATION.
- Missing required roles remain unresolved. A test or profitable backtest cannot substitute for source evidence.
- Any explicit contradiction blocks the hypothesis until reconciled.
- Failed tests block promotion. Inconclusive evidence requests a discriminating test with frozen inputs.
- A fully supported research claim may be recorded, but any request to change canonical rules is routed to human source review.
- Canonical authorization and production-decision authorization are always false. This engine never emits BUY/SELL decisions.

## Rebuild loop

1. Register a narrowly stated hypothesis and its required evidence roles.
2. Bind every evidence item to a stable reference and content hash.
3. Run deterministic synthetic fixtures and source-parity tests; retain failures as evidence, not as data to erase.
4. Evaluate missing roles, contradictions, failed tests, and inconclusive outcomes.
5. Generate only evidence-gathering or contradiction-resolution actions from the explicit result.
6. Re-run the same frozen inputs after a change; preserve prior result and hash as a separate revision.
7. Require fresh, untouched validation only after source meaning and geometry are frozen.

## Limits

This is a policy gate, not an autonomous discovery oracle, backtester, broker adapter, or canonical-rule author. It does not yet discover evidence automatically, run a continuous worker, access local MT5, or schedule jobs. It only evaluates the evidence explicitly supplied to it. Source conflicts and ambiguous geometry must remain unresolved until human/source review settles them.

## Acceptance criteria for this first slice

- Deterministic output for identical hypothesis/evidence inputs.
- Missing source evidence cannot be filled by data/test/performance evidence.
- Contradictions and failed tests block the claim.
- Canonical and production authorization remain false under every path.
- No MT5, live runner, forward test, or trading side effects.
