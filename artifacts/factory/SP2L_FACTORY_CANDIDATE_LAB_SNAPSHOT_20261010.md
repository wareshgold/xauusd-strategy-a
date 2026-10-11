# SP2L Factory Candidate Lab — Handoff Snapshot

**Snapshot date:** 2026-10-11  
**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/factory-candidate-lab-20261010`  
**Local checkout:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-factory-candidate-lab`  
**Preferred test interpreter:** `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`  
**Purpose:** authoritative continuation handoff. Read this before coding. Do not repeat completed work or treat diagnostic/backtest results as canonical source rules.

## 1. Latest user-verified state — 2026-10-11

The user reports the latest local working tree on the target branch and confirms:

- Focused reliability suite: **11 passed in 1.10s**
- Entire test suite: **752 passed in 6.89s**
- No test failures in either run.

Focused command:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest `
  tests/test_factory_orchestrator_terminal_telemetry.py `
  tests/test_factory_orchestrator_handoff_telemetry.py `
  tests/test_factory_orchestrator_journal_faults.py `
  tests/test_factory_orchestrator_dispatch_boundary.py `
  tests/test_factory_orchestrator_process_interruption.py -q
```

Full suite:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

Latest user-reported Git status:
```
## research/factory-candidate-lab-20261010...origin/research/factory-candidate-lab-20261010
?? runtime/factory_demo_status.json
?? runtime/factory_job_events.jsonl
?? runtime/factory_worker_status.json
?? src/strategy_factory/__pycache__/
?? tests/fixtures/__pycache__/
```
The user did not include `git log` output in the latest confirmation, so the next session must inspect `git log -8 --oneline` and `git status --short --branch` before making any changes. Do not guess the exact local HEAD from the test output.

## 2. Preserve user working-tree artifacts — mandatory

Do not delete, clean, reset, stage, or commit these untracked paths:

- `runtime/factory_demo_status.json`
- `runtime/factory_job_events.jsonl`
- `runtime/factory_worker_status.json`
- `src/strategy_factory/__pycache__/`
- `tests/fixtures/__pycache__/`

Do not use broad cleanup commands. Keep the current branch and prefer small, reviewable GitHub commits followed by the user's `git pull --ff-only` and local tests.

## 3. Work completed — do not redo

### Durable lifecycle / telemetry reliability
- Append-only lifecycle job journal and lifecycle-state audit coverage.
- Telemetry publication faults are isolated from durable job outcomes.
- Submit path: after durable `QUEUED` and queue mutation, a publication failure is recorded as `publish_after_submit` rather than bubbling up and inviting duplicate submission.
- Dispatch boundary: after durable `DISPATCHED`, remove the item from the in-memory queue before `worker.start`; a startup fault cannot lead to an accidental second dispatch. Recovery classifies an interrupted dispatch as `INTERRUPTED_REVIEW_REQUIRED`.
- Handoff path: a durable `HANDOFF_ACCEPTED` remains accepted/returned if telemetry publication fails; the fault is recorded as `publish_after_handoff`.
- Terminal telemetry helper now standardizes publication faults and records structured diagnostics in `telemetry_errors`. Completion publication failure must not hide `COMPLETED`; failure publication failure must preserve the original execution exception and diagnostic note.
- The terminal telemetry regression fixture was corrected to fault on publish call 3 (submit=1, dispatch=2, terminal event=3), not call 2. This correction is now covered by the user's latest **11 focused / 752 full** passing results.

### Journal integrity / recovery / queue reconstruction
- Journal integrity reads one immutable byte snapshot and hashes/validates the same bytes, avoiding a second-read TOCTOU inconsistency.
- Missing, unreadable, or invalid journals fail closed as `REVIEW_REQUIRED`; no auto-repair, truncation, replay, retry, or implicit requeue.
- Recovery report is deterministic and read-only. Interrupted dispatched work requires explicit manual reconciliation.
- Queue reconstruction is split into planning and separately approved application. Planning does not mutate the queue or execute work; applying a plan does not dispatch work.
- Recovery/lifecycle integration tests cover queued-only, interrupted dispatched, completed, failed, and conflicting terminal histories; verify deterministic classification and no automatic action, and verify journal bytes / worker state remain unchanged.
- Synthetic recovery/audit fixtures and immutable research result record coverage exist.

### Dashboard / telemetry boundaries
- Dashboard includes a read-only Job Journal Integrity panel with status, counts, path, SHA-256 and findings.
- Valid, missing, unreadable and invalid journal states have test coverage.
- Demo telemetry is separate from live worker telemetry.
- Dashboard audit/telemetry is observational; it must not mutate or repair the journal, dispatch jobs, or authorize trading.

