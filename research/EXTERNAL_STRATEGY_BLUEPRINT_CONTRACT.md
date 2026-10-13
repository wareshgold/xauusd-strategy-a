# External Strategy Blueprint Contract

## Purpose

External strategy discovery uses a generic blueprint rather than the SP2L source-resolution ledger. The blueprint binds a captured source intake to an explicit rule specification, required data capability, entry and exit semantics, execution semantics, cost model, fixed parameters, and a finite parameter grid.

## CandidatePlan integration

A validated blueprint may produce the existing development-only CandidatePlan with:

- provenance_mode set to EXTERNAL;
- external_source_fingerprint bound to the complete blueprint and its source intake;
- geometry_fingerprint used only as the existing CandidatePlan field carrying the generic rule-specification fingerprint;
- source_resolution_fingerprint set to null, never a fabricated SP2L fingerprint.

SP2L plans remain in provenance_mode SP2L and continue to require their explicit source-resolution fingerprint. The two provenance modes cannot be mixed within one candidate matrix.

## Backtest preconditions

Plan construction is blocked while unresolved_questions is non-empty. A researcher may resolve a question from the source, or create a separately identified interpretation with an explicit rule specification; the system must not silently guess. The blueprint also requires declared entry and exit semantics, execution semantics, a cost-model fingerprint, a finite candidate grid, and immutable DEVELOPMENT data with a matching byte-level SHA-256.

The resulting plan can only run through the existing adapter-injected candidate runner. This contract does not implement a strategy engine, scrape or execute third-party source code, or fabricate trades. An adapter must independently implement the declared rule specification and return fingerprint-bound trade metrics net of the declared costs.

## Decision boundary

Blueprints and candidate rankings are research-only. They do not select a canonical winner or authorize Fresh Holdout, Forward Test, or production. Existing validation gates, independent validation, frozen strategy revisions, and the no-post-Holdout-tuning boundary remain in force.
