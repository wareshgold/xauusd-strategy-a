# SP2L / XAUUSD Strategy A — Project Status Snapshot

**Snapshot date:** 2026-10-21  
**Purpose:** Durable handoff and anti-repeat record. This is a research/status snapshot, not a strategy specification or trading instruction.  
**Repository:** [wareshgold/xauusd-strategy-a](https://github.com/wareshgold/xauusd-strategy-a)

## 1. Operating principles — do not weaken

- Research-first and evidence-first. Source meaning outranks backtest performance.
- Only source-confirmed rules may become canonical. Unresolved geometry remains explicitly unresolved.
- Do not invent the P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules.
- Workflow: **SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION**.
- AI may assist research, engineering, validation, documentation, and analytics; it must not autonomously define canonical rules or issue production BUY/SELL decisions.
- Preserve evidence. No `git reset`, `git clean`, broad cleanup, mass staging, overwriting reports/snapshots, raw-source edits, or unrelated branch changes.
- Current user priority: Factory / Candidate Lab / StarNet and source/strategy research. Do not change the live Forward Runner or trailing logic without a specific request.

## 2. GitHub work in progress

### PR #337 — read-only tick dataset audit
- URL: https://github.com/wareshgold/xauusd-strategy-a/pull/337
- Branch: `research/xauusd-tick-dataset-offline-audit-20261021`
- Base: `research/factory-candidate-lab-20261010`
- State at snapshot: **open, Draft, unmerged**.
- Head reported by GitHub on 2026-10-21: `1b2b9f1698c8c18edebf9518de617ffa28e80006`.
- Scope: offline integrity checks for compressed tick source + manifest; report output must be new; source is read-only; no MT5 or runner interaction.

### PR #338 — repeated timestamp profiler
- URL: https://github.com/wareshgold/xauusd-strategy-a/pull/338
- Branch: `research/xauusd-tick-timestamp-profiling-20261021`
- Base: PR #337 branch `research/xauusd-tick-dataset-offline-audit-20261021`.
- State at snapshot: **open, Draft, unmerged**. It is stacked on #337; do not merge it independently of its prerequisite.
- Latest head verified by fetch: `366272690de6396bc198856d449fff2bd4c4e709`.
- Files added: `scripts/profile_xauusd_tick_timestamps.py`, `tests/test_profile_xauusd_tick_timestamps.py`.
- It profiles in original row order; does not sort, deduplicate, repair, or write the source; report path must be new.

### Important branch reconciliation item
- The latest locally reported Factory worktree was `research/factory-candidate-lab-20261010` at `5c9f6fe2`, with untracked runtime/artifact evidence preserved.
- GitHub PR #337 currently reports its base branch SHA as `ea35b682ef12592366e4557fc99f1d03aa63930c`.
- These references do not match. Before updating Factory or creating another stacked change, compare local HEAD, remote branch HEAD, and untracked/modified evidence. Do not reset, clean, or overwrite anything to force alignment.

## 3. Tick dataset — known evidence

Source and manifest (local paths previously used):
- `data/raw/ticks/xauusd-ecn-ticks-20260821_20260919.csv.gz`
- `data/raw/ticks/xauusd-ecn-ticks-20260821_20260919.manifest.json`

The source and manifest must remain unchanged. Existing audit outputs are evidence and must not be overwritten:
- `D:\\Mirzaei\\Private\\1\\factory-audit-output\\xauusd-ticks-audit-20261021-verified.json`
- `D:\\Mirzaei\\Private\\1\\factory-audit-output\\xauusd-ticks-audit-20261021-timestamp-review.json`
- `D:\\Mirzaei\\Private\\1\\factory-audit-output\\xauusd-ticks-timestamp-profile-20261021.json`

Audit/profile facts recorded from the acquired dataset:
- CSV rows: **10,817,858**; manifest SHA-256, file size, and row count matched in the audit.
- Invalid `time_msc`, invalid `time_utc`, UTC-vs-`time_msc` mismatch, missing/invalid Bid/Ask, crossed quotes, and adjacent out-of-order transitions: **0** each.
- Repeated timestamp groups: **7,429**.
- Groups with multiple distinct valid Bid/Ask pairs: **6,895**.
- Duplicate rows whose Bid/Ask differs from the first occurrence: **11,349**.
- Maximum group size: **15**.
- Repeated timestamps with differing quotes occur across all 21 represented trading dates.
- These are diagnostic observations. They do not, by themselves, prove corruption or establish event ordering.

**Interpretation / gate:** the integrity audit passed its recorded integrity checks, with timestamp warnings. Same-millisecond rows with differing quotes do not establish their internal event order. Do not use this dataset for tick-order-sensitive execution/fill validation until source semantics/order guarantees are established. This finding alone does not prove or disprove a Strategy A statistical edge.

## 4. Latest focused test attempt — be precise about what was verified

- Commit under review: `366272690de6396bc198856d449fff2bd4c4e709`.
- Two focused suites were invoked: `tests/test_audit_xauusd_tick_dataset.py` and `tests/test_profile_xauusd_tick_timestamps.py`.
- The isolated export test run returned **5 passed, 1 warning** in 0.56 seconds using `pytest -c NUL`.
- Caveat: the export was reconstructed with PowerShell `Set-Content -Encoding utf8`, which added BOMs/changed file encoding; `pytest.ini` then required bypassing with `-c NUL`. Thus this is useful test evidence but **not a byte-for-byte clean checkout verification**. A clean checkout/worktree run and confirmation that GitHub CI actually runs both new test files remain outstanding.
- The warning was pytest cache creation under `NUL`, not a test failure.

## 5. CI / review follow-up

Previously inspected workflows did not explicitly include both new files:
- `.github/workflows/factory-tests.yml`
- `.github/workflows/sp2l-forensic-checks.yml`

Re-check the current workflow definitions and PR checks. Ensure the two new test files are actually selected by CI. Do not treat unrelated green CI as proof that these tests ran.

## 6. Other source/data gates still relevant

- A prior July raw-M1 audit report `raw-m1-audit-2026-07-factory-rerun-20261015-2.json` was recorded as `STRUCTURAL_INTEGRITY_FAIL`: 31,483 rows, 22 unclassified timestamp gaps, zero invalid/duplicate/out-of-order rows, and a manifest SHA mismatch. Keep that source unapproved until reconciled; do not edit the raw source or manifest.
- Existing synthetic fixture tests and historical Factory test-suite passes are prior evidence, not a substitute for current validation or a fresh holdout.
- No canonical Strategy A geometry should be inferred from these data-quality investigations.

## 7. Forward Runner / trailing — out of scope for this work

- User previously reported the runner was active, logging trade lifecycle events to Telegram, and expiring pending limits after the configured time.
- The RR2/TRAIL4 configuration previously recorded: XAUUSD.ecn, 0.01 volume, TP 2R, trailing distance 4 pips where the environment defines 1 pip as MT5 point 0.01; the user asked whether 4 pips means $0.40. This is context, not a new verification of current live state.
- Do not restart, stop, reconfigure, or edit the runner/trailing code as part of the tick audit or snapshot task.
- Prior forward results and trailing counterfactuals must remain separated from source-confirmed canonical strategy rules.

## 8. Exact next actions

1. Reconcile Factory local vs remote HEAD and worktree evidence without destructive commands.
2. Verify PR #338 focused tests from a clean checkout, preserving all existing verification folders.
3. Confirm CI runs both audit and profiler test files; adjust only the narrow workflow scope if needed.
4. Review the real timestamp-profile report and retain the unresolved event-order semantics as an explicit blocker.
5. Keep #337 and #338 Draft/unmerged until prerequisites and review are complete.
6. Continue Factory/Candidate Lab and source-resolution work; do not touch live runner/trailing unless explicitly requested.

## 9. Snapshot provenance / limits

This record consolidates the project facts and command outputs available on 2026-10-21. Some live/local state is reported from earlier inspections and is explicitly labelled as such. Re-check Git refs, CI, and runner state before any operation that depends on their current values. This file is a handoff ledger, not a replacement for raw reports, commit history, manifests, or source documents.