### Provenance and protected research gates already established
- Synthetic handoff provenance coverage exists.
- Dataset identity validation and separation of Holdout versus Forward dataset identity are protected.
- Holdout → Forward boundary, certified Holdout SHA propagation/validation, frozen strategy revision and post-Holdout tuning prohibition must remain intact.
- Factory readiness/provenance gates must remain fail-closed. Engineering-test success is not a statistical-edge result.

### Previously user-verified baselines (historical context, superseded by latest total)
- 56 focused / 750 full passed before terminal telemetry correction.
- Latest is **11 focused / 752 full passed**, as stated above.
Do not rerun completed suites without a reason; only rerun if code changes, the relevant scope changes, or a discrepancy needs diagnosis.

## 4. Recent relevant commits

On branch `research/factory-candidate-lab-20261010`, recent changes recorded in the handoff trail include:

- `d06a4101` — `fix(factory): standardize terminal telemetry fault handling`
- `b28ec00c` — `test(factory): clarify terminal telemetry test setup`
- `0fc50d15` — `test(factory): target terminal telemetry publication fault`
- `269a6333` — `docs(factory): record terminal telemetry test correction`

Use `git log -8 --oneline` at the start of the next session to verify the exact current HEAD and ordering. Do not infer branch HEAD from this abbreviated list.

## 5. Hard constraints — do not cross these boundaries

- Current workstream is **Factory**, not Forward Runner. Do not alter or restart the live/demo forward runner as part of Factory work.
- Do not change the Holdout → Forward boundary, certified Holdout SHA semantics, Forward dataset identity, frozen strategy revision, or the prohibition on post-Holdout tuning.
- Do not invent Strategy A geometry or semantics: no guessed P-Gap formula; no guessed AB=CD anchors/tolerance; no invented fill/entry/exit semantics; no deciding whether F12 means touch, penetration, or close; no guessing the F10 stop anchor. Unresolved source geometry must remain explicitly unresolved.
- No AI-generated production BUY/SELL decisions and no new production authority.
- Passing tests prove software behavior only; they do **not** prove a reproducible statistical edge, certify the strategy, or authorize live trading.
- Keep research diagnostics distinct from canonical rules. Source-confirmed meaning outranks backtest performance.

## 6. Canonical research workflow

Follow this order and record evidence at each boundary:

1. **SOURCE RESOLUTION** — reconcile source notes and evidence; record confirmed, conflicting, and unresolved rules. Do not fill gaps by intuition.
2. **SYNTHETIC FIXTURES** — encode confirmed and unresolved edge cases as deterministic fixtures; test failure/ambiguity behavior before using market data.
3. **FROZEN GEOMETRY** — freeze only source-confirmed geometry and semantics, with provenance and version/hash. Unresolved items stay unresolved.
4. **DEV** — implement against the frozen contract; keep strategy logic, orchestration, telemetry, and dashboard responsibilities separated.
5. **UNTOUCHED VALIDATION** — run predeclared tests/data without tuning to their outcomes; preserve reproducibility and manifests.
6. **ROBUSTNESS/STABILITY** — evaluate sensitivity, regimes, costs, data quality, and stability without changing canonical rules to improve scores.
7. **FRESH HOLDOUT** — use a fresh, identity-verified Holdout only after the rules and strategy revision are frozen; validate SHA/provenance and forbid post-Holdout tuning.
8. **PRODUCTION** — only after evidence, approval and governance gates are satisfied. No production transition merely because a dashboard is green or tests pass.

## 7. Immediate objective and next actions

**Near-term delivery goal:** user asked for at least one complete Factory run, from start to finish, visibly represented in the existing dashboard by Monday (2026-10-12). Prioritize a narrow, observable end-to-end run over expanding features. This goal does not authorize weakening safety gates or faking completion.

Start next session with read-only inspection:
```powershell
git status --short --branch
git log -8 --oneline
git rev-parse HEAD
git rev-parse origin/research/factory-candidate-lab-20261010
```
Preserve all listed untracked files. If branch is behind, use only `git pull --ff-only` after confirming the branch and working tree; do not reset or clean.

Then inspect existing Factory dashboard, orchestration entry points, worker/demo mode, and current job lifecycle without rewriting the completed journal/recovery/telemetry protections. Map the minimum supported path for one safe **synthetic/research-only** end-to-end job:
- submit/queue,
- durable dispatch,
- worker execution,
- durable terminal result,
- evidence/provenance and dataset/strategy identity where applicable,
- read-only dashboard reflects the same run and terminal state.

Use existing supported entry points and fixtures. Do not invent an alternate lifecycle or add a bypass. If any stage is not wired end-to-end, add the smallest regression-tested integration/wiring change and record its exact evidence. The dashboard must show real persisted/derived state, not hard-coded progress or fabricated worker activity. Do not connect this run to production trading.

