# Strategy Discovery — Source Intake Contract

## Purpose

The Strategy Factory has two distinct research tracks:

1. **SP2L reconstruction:** preserve source-confirmed meanings of the original strategy. Unresolved geometry remains unresolved.
2. **External strategy discovery:** capture and research independent strategy ideas found on sources such as GitHub and YouTube. The SP2L source-resolution ledger is not a universal prerequisite for this track.

This contract defines only the first boundary of external discovery: a deterministic record of the source, captured bytes, extracted claims, and unresolved questions.

## Intake record

Each intake must preserve:

- source platform and exact HTTPS source URL;
- source title and publisher;
- upstream revision/video identifier where available;
- UTC capture time;
- local snapshot artifact URI and SHA-256 of the exact captured bytes;
- extracted claims as a list separate from unresolved questions;
- a deterministic fingerprint binding all recorded fields.

The upstream URL or branch name is not itself an immutable snapshot. The captured artifact hash is the byte-level identity used for reproducibility. Preserve the actual artifact alongside the record; the intake model does not fetch or archive it automatically.

## Interpretation boundary

Extracted claims are research notes, not automatically verified rules. A claim may be ambiguous, incomplete, misleading, or impossible to reproduce from the available market data. Record uncertainty rather than silently filling gaps.

An intake record can be ready to draft a research candidate while still containing unresolved questions. That status does **not** mean it is ready for a valid backtest, Fresh Holdout, Forward Test, or production.

Every intake serializes these controls explicitly:

- canonical: false
- backtest_approved: false
- forward_approved: false
- production_eligible: false
- allowed_use: RESEARCH_CANDIDATE_DRAFT_ONLY

## Out of scope

This module does not:

- crawl YouTube or GitHub;
- download source code, transcripts, or data;
- execute third-party code;
- assert source claims are true;
- define strategy geometry or execution semantics;
- optimize parameters or rank strategies;
- approve a backtest, Holdout, Forward Test, or production deployment.

## CandidatePlan integration

The external-strategy blueprint now binds this intake record to a rule specification, declared data capability, execution and cost assumptions, and a finite parameter grid. It creates an EXTERNAL CandidatePlan with its own provenance fingerprint and no fabricated SP2L source-resolution fingerprint. Source uncertainties must either remain explicit or have a separately recorded resolution rationale.

The existing candidate runner still requires immutable DEVELOPMENT data, matching dataset bytes, an injected adapter that implements the declared rules, and fingerprint-bound metrics net of costs. The blueprint is not itself a backtest engine or source crawler. Next work is the source-capture/connectors and a safe adapter contract; Fresh Holdout remains untouched by optimization, and post-Holdout tuning remains prohibited.
