# Independent AI audit handover — XAUUSD Strategy A / SP2L (2026-11-02)

This directory contains evidence for independent review only. It is **not** a request to merge, deploy or run any strategy. It adds documentation and evidence files only; it does not change code, configuration, datasets or existing research artifacts.

**Read first:** `INDEPENDENT_AUDIT.md`, the principal audit report. `HANDOVER_MANIFEST.json` lists every published file with its SHA-256, plus withheld files and the reasons for withholding them.

## Three separate branches

The two code changes have different base histories. They were kept on separate branches and were not forced into a single history.

| Branch | Parent (original base) | Published commit | Original local commit | Content |
|---|---|---|---|---|
| `audit/independent-ai-handover-20261102-runner` | `dc14a451669992d39bad559a125a7b0196e410e4` (tip of `research/strategy-a-v3-1-magic-clock-guard-20261102`) | `a6dad3ff7190c2cdece87082767aec6be931fec7` | `5c6ab4b7de7db320c9a0019a1c97500c2d9e08f6` | Runner gateway fix: 2 files |
| `audit/independent-ai-handover-20261102-factory` | `38f63c62f12e4e5c9fd6e13bc39202c9dc46f5f5` (tip of `research/v3-replay-evidence-export-20261101`) | `c40f29e927c90c68e72ac378375ae418bce7f912` | `95f3af891dbc0effd7037e925edc1735a3f88c68` | Factory snapshot fix: 4 files |
| `audit/independent-ai-handover-20261102` | `015c21e80a9d274e711f8a6597a5fc7c11f693ab` (`main`) | see Git history | — | Evidence only: this directory |

The Runner and Factory bases share merge-base `493eae922ce887946eb888ae7c55f3cf2d82b177`, but have since diverged substantially. Neither is the default branch.

### Why the published commit SHAs differ

The publishing connector can create branches and file commits, but cannot transfer local Git commit objects, and the audit sandbox has no Git push credential. The original SHAs therefore **could not be preserved**. Instead:

- each published commit has the exact original parent;
- each published commit's **tree SHA equals the original local tree SHA**: Runner `548cfac0259b2bab57032a3cca3780eb0eabd786`, Factory `051fa1b75ae962d255ae75fdc07e5abdaf369a43`;
- commit SHAs differ only because author, committer and timestamp metadata differ. Locally, the commits used “Independent Offline Audit”; on GitHub, they are attributed to the connected account at publication time.

The original commits are also reproducible exactly from `runner/patch/` and `factory/patch/`. Verify with:

```sh
git init -q --bare /tmp/v && cd /tmp/v
git fetch -q https://github.com/wareshgold/xauusd-strategy-a.git \
  refs/heads/audit/independent-ai-handover-20261102-runner:refs/heads/r \
  refs/heads/audit/independent-ai-handover-20261102-factory:refs/heads/f
git log -1 --format='%P %T' r   # dc14a451... 548cfac0...
git log -1 --format='%P %T' f   # 38f63c62... 051fa1b7...
```

## Layout

- `INDEPENDENT_AUDIT.md` — principal report, preserved unchanged. It was written before the Factory fix and therefore still lists B01 as unfixed; the fix is described in `factory/audit/FACTORY_FIX_README.md`.
- `COMMANDS.md` — exact Runner and audit commands with exit codes.
- `runner/patch/0001-fail-closed-exposure-inventory.patch` — exact original `git format-patch` output.
- `runner/source-at-commit/` — the changed gateway file and the full gateway test file at the original commit.
- `runner/probes/` — synthetic reproductions, results and the audit-only offline pytest guard.
- `runner/logs/` — raw pytest and probe outputs before and after the change.
- `runner/audit/` — static Runner audit and PR proposal.
- `factory/patch/0001-factory-single-snapshot-validation.patch` — exact original patch.
- `factory/source-at-commit/` — three of the four changed Factory files, including the 21-case synthetic test file. The fourth, `docs/V3_INTERACTIVE_RESEARCH_DASHBOARD.md`, is withheld from this directory; see “Withheld artifacts”. My exact change to it is in the Factory patch, and the full file is on the Factory branch.
- `factory/probes/` — race reproduction and offline guards.
- `factory/logs/` — raw Factory audit outputs and fix outputs (`fix-*.log`).
- `factory/audit/` — static Factory/data audit, fix README and change manifest.
- `data-evidence/` — independently measured dataset SHA-256s and integrity scans (`datasets.json`), the scanner, and source-code hashes. **No raw market data is included.**
- `discovery/` — remote refs, history and PR metadata recorded during the audit.
- `environment/` — interpreter/package versions, installation logs and test-safety scan.
- `original-bundle-manifests/` — SHA-256 manifests of the two ZIP bundles previously delivered privately.

## Reproducing tests offline

Use a fresh checkout. Do **not** install the real `MetaTrader5` package or run any runner, acquisition script or dashboard. Use Python 3.9 to match the recorded environment, or Python 3.11+ to adjudicate the three Factory `add_note` failures. Installing `pytest` (and `numpy` for one Runner test) is sufficient.

