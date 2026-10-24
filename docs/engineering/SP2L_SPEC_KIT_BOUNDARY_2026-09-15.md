# SP2L Spec Kit Engineering Boundary — 2026-09-15

## Purpose

Define the allowed boundary for GitHub Spec Kit if it is adopted by the SP2L project.

## Authority Model

```text
AUTHORITATIVE
Source Evidence → Manual Adjudication → Frozen Geometry

ENGINEERING
Frozen Geometry / Authorized Engineering Requirement
        ↓
Spec Kit → Specify → Plan → Tasks → Implement → Converge
```

Spec Kit is an **engineering process/tooling layer**. It is not a source-of-truth layer for trading semantics.

## Allowed Inputs

Spec Kit may consume:

- manually adjudicated requirements;
- frozen geometry fields;
- source-linked engineering constraints;
- deterministic infrastructure requirements;
- reproducibility and CI requirements.

## Forbidden Promotion

A Spec Kit artifact must not promote any of the following from hypothesis/blocked state to canonical state:

- unresolved P-Gap geometry;
- unresolved entry anchor;
- unresolved Leg-2 anchor;
- unresolved invalidation boundary;
- unresolved pending refresh semantics;
- unresolved trigger classifier;
- unresolved AB=CD anchors or tolerance;
- unresolved target/2X semantics;
- unresolved bearish mirror;
- unconfirmed fill/execution semantics;
- implementation-selected buffers or thresholds.

## Review Gate

Before a Spec Kit-generated implementation can affect Strategy A behavior, the relevant requirement must already have a valid SP2L research disposition and frozen-geometry authorization.

If a requirement is not frozen, implementation may only represent it as explicitly blocked, observational, or fixture/test infrastructure. It must not become executable trading logic.

## Success Criterion

Adoption succeeds only if it improves engineering reproducibility and reviewability **without changing the source-first research hierarchy**.
