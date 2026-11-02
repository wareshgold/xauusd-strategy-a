# Factory single-snapshot validation fix — 2026-11-02

## Status and scope

Implemented and committed locally on a new isolated worktree/branch. No push, PR creation, merge, deployment, broker connection, MT5 import/initialization, runner operation or holdout access. Prior audit evidence and its ZIP/report remain unchanged.

- Base: 38f63c62f12e4e5c9fd6e13bc39202c9dc46f5f5 (the audited Factory replay research snapshot, not main).
- Branch: fix/factory-single-snapshot-validation-20261102
- Commit: 95f3af891dbc0effd7037e925edc1735a3f88c68
- Worktree: /agent/workspace/sp2l-factory-snapshot-fix
- 4 files changed; 239 insertions, 11 deletions (most added lines are synthetic tests/documentation).

## Defect and fix

Previously V3ResearchSession validated/hash-checked a file through validate_m1_artifact, then reopened the path to parse replay bars. A replacement could therefore cause the manifest hash and replayed bytes to disagree.

Now the session captures the M1 file once as immutable bytes. It passes that exact bytes value to validate_m1_artifact_bytes and parses the same value for both exit and management engines. There is no second M1 read in the session.

The new byte-oriented validator performs no filesystem access, requires immutable bytes and an explicit json/csv format, and retains existing schema, chronology, OHLC, gap and provenance validation. Existing path APIs remain available and delegate to the same byte validator. Raw BOM/CRLF bytes are not normalized before hashing.

Source references at this commit:
- src/strategy_factory/v3_research_session.py:50-80 — single capture, validation/hash check and replay parsing.
- src/strategy_factory/m1_integrity.py:89-121,208-255 — compatible path wrappers and immutable-byte dispatch.
- tests/test_v3_session_snapshot_binding.py — all21 new synthetic cases.
- docs/V3_INTERACTIVE_RESEARCH_DASHBOARD.md — snapshot consistency and limitations.

## Changed files

1. src/strategy_factory/m1_integrity.py
2. src/strategy_factory/v3_research_session.py
3. tests/test_v3_session_snapshot_binding.py (new)
4. docs/V3_INTERACTIVE_RESEARCH_DASHBOARD.md

change-manifest.json supplies final file SHA-256 digests. The patch contains the complete committed change.

## Regression evidence

Before the code change, all6 race cases failed: changed/invalid/removed files after capture, for JSON and CSV. Valid changed bytes altered the replay; corruption/deletion instead broke the reread. The pre-change log shows6 failed,10 deselected (five additional negative/API cases were added later).

After the change:
- All21 new tests pass (exit0).
- Selected existing/new synthetic integrity/discovery/robustness/replay/management/session/API/HTTP tests:70 pass (exit0), repeated after commit with the same result.
- git diff --check: exit0.
- Modified Python module compilation: exit0.
- git apply --check against the separate original Factory snapshot: exit0, no application or changes made there.
- Fix worktree final git status --porcelain: empty, exit0.

Counts overlap and must not be summed as independent coverage. Initial focused41-pass run occurred before five extra cases were added; the final70-test run includes all21 new cases. No full-repository, TypeScript, empirical strategy backtest or holdout result is claimed.

Cases cover:
- Source changed, corrupted or removed after capture, for both formats; exactly one M1 read and replay of the original captured buffer by both engines.
- Source changed before capture: expected-hash mismatch blocks before frozen-entry loading.
- Invalid captured data replaced by valid bytes after capture: original invalid snapshot still rejected.
- Capture failure wrapped as V3ResearchSessionError before entry loading.
- Byte/path validator report parity, retained malformed-OHLC rejection, immutable-buffer requirement, unknown-format rejection and standalone CSV path API compatibility.
- CSV fixtures explicitly use UTF-8 BOM and CRLF to exercise exact raw-byte hashing.

All new artifacts were created in fresh pytest temporary directories. Replacement, corruption and deletion affected only these synthetic fixtures. The selected existing test sources were inspected to confirm temporary/in-memory fixture use. No protected-stage test module was selected.

## Safety enforcement

