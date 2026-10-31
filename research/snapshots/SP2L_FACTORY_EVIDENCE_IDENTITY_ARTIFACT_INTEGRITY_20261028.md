# SP2L Factory Snapshot — Evidence Identity vs Artifact Integrity — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-EVIDENCE-IDENTITY-ARTIFACT-INTEGRITY-20261028`
- Branch: `research/factory-candidate-lab-20261010`
- Audited source revision: `dae8dd2b9da3eaa48be0867513ae1a209770d37a`
- Scope: read-only source audit of existing evidence identities, in-memory ledgers, handoff binding, and restart recovery.
- Strategy/production status: research infrastructure only; no canonical SP2L geometry or trading decisions.

## Findings confirmed in source

1. `EvidenceBundle` computes a deterministic SHA-256 fingerprint over its serialized run identity, metrics, result revision, and result payload. `EvidenceLedger` rejects a conflicting payload reusing an `evidence_id`, but the ledger is in-memory and does not itself provide a durable artifact store.
2. `ResearchRecord` binds the run fingerprint, evidence ID and evidence fingerprint, snapshot fingerprint, and audit fingerprint. Its `from_dict` path validates the record's own fingerprint. That proves internal record consistency; it does not independently load the original evidence, snapshot, audit, or artifact bytes and recompute their fingerprints.
3. `ResearchEvidenceBundle` and `ResearchEvidenceLedger` similarly bind run/record/statistical/stability identities, but the ledger implementation is in-memory. These fingerprints do not, by themselves, establish that an external file currently named by an artifact identifier contains the expected bytes.
4. `ResearchHandoff` binds an output artifact identifier to a `ResearchRecord.evidence_id`, checks the source `COMPLETED` event and research-run fingerprint, and fingerprints the handoff payload. It does not carry the research evidence fingerprint as a distinct field or read/hash the external output artifact. The optional content SHA in this contract is for the dataset, not a general output-artifact byte receipt.
5. The restart recovery report remains deliberately journal-derived. It validates event/report fingerprints and recognizes lifecycle events, but does not resolve artifact identifiers against a durable registry or reconcile external artifact bytes.

## Decision

The repository contains strong **identity and in-memory consistency checks**, but the audited paths do not establish a durable, byte-verified output-artifact receipt that restart recovery can safely use as a completion signal. Do not equate:
- an artifact ID or filename with artifact integrity;
- a valid event/handoff/record fingerprint with verification of external file bytes;
- an in-memory append-only ledger with durable cross-process persistence;
- an artifact side effect with a committed terminal lifecycle event.

Keep recovery fail-closed: an interrupted `DISPATCHED` job without a durable `COMPLETED` or `FAILED` event remains `INTERRUPTED_REVIEW_REQUIRED` and requires explicit manual reconciliation. No automatic replay, inferred completion, journal repair, or artifact deletion.

## Verification context

The preceding boundary test commit `8271493be3bc5542c9a6c2bfb15934f627ebc82f` had:
- Factory Research Tests PASS — run `40669402324`.
- Factory Journal Lock Cross-Platform Tests PASS on Ubuntu and Windows — run `40669402343`.
- A fresh forensic workflow run on that exact test commit was not observed; the latest recorded forensic PASS was on parent snapshot commit `416f8ade41a9e03a80870399b58307b1042d67c0`, run `40669259420`.

This document is a source audit, not a claim that new tests were executed. The snapshot commit itself must be verified separately if CI is required for documentation changes.

## Next safe step

Before proposing a receipt schema, inspect the actual Factory output writers and artifact directory conventions to determine whether an existing persisted manifest/registry already records output paths and content hashes. If none exists, record that as an explicit design gap and request a source-approved contract before implementing one. Do not invent fields or promote recovery state based on assumed semantics.

## Non-goals

- No Strategy A geometry, P-Gap, AB=CD, entry, fill, or execution rule changes.
- No MT5 terminal, Strategy A forward-test, or Strategy B runner changes.
- No statistical edge, holdout pass, or production readiness inferred.
- No local pull, branch merge, cleanup, or mutation of runtime evidence.
