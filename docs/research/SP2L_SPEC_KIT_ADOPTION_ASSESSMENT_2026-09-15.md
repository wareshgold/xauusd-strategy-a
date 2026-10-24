# SP2L GitHub Spec Kit Adoption Assessment — 2026-09-15

## Status

**ASSESSMENT ONLY — NO ADOPTION / INSTALLATION YET**

This document evaluates whether GitHub Spec Kit should be added to the SP2L project. It does not change Strategy A geometry, execution semantics, validation gates, or production authorization.

## Decision

**Recommendation: adopt selectively as an engineering SDD layer only after a compatibility review; do not make Spec Kit the authority for research meaning or trading rules.**

Spec Kit is well aligned with the engineering side of SP2L because it provides a specification-driven workflow for turning an agreed specification into plans, tasks, implementation, and convergence. The SP2L project, however, has a stricter research governance boundary: source meaning outranks implementation convenience, unresolved geometry remains unresolved, and AI cannot autonomously define canonical Strategy A rules.

Therefore Spec Kit must sit **below the SP2L research-governance layer**, not replace it.

## Source / External Reference Basis

The assessment was made against the official GitHub Spec Kit documentation and repository:

- https://github.github.com/spec-kit/
- https://github.com/github/spec-kit

The official material describes Spec Kit as a toolkit for specification-driven development and documents a lifecycle centered on constitution/specification/clarification/planning/tasks/implementation/convergence, with workflows and review gates that can be adapted to an existing project.

## Proposed Architecture

```text
SP2L GOVERNANCE
│
├── RESEARCH GOVERNANCE
│   ├── Source Resolution
│   ├── Evidence Intake
│   ├── Manual Adjudication
│   ├── Freeze Review
│   └── Frozen Geometry
│
└── ENGINEERING SDD
    ├── Spec Kit Constitution / project constraints
    ├── Specify
    ├── Clarify
    ├── Plan
    ├── Tasks
    ├── Implement
    └── Converge
```

The boundary is intentional: **Spec Kit may operationalize an already-authorized engineering specification; it may not authorize the specification itself.**

## What Spec Kit Could Improve

### 1. Engineering requirements traceability

A frozen engineering requirement can become a structured specification before implementation. This is useful for deterministic engine work, replay harnesses, CI, provenance, and validation infrastructure.

### 2. Repeatable implementation workflow

The specify → plan → tasks → implement → converge lifecycle gives the project a more explicit engineering sequence than ad-hoc issue-to-code progression.

### 3. Review checkpoints

Spec Kit workflows support review gates/checkpoints. SP2L can use those gates for engineering review without allowing them to overrule source adjudication.

### 4. Brownfield compatibility

The project is already substantial. Spec Kit's documented support for evolving specifications in existing projects makes it more suitable than a greenfield-only process.

## What Spec Kit Must NOT Replace

The following remain SP2L governance and are outside Spec Kit's authority:

1. **Source Resolution** — determining what the authoritative SP2L source actually means.
2. **Evidence Intake** — recording Tier-1/Tier-2 evidence and discriminators.
3. **Manual Adjudication** — resolving source ambiguity.
4. **Finite evidence stop condition** — preventing endless evidence hunting from becoming implicit rule invention.
5. **Frozen Geometry Readiness** — determining whether all required dimensions are actually adjudicated.
6. **Frozen Geometry** — the canonical source-derived Strategy A contract.
7. **Untouched Validation** — preserving independent validation data/procedures.
8. **Fresh Holdout** — final out-of-sample evidence before production.
9. **Production authorization** — no automated BUY/SELL authorization from an engineering SDD tool.
10. **Statistical edge determination** — backtest performance cannot resolve source ambiguity.

## SP2L-Specific Non-Negotiable Boundary

Spec Kit documentation can help answer **"How should we implement an agreed rule?"**

It must not answer **"What is the rule?"** when that rule is still source-ambiguous.

In particular, Spec Kit must not be used to invent or optimize any of the currently unresolved Strategy A dimensions, including:

- P-Gap formula / exact boundaries
- entry anchor / correction-level geometry
- Leg-2 start anchor
- structural invalidation OHLC boundary
- pending-order refresh threshold/semantics
- trigger classifier exact rule
- AB=CD A/B/C/D anchors
- AB=CD tolerance
- 2X / TP1 / TP2 formulas
- deterministic bearish mirror
- execution/fill semantics
- buffers or thresholds not confirmed by source