After any code change, run the smallest affected tests first and then the full suite. Report exactly what was and was not tested. Update this snapshot with the new commit and user-verified outputs when the end-to-end run is confirmed.

## 8. Next-session opening instruction

Read this entire snapshot first. Treat the completed-work list as done; do not repeat it. Inspect Git state before edits, protect untracked artifacts, and continue with the smallest path to a genuine end-to-end Factory run visible in the existing dashboard. Keep the source-first SP2L guardrails and the canonical workflow above in force.

## 9. New synthetic end-to-end wiring work — pending local validation

After the user fast-forwarded to snapshot commit `cd3dd265`, a narrowly scoped Factory integration path was added on the same branch. **Do not describe these latest changes as tested until the user runs the commands below.**

Commits:
- `0aeb8e97` — `feat(factory): add isolated synthetic end-to-end runner`
- `ac89af04` — `fix(factory): audit isolated demo job journal in dashboard`
- `3ddddd83` — `test(factory): cover isolated synthetic end-to-end dashboard run`
- `b59f4554` — `fix(factory): preserve existing runtime demo artifacts`
- `e8759b62` — `feat(factory): allow isolated demo telemetry paths`
- `12a4ccec` — `test(factory): protect pre-existing demo runtime artifact`

New runner: `scripts/run_factory_synthetic_e2e.py`
- Runs one deterministic synthetic fixture through the existing dataset registry, research runner, execution adapter, orchestrator, durable lifecycle ledger, research evidence/record, and explicit evidence-bound handoff.
- Uses only new isolated `runtime/factory_synthetic_e2e_status.json` and `runtime/factory_synthetic_e2e_job_events.jsonl` by default.
- Explicitly refuses to overwrite the live worker status, live Factory job journal, or the user-owned `runtime/factory_demo_status.json` artifact. Existing untracked runtime files are not to be overwritten.
- Labels output `SYNTHETIC_ONLY`, reports `production_decisions: 0`, and makes no strategy-edge claim. Its synthetic metrics are a software fixture, not SP2L performance evidence.
- Does not consume Holdout/Forward datasets, launch MT5, or create BUY/SELL decisions.

Dashboard adjustment: in `SP2L_FACTORY_DEMO=1` mode, the read-only journal panel audits the configured demo journal against the demo worker snapshot. New environment overrides `SP2L_FACTORY_DEMO_STATUS_FILE` and `SP2L_FACTORY_DEMO_JOB_EVENTS_FILE` let the user point the dashboard at the dedicated synthetic E2E outputs. In non-demo mode, the dashboard continues to audit the existing live journal. The new path does not overwrite or append to the user's pre-existing demo or live files.

New tests: `tests/test_factory_synthetic_e2e_run.py`
- Checks persisted `QUEUED → DISPATCHED → COMPLETED → HANDOFF_ACCEPTED` events, evidence artifact, completed worker snapshot, and a consistent journal audit.
- Checks demo dashboard journal isolation.
- Checks refusal to write to live Factory status/journal paths.

### Local validation requested

After confirming the current branch and preserving all pre-existing untracked files, run:
```powershell
git pull --ff-only
git log -6 --oneline
git status --short --branch

& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/test_factory_synthetic_e2e_run.py tests/test_factory_e2e_smoke.py tests/test_factory_dashboard.py -q

& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" -m pytest tests/ -q
```

If tests pass, run the synthetic integration once:
```powershell
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" scripts/run_factory_synthetic_e2e.py
```
Then start the dashboard in an isolated demo-mode terminal:
```powershell
$env:SP2L_FACTORY_DEMO = "1"
$env:SP2L_FACTORY_DEMO_STATUS_FILE = "$PWD\\runtime\\factory_synthetic_e2e_status.json"
$env:SP2L_FACTORY_DEMO_JOB_EVENTS_FILE = "$PWD\\runtime\\factory_synthetic_e2e_job_events.jsonl"
& "D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe" scripts/factory_dashboard.py
```
Open `http://127.0.0.1:8788/`. Verify the displayed worker/job/artifact matches the script's run ID and the Job Journal Integrity panel reports a valid, consistent demo journal. Do not treat a passing synthetic run as canonical research acceptance or a statistical edge.

The previous five user-owned untracked paths remain protected, including `runtime/factory_demo_status.json`. The synthetic run writes only the new `factory_synthetic_e2e_*` files. Do not modify `runtime/factory_worker_status.json` or `runtime/factory_job_events.jsonl`; the dashboard must be explicitly pointed at the new synthetic paths using the environment variables above.
