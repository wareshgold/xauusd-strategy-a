# Runner / Position Provenance — Research Design

Status: research-only prototype; not wired into any MT5 runner.

## Purpose

Make every future runner execution and broker position traceable to the exact
runner version, Git commit, and immutable configuration snapshot that created it.
This is an observability/evidence feature only. It does not define SP2L geometry,
order semantics, fills, risk rules, or trading decisions.

## Identity model

- `runner_id`: stable logical runner family (e.g. `SP2L_V3_1_XAUUSD`).
- `runner_version`: explicit human-readable build/version label.
- `run_id`: unique 128-bit ID generated once per process execution.
- `git_commit`: exact source commit; must be captured from the running build.
- `config_snapshot`: complete explicit, JSON-safe effective configuration.
- `config_hash_sha256`: SHA-256 over canonical JSON (sorted keys, compact UTF-8).
- `config_id`: readable label derived from the first 12 hash hex characters.

The configuration snapshot must contain effective values after all environment
overrides and wrapper assignments. It must not contain passwords, tokens,
account credentials, or other secrets. A config hash is only meaningful if the
snapshot is complete and sourced from the actual runtime values.

## Position linkage

A `POSITION_LINKED` evidence event joins:
- run identity: run_id, runner_id, runner_version, git_commit;
- config identity: config_id and config_hash_sha256;
- observed broker identifiers: position_id, order_ticket, deal_ticket;
- symbol and magic;
- broker comment as an explicitly untrusted correlation hint.

The short MT5 comment token is `S2L:<run-id-prefix>:<config-hash-prefix>`.
It is not authoritative: brokers can truncate, rewrite, or omit comments.
The append-only local evidence log is the primary link source.

## Evidence integrity

- Run manifest is create-once; an existing path is never overwritten.
- JSONL events are append-only and hash-chained with sequence numbers.
- Startup verification fails closed on malformed, truncated, reordered, or
  modified prior events.
- The prototype assumes one writer process per event log. Multi-process use
  requires an explicit lock/coordination design before integration.
- Files should be retained with the run artifacts and included in a SHA-256
  evidence manifest at run completion.

## Integration gates — NOT YET APPROVED

1. Confirm the actual effective config fields for each runner wrapper.
2. Capture the exact Git commit from build metadata; do not silently use
   `unknown` or the repository's current HEAD if it differs from running code.
3. Write the immutable run manifest and `RUNNER_STARTED` before any order path.
4. Link broker position identifiers only after they are observed from MT5
   acknowledgements/history; do not infer position_id from order_ticket.
5. Add recovery/reconciliation for partial fills, multiple deals per position,
   pending orders, netting/hedging behavior, and broker comment loss.
6. Add unit, mutation, and synthetic MT5-response fixtures.
7. Review event privacy, storage location, retention, and failure policy.
8. Only then propose a separate integration PR. No change to active V3.1 runner.

## Current limitations

- No MT5 dependency or terminal connection.
- No order send/modify/cancel calls.
- No live Runner imports.
- The helper accepts a caller-supplied config snapshot; it cannot prove the
  caller supplied every effective setting.
- The hash chain detects accidental/ordinary tampering but is not a digital
  signature against an attacker able to rewrite the entire file and recompute it.
- Broker history may not expose every historical SL/TP request/response. This
  provenance feature does not solve missing broker-side records.