```sh
git clone https://github.com/wareshgold/xauusd-strategy-a.git && cd xauusd-strategy-a
# copy runner/probes/offline_guard.py and factory/probes/snapshot_offline_guard.py
# to a directory GUARD; edit snapshot_offline_guard.py's explicit root path to this checkout.

# Runner
git checkout audit/independent-ai-handover-20261102-runner
PYTHONPATH=$GUARD:$PWD:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p offline_guard \
  tests/test_live_mt5_gateway.py scripts/test_sp2l_v31_startup_recovery.py scripts/test_sp2l_runner_lock.py \
  scripts/test_sp2l_deal_lifecycle_dedupe.py scripts/test_sp2l_v3_1_trailing_bar_guard.py scripts/test_telegram_client_env.py -q
# recorded: exit 0, 45 passed (runner/logs/relevant-after.log)

# Factory
git checkout audit/independent-ai-handover-20261102-factory
PYTHONPATH=$GUARD:$PWD:$PWD/src:$PWD/scripts PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p snapshot_offline_guard \
  tests/test_v3_session_snapshot_binding.py tests/test_m1_integrity.py tests/test_v3_discovery_artifact_audit.py \
  tests/test_v3_exit_robustness.py tests/test_v3_exit_engine.py tests/test_v3_management_engine.py \
  tests/test_v3_research_api.py tests/test_v3_research_http.py tests/test_v3_research_session.py -q
# recorded: exit 0, 70 passed (factory/logs/fix-post-commit-tests.log)
```

To reproduce red-to-green behavior, run the new regression cases against each parent commit with the new test file applied; the recorded red runs are `runner/logs/exposure-regression-before.log` (6 failed) and `factory/logs/fix-regression-before.log` (6 failed). Full commands are in `COMMANDS.md` and `factory/audit/FACTORY_FIX_README.md`. Probe scripts use explicit sandbox paths; adjust only their root paths.

## Results summary (raw logs are authoritative)

| Run | Exit | Result | Raw log |
|---|---:|---|---|
| Runner full `tests`, baseline | 2 | 6 collection errors | `runner/logs/runner-baseline-pytest.log` |
| Runner safe subset, before/after | 1 / 1 | 97 passed, 7 failed / 107 passed, 6 failed | `runner/logs/runner-safe-subset-*.log` |
| Gateway regressions, before/after | 1 / 0 | 6 failed, 3 passed / 9 passed | `runner/logs/exposure-regression-*.log` |
| Final Runner-related suite | 0 | 45 passed | `runner/logs/relevant-after.log` |
| Factory, 113 test files | 1 | 653 passed, 3 failed (Python 3.9 lacks `Exception.add_note`) | `factory/logs/factory-broad.log` |
| Factory snapshot regressions, before/after | 1 / 0 | 6 failed / 21 passed | `factory/logs/fix-regression-*.log` |
| Factory selected synthetic suite after commit | 0 | 70 passed | `factory/logs/fix-post-commit-tests.log` |
| TypeScript dependencies | 1 | npm registry HTTP 403; no TypeScript tests run | `environment/npm-install.log` |

Known failures, incomplete tests and open findings are listed in `INDEPENDENT_AUDIT.md` §3–§6.

## Explicit statements

- **No backtest edge was established.** No market-performance experiment, validation or holdout was run; no Net R, profit factor, drawdown, win rate or confidence interval is claimed.
- **No MT5 or broker execution occurred.** MT5 was not installed or initialized; no broker connection; no order was created, modified or cancelled; no runner process was started, stopped or restarted.
- **No canonical strategy rules were changed.** Both changes are engineering safeguards. P-Gap classification, AB=CD anchors and fill semantics remain unresolved.
- No production configuration, dataset or existing evidence file was modified. Nothing was merged.

## Withheld artifacts

See `HANDOVER_MANIFEST.json` → `withheld`: compiled `.pyc` files and a pytest `__pycache__` (generated caches), and the two private ZIP bundles. The ZIPs are binary aggregates whose content files are published individually here; their per-file SHA-256 manifests are in `original-bundle-manifests/`. No raw M1 or tick datasets are published, only hashes and scan results. Raw files committed in the repository can be checked against `data-evidence/datasets.json`. Machine-local datasets were unavailable during the audit and are not included.

**Withheld for privacy:** a full copy of `docs/V3_INTERACTIVE_RESEARCH_DASHBOARD.md` at the Factory commit, SHA-256 `b790a4f40599f2219a0f6404392eb6029cc40bef82573d603319409fae68d821`. It contains a pre-existing local Windows filesystem path that includes a personal name, introduced by the repository owner in commit `9cbd1dfa9…`, not by this audit. That content is already public on `research/v3-replay-evidence-export-20261101`, and therefore is also present unchanged on the Factory branch because the full file was published there. It was not duplicated into this evidence directory. My change to that file is in `factory/patch/0001-factory-single-snapshot-validation.patch`, which does not contain the path.

Secret scan: every published file was scanned for credentials, tokens, Telegram configuration, account identifiers, personal paths and private URLs. Apart from the withheld documentation copy above, matches were limited to branch names, public PR URLs, guard keyword lists and quoted code identifiers. **No file was sanitized or edited**; all published evidence is byte-identical to the original files.
