# Dataset Manifest Pin Ledger Contract — 2026-10-26

## Purpose

The pin ledger records dataset-manifest fingerprints in a deterministic, append-only sequence. It supports reproducible reload and tamper/truncation/reordering detection when checked against an independently trusted expected tip fingerprint.

## Implementation

- Module: `src/strategy_factory/dataset_manifest_pin_ledger.py`
- Tests: `tests/test_dataset_manifest_pin_ledger.py`
- Serialization: canonical JSON with sorted keys and compact separators.
- Each pin binds sequence number, dataset ID, manifest fingerprint, and previous pin fingerprint.
- Reload validates the entire chain and requires an externally supplied expected tip fingerprint.
- A dataset ID may be pinned only once within a ledger.
- CI executes the pin-ledger tests in a dedicated step.

## Trust boundary

The ledger is not itself a trust root. If the expected tip fingerprint is read from the same mutable location as the ledger, an attacker or mistaken operator able to replace both can replace the history undetected. The expected tip must be retained or signed through a separately controlled channel, such as a protected release attestation or a separately administered registry. This repository implementation does not yet fetch, authenticate, or enforce that external channel.

The ledger is durable only if the caller stores its serialized bytes in durable storage. The module itself does not write files, call external services, sign attestations, or establish access controls.

## Adversarial coverage

Synthetic tests cover deterministic round-trip, wrong external tip, modified record content, truncation, duplicate dataset IDs, and reordered/noncontiguous records. These tests validate the implementation contract; they do not prove that an external pin is authentic or that any real dataset was frozen.

## Scope

This is research-governance infrastructure only. It does not define canonical SP2L geometry, produce trading signals, establish statistical edge, or authorize production. No local worktrees, MT5, live runners, Strategy A forward-test evidence, or Strategy B execution are part of this increment.
