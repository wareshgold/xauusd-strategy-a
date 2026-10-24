# SP2L Spec Kit Pilot Specification — Coverage Component — 2026-09-15

## Problem

The project needs a repeatable engineering process for small deterministic infrastructure changes without allowing the process to become a source of Strategy A trading semantics.

## Scope

Only the historical coverage infrastructure is in scope. The pilot does not modify Strategy A signal generation, execution, fills, targets, or geometry.

## Functional Requirements

1. Coverage windows must be represented deterministically.
2. Input ranges and window boundaries must remain explicit.
3. Overlap/coverage checks must be testable from fixed inputs.
4. The behavior must be reproducible across repeated runs.
5. Tests must document the accepted contract.

## Governance Requirements

1. No unresolved Strategy A geometry may enter the pilot specification.
2. No optimization may be used to choose implementation behavior.
3. No trading performance metric may be used as an acceptance criterion.
4. Any future strategy-specific requirement must pass the SP2L research gates first.

## Acceptance Criteria

- Existing coverage behavior is preserved unless an explicitly reviewed engineering change is required.
- Tests cover normal, boundary, and overlap cases represented by the existing contract.
- The specification can be traced to implementation and tests.
- Reviewers can distinguish engineering requirements from research governance.

## Out of Scope

P-Gap, entry anchor, Leg-2 start, invalidation, pending refresh, trigger classifier, AB=CD, targets, 2X, bearish mirror, execution/fill semantics, buffers, thresholds, and production BUY/SELL logic.

## Review Decision

This specification is a pilot artifact only. It does not constitute a frozen Strategy A specification.