## Recommended SP2L Workflow With Spec Kit

```text
SOURCE_RESOLUTION
    ↓
EVIDENCE_INTAKE
    ↓
MANUAL_ADJUDICATION
    ↓
FREEZE_REVIEW
    ↓
FROZEN_GEOMETRY
    ↓
SPECIFY
    ↓
CLARIFY
    ↓
PLAN
    ↓
TASKS
    ↓
IMPLEMENT
    ↓
CONVERGE
    ↓
UNTOUCHED_VALIDATION
    ↓
ROBUSTNESS / STABILITY
    ↓
FRESH HOLDOUT
    ↓
PRODUCTION AUTHORIZATION
```

Spec Kit therefore begins **after** source-derived geometry is frozen for the engineering scope. It can also be used earlier for non-strategy infrastructure specifications, provided those specifications cannot silently encode unresolved trading geometry.

## Where Selective Adoption Makes Sense Now

### Safe / high-value candidates

- deterministic replay infrastructure
- evidence-candidate intake infrastructure
- provenance schemas
- CI gates
- fixture contracts
- validation harness infrastructure
- research documentation templates
- reproducibility tooling

### Unsafe before source freeze

- Strategy A signal specification
- executable P-Gap rules
- entry/fill rules
- AB=CD geometry
- target formulas
- pending refresh logic
- production BUY/SELL logic

## Constitution Requirements If Adopted

The project should impose an SP2L-specific constitution/guardrail set above the normal engineering workflow. At minimum:

1. Source meaning outranks implementation convenience.
2. No unresolved geometry becomes canonical.
3. Backtest performance cannot resolve source ambiguity.
4. AI cannot autonomously define Strategy A geometry.
5. Every canonical rule requires source provenance and adjudication status.
6. Every implementation must be reproducible.
7. Research gates precede implementation gates.
8. Production BUY/SELL remains forbidden until frozen geometry and statistical validation requirements are satisfied.
9. Untouched validation remains untouched.
10. Fresh holdout evidence is required before production.

## Adoption Risks

### Risk: specification becomes an accidental source of truth

**Mitigation:** mark source evidence and adjudication artifacts as authoritative; Spec Kit specifications may reference them but may not override them.

### Risk: AI fills gaps during clarification/planning

**Mitigation:** unresolved fields must remain explicitly unresolved/blocked. Clarification cannot promote a hypothesis to canonical geometry without manual adjudication.

### Risk: engineering optimization contaminates research

**Mitigation:** keep research and engineering artifacts separate and require a freeze-review gate before strategy implementation.

### Risk: process overhead

**Mitigation:** use Spec Kit selectively for durable engineering work rather than retrofitting every historical research artifact.

## Adoption Plan

### Phase A — Compatibility assessment

This document is the Phase A deliverable.

### Phase B — Minimal pilot

If approved, apply Spec Kit to one non-canonical engineering scope, preferably a deterministic infrastructure component. Measure whether the workflow improves traceability without changing research governance.

### Phase C — SP2L engineering constitution

Encode the boundary rules above in the engineering SDD layer. Keep source-resolution gates external/authoritative.

### Phase D — Controlled expansion

Extend Spec Kit to additional engineering scopes only if the pilot demonstrates improved reproducibility and reviewability without governance leakage.

### Phase E — Strategy implementation

Only after the relevant geometry is manually adjudicated and frozen should Spec Kit be allowed to drive implementation of that Strategy A specification.

## Explicit Non-Goals

This assessment does **not**:

- install Spec Kit;
- add `.specify/` or equivalent project scaffolding;
- rewrite existing research artifacts;
- declare any Strategy A geometry canonical;
- run optimization/backtests to select rules;
- change execution behavior;
- authorize BUY/SELL decisions;
- replace existing SP2L research gates.

## Final Recommendation

**Do not migrate the repository wholesale.**

**Do add Spec Kit later as a controlled engineering SDD layer, starting with a small non-canonical pilot.**

The project already has a stronger research-governance requirement than a conventional software project. Spec Kit is valuable for making the engineering path more deterministic and reviewable, but it should remain subordinate to SP2L source evidence, manual adjudication, frozen geometry, and statistical validation.

**Current gate:** `ASSESSMENT_COMPLETE → PILOT_NOT_STARTED`