The initial red and first focused run used the previous audit's no-network/no-real-MT5 guard. Final runs used the bundled snapshot_offline_guard plugin, which additionally rejects imports of MetaTrader5 and file opens under this worktree's existing data/, artifacts/ and runtime/ directories. No network access or protected file-open rejection occurred during the passing runs. No real MetaTrader5 package is installed.

## Exact commands and exits

Definitions for the literal sandbox paths used:

```sh
R=/agent/workspace/sp2l-factory-snapshot-fix
E=/agent/workspace/sp2l-factory-snapshot-fix-evidence
PY=/agent/workspace/sp2l-audit-venv/bin/python
```

Branch creation (exit0):

```sh
git -C /agent/workspace/sp2l-independent-audit worktree add -b fix/factory-single-snapshot-validation-20261102 /agent/workspace/sp2l-factory-snapshot-fix 38f63c62f12e4e5c9fd6e13bc39202c9dc46f5f5
```

Red regression, before code change (exit1):

```sh
cd "$R"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/agent/workspace/sp2l-audit-evidence:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_v3_session_snapshot_binding.py -k uses_captured_bytes -q --tb=short
```

Initial focused run (exit0;41 passed):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/agent/workspace/sp2l-audit-evidence:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_v3_session_snapshot_binding.py tests/test_m1_integrity.py tests/test_v3_research_session.py tests/test_v3_research_api.py tests/test_v3_research_http.py -q --tb=short
```

Final new regressions (exit0;21 passed):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p snapshot_offline_guard tests/test_v3_session_snapshot_binding.py -q --tb=short
```

Final selected synthetic suite, run before and after commit (each exit0;70 passed):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p snapshot_offline_guard tests/test_v3_session_snapshot_binding.py tests/test_m1_integrity.py tests/test_v3_discovery_artifact_audit.py tests/test_v3_exit_robustness.py tests/test_v3_exit_engine.py tests/test_v3_management_engine.py tests/test_v3_research_api.py tests/test_v3_research_http.py tests/test_v3_research_session.py -q --tb=short
```

Compilation and whitespace checks (each exit0):

```sh
python3 - <<'PY'
import py_compile
from pathlib import Path
out=Path('/agent/workspace/sp2l-factory-snapshot-fix-evidence')
for name in ('m1_integrity','v3_research_session'):
    py_compile.compile(f'src/strategy_factory/{name}.py',cfile=str(out/f'{name}.pyc'),doraise=True)
PY
git diff --check
```

Local commit, patch and non-mutating apply check (each exit0):

```sh
git add src/strategy_factory/m1_integrity.py src/strategy_factory/v3_research_session.py tests/test_v3_session_snapshot_binding.py docs/V3_INTERACTIVE_RESEARCH_DASHBOARD.md
git -c user.name='Independent Offline Audit' -c user.email='offline-audit@example.invalid' commit -m 'fix(factory): validate and replay one immutable M1 byte snapshot'
git format-patch -1 HEAD --stdout > "$E/0001-factory-single-snapshot-validation.patch"
git -C /agent/workspace/sp2l-factory-audit apply --check "$E/0001-factory-single-snapshot-validation.patch"
git status --porcelain
git diff --exit-code HEAD
```

Runtime: Python3.9.25, pytest8.4.2 in the existing isolated audit virtualenv. No dependency installations were needed this turn. For external reproduction, adjust the guard's explicit worktree root and environment path definitions to a separately pinned checkout. These commands record sandbox work; they are not instructions to operate a trading host.

## Deliberate limits

This is snapshot consistency, not filesystem immutability: a source change after capture is deliberately irrelevant to the established session. The manifest identifies the captured bytes; it does not promise that reopening the path later yields those bytes. Exact source-byte archival remains necessary for future reproduction.

The fix is scoped to V3ResearchSession M1 loading and its integrity APIs. It is not an OS file lock, a cross-file transaction, a scan of every other Factory loader for races, persistent experiment storage, engine-code attestation, protected-sample independence enforcement or resolution of strategy geometry/fill semantics. Entry CSV loading already hashes and parses its own single captured raw value and was not changed. No trading parameters, rules, results or canonical classifications were changed. No production readiness or validated edge follows from these synthetic results.
