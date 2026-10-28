# SP2L Factory Lifecycle / Provenance Audit — 2026-10-28

- Snapshot ID: `SP2L-FACTORY-LIFECYCLE-PROVENANCE-AUDIT-20261028`
- Repository: `wareshgold/xauusd-strategy-a`
- Work branch: `research/factory-candidate-lab-20261010`
- Branch base observed via current open PR #352/#353: `8471b175f71e3af650babe52720d5a163a0bb61d`
- Scope: GitHub-source review only; no local files, runtime journals, MT5, or forward tests accessed or modified.

## Current remote/PR/CI evidence

- #352 `docs/factory-journal-quarantine-disposition-20261026`, head `ffb22153cfe2a04d10e547101971116d0333315d`, open Draft. Runs: Factory Research Tests #808 SUCCESS; SP2L forensic deterministic checks #466 SUCCESS.
- #353 `research/factory-tick-gate-fixtures-20261026`, head `9d6ee131075101179c2b45cb4fd78ac0491b5c2f`, open Draft. Runs: Factory Research Tests #1040 SUCCESS; SP2L forensic deterministic checks #578 SUCCESS.
- #334 `fix/factory-persisted-lifecycle-append-guard-20261021`, head `e732d99d686715aa89b050ded47b787bad2ee367`, open non-Draft. Its base recorded by the PR API is stale (`cd48a52b...`) relative to #352/#353 (`8471b175...`); do not treat its patch as present on the Factory base without an explicit diff/rebase review.
- #348 is closed/merged at `525ce1eb919f80265a79ad9af0b8afac398e19db`; the handoff snapshot says journal isolation tests were added to the workflow.
- Both workflows passed on the recorded Factory base `8471b175...` (runs #807 and #465). This confirms only the exact recorded commits; it does not certify any local runtime evidence.

## Non-mutating lifecycle finding

The base-branch `src/strategy_factory/job_events.py` parser validates JSON schema, event fingerprint and contiguous sequence, but those structural checks alone do not reject a semantically impossible lifecycle history such as repeated `COMPLETED` for the same job. The worker/journal audit code has diagnostic handling for `TERMINAL_CONFLICT_REVIEW_REQUIRED` and `LIFECYCLE_CONFLICT_REVIEW_REQUIRED`; diagnostic detection is not historical repair and must remain non-mutating.

PR #334 contains a persisted-append transition guard in its own head: `QUEUED → DISPATCHED → (COMPLETED | FAILED)`, with a single terminal event and stable job fingerprint. It is not merged, and its presence on that PR head does not establish that the current Factory base enforces the guard. Even if adopted, it protects future persisted writes; it cannot identify the historical journal writer or validate old history retroactively.

Required historical disposition remains: preserve original bytes, record SHA-256/size/line count from a read-only snapshot, report duplicate terminal events and per-job transition conflicts in a separate new artifact, and require human review. No repair, truncate, replay, or rewrite.

## End-to-end provenance review — current evidence and remaining gaps

- **Fresh Holdout:** the handoff contract carries dataset artifact identity/hash and a validated ResearchRecord, but this review has not established that every entry point enforces the holdout boundary or rejects all tuning-derived artifacts.
- **Handoff:** `handoff.py` defines explicit permitted routes and a fingerprinted handoff record. This is useful provenance structure; it does not by itself prove upstream source resolution or execution semantics.
- **Gate:** `gates.py` exposes boolean-based `validation_gate` inputs (development, untouched validation, robustness, Fresh Holdout). These booleans can represent caller assertions; the function alone does not bind each assertion to immutable evidence, dataset/code/strategy revisions, or an independent holdout manifest. Treat PASS from this helper as a gate result, not as end-to-end provenance proof.
- **Session:** a full cross-check from session inputs to the exact accepted handoff, data manifest, and code/strategy identity was not proven by the files inspected in this pass. Keep this link OPEN pending focused code/tests.
- **Lifecycle:** the audit can flag lifecycle conflicts, and the proposed append guard can block invalid future persisted transitions; the historical journal remains untrusted pending separate audit.
- **Production:** no production authority was enabled or inferred. Synthetic test success is not broker-fill proof or statistical edge.

## Bounded next change

Before changing runtime logic, add a separate read-only journal audit/report path with synthetic fixtures for (1) duplicate terminal events, (2) invalid transition order, (3) stable job fingerprint, (4) structurally valid but semantically conflicting history, and (5) byte-for-byte unchanged source journal before/after audit. Report conflicts; never repair them. Then trace Session-to-Handoff/Gate identity binding and add fail-closed tests only for gaps proven by the current source.

## Safety statement

This snapshot is additive documentation. No historical journal, raw dataset, runtime, MT5 session, live Strategy A RR2/TRAIL4 runner, Strategy B forward test, or canonical SP2L geometry was modified. No production BUY/SELL decisions were generated.
