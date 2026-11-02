# Commands and observed exits

Commands ran inside isolated audit checkouts. Paths below are sandbox paths, not instructions to operate any real trading host. No real MetaTrader5 package is installed. Tests were run with the audit-only offline_guard pytest plugin from this bundle. Real network connections are denied during pytest; external API modules are mocked by individual tests. No runner entrypoint was imported/executed by the custom probes.

## Setup/discovery

```sh
GIT_TERMINAL_PROMPT=0 git ls-remote --symref https://github.com/wareshgold/xauusd-strategy-a.git HEAD 'refs/heads/*' 'refs/tags/*' 'refs/pull/*/head'
# exit 0
GIT_TERMINAL_PROMPT=0 git clone --no-checkout https://github.com/wareshgold/xauusd-strategy-a.git /agent/workspace/sp2l-independent-audit
# exit 0
cd /agent/workspace/sp2l-independent-audit
git switch -c audit/offline-independent-20261102 dc14a451669992d39bad559a125a7b0196e410e4
# exit 0
git worktree add --detach /agent/workspace/sp2l-factory-audit 38f63c62f12e4e5c9fd6e13bc39202c9dc46f5f5
# exit 0
python3 -m venv /agent/workspace/sp2l-audit-venv
/agent/workspace/sp2l-audit-venv/bin/python -m pip install pytest openpyxl flask
# exit 0
/agent/workspace/sp2l-audit-venv/bin/python -m pip install numpy
# exit 0
npm install --ignore-scripts --package-lock=false
# exit 1: registry.npmjs.org @types/node HTTP403. TypeScript build/tests NOT run.
```

PR metadata was read using Python urllib.request, GET https://api.github.com/repos/wareshgold/xauusd-strategy-a/pulls/{number}, for376–391. The script exited0; selected non-sensitive fields are saved in pull-requests.json. No authentication token, write or PR creation was used.

## Exact test commands

For readability define the identical environment prefixes used in actual shell invocations:

```sh
PY=/agent/workspace/sp2l-audit-venv/bin/python
E=/agent/workspace/sp2l-audit-evidence
R=/agent/workspace/sp2l-independent-audit
F=/agent/workspace/sp2l-factory-audit
```

### Runner baseline

```sh
cd "$R"
PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests -q --tb=short
# exit2, 6 collection errors; runner-baseline-pytest.log

PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests -q --tb=short --ignore=tests/test_discover_mt5_research_symbols.py --ignore=tests/test_fixed_sltp_matrix.py --ignore=tests/test_live_readiness.py --ignore=tests/test_live_report_engine.py --ignore=tests/test_live_session_infra.py --ignore=tests/test_sp2l_continuous_poll_forensics.py
# exit1; 97 passed,7 failed; runner-safe-subset-before.log
```

### Red/green regression

After adding the nine new cases, before changing gateway code:

```sh
PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_live_mt5_gateway.py -q --tb=short -k 'unknown_inventory or valid_owned_inventory or valid_empty_and_foreign'
# exit1; 6 failed,3 passed,10 deselected; exposure-regression-before.log
```

After gateway code change, before repairing the old ownership fixture:

```sh
PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_live_mt5_gateway.py -q --tb=short
# exit1;18 passed,1 failed; gateway-after.log
PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_live_mt5_gateway.py -q -k 'unknown_inventory or valid_owned_inventory or valid_empty_and_foreign'
# exit0;9 passed,10 deselected; exposure-regression-after.log
```

Final relevant existing/new tests, after fixing the pre-existing unowned-object fixture:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_live_mt5_gateway.py scripts/test_sp2l_v31_startup_recovery.py scripts/test_sp2l_runner_lock.py scripts/test_sp2l_deal_lifecycle_dedupe.py scripts/test_sp2l_v3_1_trailing_bar_guard.py scripts/test_telegram_client_env.py -q --tb=short
# exit0;45 passed; relevant-after.log

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests -q --tb=short --ignore=tests/test_discover_mt5_research_symbols.py --ignore=tests/test_fixed_sltp_matrix.py --ignore=tests/test_live_readiness.py --ignore=tests/test_live_report_engine.py --ignore=tests/test_live_session_infra.py --ignore=tests/test_sp2l_continuous_poll_forensics.py
# exit1;107 passed,6 failed; runner-safe-subset-after.log
```

### Factory snapshot tests

```sh
cd "$F"
PYTHONPATH=$E:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_strategy_factory.py tests/test_v3_research_session.py tests/test_factory_run_contract.py tests/test_validation_factory.py tests/test_robustness_factory.py tests/test_stability_factory.py tests/test_holdout_factory.py tests/test_discovery_factory.py -q --tb=short
# exit0;27 passed; factory-subset.log

grep -lE '(from|import) strategy_factory' tests/test*.py > "$E/factory-test-files.txt"
# exit0;113 test files
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard $(cat "$E/factory-test-files.txt") -q --tb=short
# exit1;653 passed,3 failed due to missing Exception.add_note on Python3.9; factory-broad.log

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$E:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest -p offline_guard tests/test_m1_integrity.py tests/test_v3_discovery_artifact_audit.py tests/test_v3_exit_robustness.py tests/test_v3_exit_engine.py tests/test_v3_management_engine.py tests/test_v3_research_api.py tests/test_v3_research_http.py tests/test_v3_research_session.py -q --tb=short
# exit0;49 passed; v3-research-tests.log
```

### Audit-only probes and scans

```sh
python3 "$E/dataset_inventory.py"
# exit0; datasets.json. Initial scanner did not parse ISO timestamps; corrected scanner rerun is the authoritative output. No dataset modified.
PYTHONDONTWRITEBYTECODE=1 python3 "$E/runner_synthetic_probes.py"
# first attempt exit1 due to missing TIMEFRAME_M1 in synthetic fake, runner-synthetic-probes.log
# after fake corrected: exit0, runner-synthetic-probes-final.log
PYTHONDONTWRITEBYTECODE=1 "$PY" "$E/factory_race_probe.py"
# exit0; factory-race-probe.log. Writes only fresh temporary fixture files, not repository data.
```

Modified-code compile command, from runner checkout:

```sh
python3 - <<'PY'
import py_compile
py_compile.compile('scripts/live_mt5_gateway.py',cfile='/agent/workspace/sp2l-audit-evidence/gateway-compiled.pyc',doraise=True)
PY
# exit0; does not resolve imports or establish runner safety

git diff --check
# exit0
```

## Local commit

```sh
cd "$R"
git add scripts/live_mt5_gateway.py tests/test_live_mt5_gateway.py
git -c user.name='Independent Offline Audit' -c user.email='offline-audit@example.invalid' commit -m 'fix(gateway): fail closed when exposure inventory queries are unavailable'
# exit0;5c6ab4b7de7db320c9a0019a1c97500c2d9e08f6

git format-patch -1 HEAD --stdout > "$E/0001-fail-closed-exposure-inventory.patch"
# exit0
```

No git reset/clean, rebase, force push, merge or protected-branch update. Untracked test-created bytecode directories were left uncommitted; final tracked files are clean. No remote publication occurred.

## Reproduction portability

The probes intentionally contain explicit sandbox clone paths. To replay elsewhere, change only those root paths to separately pinned checkouts of the listed commits. Install only offline research-test dependencies, never MT5; retain the offline guard. The Factory broad suite should be rerun on Python3.11+ to adjudicate its three environment-specific failures. Do not execute any forward runner, live acquisition, broker or dashboard script as part of reproducing this audit. CLI snippets are evidence of sandbox execution, not a request that the repository owner operate a live machine.
