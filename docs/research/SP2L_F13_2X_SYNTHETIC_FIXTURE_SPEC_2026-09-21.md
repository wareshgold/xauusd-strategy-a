# SP2L F13 2X Synthetic Fixture Specification — 2026-09-21

## Purpose

Freeze the **tests**, not the unresolved execution rule, for the newly sourced 50% Entry-to-SL relationship.

Canonical promotion is explicitly disabled. These fixtures must detect implementation choices that would silently turn an unresolved 2X lifecycle into a canonical rule.

## Source-derived invariant under test

Author-controlled written evidence states that a secondary entry can be added at **50% of the distance from Entry to Stop-Loss**.

The fixtures therefore test only the price relationship:

**secondary_entry = Entry + 0.50 × (StopLoss - Entry)**

for a bullish price layout where Stop-Loss is below Entry, and the directional mirror for bearish layouts.

## Explicitly unresolved

Fixtures MUST NOT decide:
- whether 2X is mandatory or optional;
- order type;
- activation event;
- touch vs breach vs close;
- fill semantics;
- whether 2X is placed before/after first entry;
- whether 2X remains after partial fill;
- TP1/TP2 allocation;
- shared vs separate SL;
- replacement/update precedence.

## Fixture classes

| ID | Purpose | Expected state |
|---|---|---|
| F13-001 | Bullish 50% midpoint | PASS_RELATION_ONLY |
| F13-002 | Bearish 50% midpoint | PASS_RELATION_ONLY |
| F13-003 | Non-50% candidate | REJECT_RELATION |
| F13-004 | Entry/SL reversed geometry | REJECT_GEOMETRY |
| F13-005 | Same midpoint, different order type | UNRESOLVED_LIFECYCLE |
| F13-006 | Same midpoint, touch trigger | UNRESOLVED_LIFECYCLE |
| F13-007 | Same midpoint, breach trigger | UNRESOLVED_LIFECYCLE |
| F13-008 | Same midpoint, close trigger | UNRESOLVED_LIFECYCLE |
| F13-009 | 2X optional vs mandatory | UNRESOLVED_POLICY |
| F13-010 | 2X retained after first fill | UNRESOLVED_LIFECYCLE |
| F13-011 | 2X cancelled after first fill | UNRESOLVED_LIFECYCLE |
| F13-012 | 2X with changed SL | UNRESOLVED_UPDATE |
| F13-013 | 2X with changed Entry | UNRESOLVED_UPDATE |
| F13-014 | Shared vs separate SL | UNRESOLVED_RISK_BINDING |
| F13-015 | TP allocation variants | UNRESOLVED_TARGET_BINDING |

## Safety invariant

Every fixture carries:
- evidenceState = UNRESOLVED unless testing only the 50% relationship;
- canonicalEligible = false;
- productionEligible = false.

A passing fixture MUST NOT mutate Frozen Geometry or production eligibility.

## Gate

F13 fixture gate passes only when all 15 fixture classes execute deterministically and unresolved lifecycle variants remain distinguishable.

This is a research harness gate, not a source-resolution closure.
