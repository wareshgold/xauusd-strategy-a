# XAUUSD Strategy A / SP2L — Independent Offline Engineering Audit

Audit date: 2026-11-02. Scope: repository evidence, isolated clones/worktrees, synthetic fixtures and offline tests only.

## Executive decision

**Not production-ready. No independently established trading edge.** Useful pure replay and research-governance components exist, but the current runner and Factory are divergent lineages. The runner snapshot is missing two required modules, entry detection consumes forming bars, trailing bypasses mutation permission gates, and restart state is deliberately fresh rather than continuous. The Factory has meaningful provenance and replay safeguards, but interactive sessions are process-local, engine revision is caller asserted, protected-sample independence is not proved by different hashes, and a byte-binding race is reproducible.

I implemented exactly one production-independent engineering safeguard on an isolated local branch: **failed exposure inventory queries now block execution instead of becoming empty inventory.** No strategy geometry, thresholds, fill semantics, position-management policy, production configuration, dataset, existing evidence or remote branch was changed. This does not make the runner deployable.

### What actually ran

- Safe Python tests with no real MetaTrader5 package installed; an audit-only pytest plugin rejects network connections and removes credential-bearing environment variables without printing their contents.
- Pure config and AST-extracted trailing-function probes with synthetic data and an in-memory fake MT5 object; the runner entrypoint was never imported or run.
- Factory synthetic tests and a temporary-file race reproduction. No dashboard/server or trading process was started.
- Public Git reads and unauthenticated GitHub PR metadata reads only. No GitHub write, push, PR creation or merge.
- No real/demo broker contact, no MT5 initialization, no real order placement/modification/cancellation, no existing runner process inspection/control. Lock tests spawned and terminated only their own temporary synthetic lock-holder processes.

## 1. Repository and branch discovery

Discovery used git ls-remote, a fresh no-checkout clone, all remote branch refs/history, isolated checkout and a separate detached Factory worktree. The default branch was not treated as current research. See refs.txt, recent-history.txt and pull-requests.json for evidence.

| Workstream | Branch | Pinned commit | Meaning |
|---|---|---|---|
| Default | main | 015c21e80a9d274e711f8a6597a5fc7c11f693ab | Not the latest runner/Factory implementation |
| Runner audit base | research/strategy-a-v3-1-magic-clock-guard-20261102 | dc14a451669992d39bad559a125a7b0196e410e4 | Includes merged startup recovery PR390 and OS-lock PR391 |
| Runner dependency proposal | fix/v31-history-query-helper-import-20261102 | 60e198af680cb6ce2ff6280ea98705de1a2c6048 | PR386 open/draft, not merged into audit base |
| History semantics proposal | fix/v31-order-to-position-history-20261102 | d215c87a7f89869575f8cb0e40e127136c6caa17 | PR387 open/draft, not merged into audit base |
| Factory baseline | research/factory-candidate-lab-20261010 | 83939ec42e76ed362f510f974af88a3b0da2f630 | Includes PR376 repository pytest workflow |
| Factory source-authority proposal | research/fresh-holdout-source-authority-hardening-20261031 | d703e8cd3ce9fc488791d3da7576dde9741bf9e8 | PR377 open/draft; not baseline protection |
| Entry-freeze/data proposal | research/m1-integrity-gate-v3-entry-freeze-20261101 | 5f808175a40fe52ba95512ce42258a3bccd77910 | PR378 open/draft |
| Discovery/robustness proposals | research/v3-discovery-artifact-audit-20261101; research/v3-exit-robustness-20261101 | 3deebf6e3c3c75e652aaa31f61fdd8f31b2aa3bc; 01256593215176b766865cbd04f86bc252474bc3 | PR379/380 open/draft |
| Interactive replay proposal | research/v3-interactive-replay-engine-20261101 | 9cbd1dfa95c2e71fad612f6bc03e65ce766475bd | PR381 open/draft |
| Factory replay audit/test snapshot | research/v3-replay-evidence-export-20261101 | 38f63c62f12e4e5c9fd6e13bc39202c9dc46f5f5 | PR385 closed, not merged; used as isolated research snapshot, not shared baseline |
| Candidate evidence | research/rr4-act50-d40-evidence-snapshot-20261101 | 4ecb9fdf289fbaf99b311379c30251b45fe1f62e | PR384 open/draft; identical Git tree to 38f63c62 at audit time |
| This local implementation | audit/offline-independent-20261102 | 5c6ab4b7de7db320c9a0019a1c97500c2d9e08f6 | One local commit atop dc14a451; not pushed |

PR388/389/390/391 are merged into the runner lineage, not main. PR386/387 remain drafts despite containing missing dependencies. GitHub PR states were read directly during this audit, not inferred from filenames. A GitHub API merge_commit_sha on an unmerged PR is not evidence of a completed merge. Runner/Factory merge-base is 493eae922ce887946eb888ae7c55f3cf2d82b177. No single branch was certified as the fully integrated system.

### Architecture and responsibilities

Runner lineage:
- scripts/sp2l_v3_1_rr4_act40_config.py: pure research detection, first trigger, SL/risk/4R target, trailing-distance helper and completed-bar-after-position guard.
- scripts/run_sp2l_v3_1_xauusd_forward_test.py: wrapper monkey-patching the shared forward loop with RR4/ACT40 policy, clock/ownership/expiry/lifecycle isolation, startup recovery and completed-bar trailing.
- scripts/run_sp2l_author_replica_multi_symbol_forward_test.py: polling, signal keys, execution routing, event/state writes, notification retry, pending and position lifecycle.
- scripts/live_mt5_gateway.py: approved-payload parsing, exposure/permission/broker-distance checks and submission adapter. Tested here only with fakes.
- scripts/sp2l_v31_startup_recovery.py; sp2l_runner_lock.py; sp2l_deal_lifecycle_dedupe.py: owned active inventory recovery, OS-backed singleton locking and per-process event claims.
- TypeScript src/domain, src/backtest and research/harness are distinct domain/backtest/source-fixture paths. Their tests do not certify the Python wrapper.

Factory baseline and replay snapshot:
- src/strategy_factory/models.py, sp2l_manifest.py, source_ledger.py, source_gate.py, compiler.py: research identities, unresolved questions and canonical/source gates.
- datasets.py, dataset_provenance.py, usage.py, test_contract.py: raw artifact identity, roles, usage/isolation contracts. Registry/usage state is in memory.
- jobs.py, runs.py, execution.py, acceptance.py, runner.py, research_provenance.py: job/run/adapter/receipt/evidence provenance chain.
- orchestrator.py, worker_state.py, job_events.py, recovery modules: operational journals, interruption evidence and recovery planning; not strategy approval.
- validation_factory.py, robustness_factory.py, stability_factory.py, holdout_factory.py and handoff modules: staged evidence-bound research handoffs.
- m1_integrity.py and frozen_entry_population.py: M1 schema/hash/chronology/quality and already-frozen candidate import.
- v3_exit_engine.py and v3_management_engine.py: pure replay over fixed entries. No entry detection, MT5 or canonical decisioning.
- v3_research_session.py, v3_research_api.py, v3_research_http.py: provenance-bound local research sessions/API/catalog and allowed parameter experiments; no server started here.
- statistics.py and scripts/audit_v3_exit_robustness.py: descriptive uncertainty and exploratory time/sensitivity/multiplicity diagnostics.

## 2. Evidence classification

Here, Source-confirmed means **recorded as source-confirmed by the repository's preserved source reconstruction**, not newly authenticated by this auditor against all primary video/media. No new canonical adjudication occurred.

| Category | Claim/rule or artifact | Supporting evidence and boundary |
|---|---|---|
| Source-confirmed | Spike → correction → Leg 2; two legs expected to match in magnitude; AB=CD conceptual analogy | docs/research/SP2L_F14_ABCD_SOURCE_RESOLUTION_CHECKPOINT_20260926.md:9-16,31-37. Does not specify machine anchors/tolerance/TP projection. |
| Source-confirmed | P-Gap means Pressure Gap, distinct from E-Gap; bullish adjacent non-overlap primitive | docs/research/SP2L_PGAP_SOURCE_CEILING_CHECKPOINT_20260926.md:7-19,42-53. Primitive is not the complete P-Gap classifier; bearish expression is a mirror with a stated primary-evidence limit. |
| Source-confirmed | Limit-order and pending-to-position concepts appear in source reconstruction | docs/research/SP2L_F11_PENDING_ORDER_LIFECYCLE_SOURCE_RESOLUTION_20260926.md:10-42,70-98. Exact fills, cancellations/replacements and spread are not resolved. |
| Implemented but not source-confirmed | Three directional bodies, non-adjacent gap +1.0, body multiplier 1.5, max risk 10, first later low/high, before-spike SL, TP4R, 0.4-price trail, TTL30, volume0.01 | scripts/sp2l_v3_1_rr4_act40_config.py:9-107 and actual wrapper trailing. Existence in code is evidence of implementation, not canonical truth. SL_ANCHOR metadata says spike but code uses before-spike. |
| Research-only | Frozen candidate exit/management sweeps; RR4 ACT40/ACT50 alternatives; M1 historical proxies | Replay session manifest is canonical=false, NOT_VALIDATED (v3_research_session.py:146-169); discovery receipt explicitly exploratory/in-sample. No winner promoted. |
| Diagnostic-only | Gap/integrity counts; candidate-vs-observed reconciliation; bootstrap/max-t and parameter neighborhood diagnostics | m1_integrity.py; docs/research/v3-exit-robustness-audit.md:23-48. These assess artifacts/model sensitivity, not validated signals or proof of edge. |
| Unresolved | Complete P-Gap roles/pressure/order classifier; exact AB=CD anchors/fields/tolerances; exact fill/touch/penetration, cancellation and execution ordering | P-Gap checkpoint:21-40,68-78; F14 checkpoint:39-64; F11 checkpoint and intrabar forensic report. No formula/geometry invented. |
| Missing evidence | Referenced tick bytes/manifests, exact newer 30-day M1 and 462-entry CSV, full local discovery artifacts, independent engine attestation, untouched-sample exposure ledger | Factory audit sections 4-7; local discovery receipt:15-21 explicitly says underlying bytes are not uploaded. Reported hashes are not independently verified available inputs. |

Engineering fixes/proposals in this audit do not enter the Source-confirmed strategy category. They are software safety and reproducibility proposals.

## 3. Engineering findings

All runner line references below are at dc14a451 unless stated otherwise. Factory replay refs are at 38f63c62; Factory baseline refs are at 83939ec4. Full runner and Factory static audit appendices provide additional mechanisms and test recommendations. A static finding is not claimed to be a broker incident.

| ID/severity | Exact reference and reproduction | Expected → actual | Fix / regression / status |
|---|---|---|---|
| A01 Blocker | V3.1 runner:29-31; git tree lacks sp2l_history_query_failure_log.py. Examine tracked local import closure. | Clean checkout resolves required helper → module absent, entrypoint cannot import with external dependencies present. | Integrate reviewed PR386 dependency and clean-tree import-closure test. Not fixed; absence verified, runner not imported. |
| A02 Blocker | V3.1 runner:324-336; tracked IDs cause import of absent sp2l_tracked_deal_history before try block. | Recovered inventory can reach lifecycle polling → missing helper aborts path. | Review PR386/387 composition; first-poll tests with recovered pending/position/new pending. Not fixed. |
| A03 High | shared runner:377-381,1246-1251; active config:65-107. Synthetic bars end with provisional low106.5 then104 at same timestamp240. | Completed-bar research geometry stable → candidate entry changes with forming-bar poll snapshot under same key. | Explicit completed-input boundary/parity, both directions and intrabar revisions. Reproduced in runner_synthetic_probes.py; not fixed because a policy change needs explicit research contract. |
| A04 High | V3.1 runner:52-110. Extract function AST, stub original monitor/MT5, supply eligible owned position, disable both flags. | Disabled permission/account gate means zero mutations → fake order_send called once, no current-account gate. | Shared deny-first predicate for every mutation, flags/account-switch/missing-account tests. Reproduced; not fixed. |
| A05 High | gateway base:134-154,228-231. Either positions_get/orders_get returns None with valid other inputs. | Unknown exposure blocks → None became empty and proceeded toward submission. | Implemented exception + explicit EXPOSURE_INVENTORY_UNAVAILABLE result before market access; nine cases added. Patch refs: gateway:134-167,241-249; tests:113-155. Six red cases before; all nine green after. |
| A06 High | shared runner:1250-1251,1288-1299. Supply candidate key sequence A/B/A, with no current exposure. | Prior event identity is not submitted twice → only last key is remembered; third passes equality check. | Durable ID/watermark and explicitly separate retry policy; bounded poll A/B/A + sliding-window fixture. Static; not fixed. |
| A07 Medium | V3.1 runner:489-521; shared:1273-1276,1298-1305. First attempt has transient stale-clock block, next poll healthy same key. | Explicit retry/abandon policy → key is consumed regardless of transient pre-submit block. | Classify terminal vs retryable failure; uncertain submissions reconcile before retry. Proposed regression, not run/fixed. |
| A08 Medium | V3.1 runner:365-385 vs529-540,195-252. Use stated broker-offset convention with recovered pre-start entry and post-start close. | Same verified clock basis → raw deal times compared to UTC startup cutoff. | Normalize verified bases; +2/0/negative offset tests. Conditional on documented broker convention, not universal MT5 claim. Static; not fixed. |
| A09 Medium | shared runner:787-793,810,839; V3.1:220-223. Expired fake pending in dry-run returns ok=true,dry_run=true. | Simulation not recorded as broker cancellation → terminal CANCELLED marker suppresses later retry. | Separate simulated/skipped vs broker-confirmed marker, disabled→enabled transition regression. Static; not fixed. |
| A10 Medium | V3.1:227-252 vs shared:777-778,811-831. Offset+2, actual age31m. | Logged age equals eligibility age → shared evidence can record −89m. | Pass verified normalized age into cancellation event; TTL/log parity regression. Static; not fixed. |
| A11 Low | config:15 TP_R=4 vs shared runner:721 hardcoded TP(1R). | Label matches target → actual 4R price labeled 1R. | Neutral TP or derived label; fake-notifier render test. Static; not fixed. |
| B01 High | Replay session:51-77. Run factory_race_probe.py; change temporary M1 bytes immediately after genuine validator returns. | Hash/validation and replay use identical bytes → changed bars replayed while manifest retains old hash. | Single read immutable buffer validated/parsed once; reject source changes before publishing session. Reproduced; not fixed on separate Factory proposal branch. |
| B02 High gap | docs/V3_INTERACTIVE_RESEARCH_DASHBOARD.md:23-31; v3_research_api.py:23-28,39-49,53-64; datasets.py:89-98. Construct session, discard API process/object, attempt old handle. | Reproduce saved experiment after restart → handles/caches vanish; interactive archive is not durable by itself. | Append-only artifact bundle containing exact inputs/config/results/runtime/code revision; fresh-process replay regression. Documented limitation, not hidden implementation promise. |
| B03 High gap | v3_research_http.py:149-175; v3_exit_engine.py:314-345. Pass arbitrary nonempty engine_revision. | Revision bound to executable bytes → caller label accepted and hashed. | Measured Git tree/commit + dirty diff and engine/runtime dependency digests, distinguish declared vs measured identity; mismatch tests. Static design gap, not claim all Factory receipts are invalid. |
| B04 High | Baseline holdout_factory.py:43-46,64-113,138-164; snapshot.py:55-78. Trace caller frozen flag, self-hash validation and pre-read checks. | Source/freeze authority verified before protected read → no independent authority check in that baseline path. | Review/integrate PR377 trusted verifier; test blocked/self-asserted snapshot with file-open trap. Static; not executed against holdout. |
| B05 High gap | baseline holdout_factory.py:115-127; datasets.py:171-179. Re-encode/re-cut overlapping development rows to obtain different hash/ID. | Distinct sample/exposure proven → hash difference alone does not prove independence or unread status. | Authorized row/time-overlap/purge/exposure ledger; overlapping re-encoding fixture. No holdout opened. |
| B06 Medium gap | m1_integrity.py:104-110 vs acquisition CSV header timestamp,open,high,low,close,tick_volume,spread,real_volume. | Available downloaded M1 directly loadable → replay expects different epoch+ISO schema. | Explicit nonoverwriting deterministic adapter, raw+normalized hashes, validated source identity/clock. Schema mismatch established; do not silently substitute/convert. |

### State/recovery and determinism assessment

Recent recovery distinguishes None from valid empty inventory, scopes symbol/magic, validates owned tickets/types and persists recovered ownership before logging success. OS locking has real separate-process synthetic contention/owner-death tests. These are meaningful improvements.

However, V3.1 overwrites load_state with fresh state and disables reconciliation (runner:575-576). Only active inventory is recovered; positions closed during downtime need separate historical evidence. save_state uses in-place write_text (shared:568-580), not atomic replacement. Submission, external notification and persistence are not transactional. Trail attempts are per-process, only the latest completed bar is examined, and local TTL uses GTC pending orders whose expiration is not enforced while runner is down. None of this establishes durable exactly-once recovery.

Pure config functions are deterministic for identical valid ordered finite input. Full forward behavior is not demonstrated deterministic: forming-bar sampling, sliding-window identity rollback, fresh restart state, clock assumptions and polling gaps matter. Input chronology/uniqueness/OHLC/finite-value guards and end-to-end one-cycle wiring tests are missing. Passing helper tests and py_compile cannot detect all missing runtime imports.

## 4. Implementation and regression evidence

Local branch: audit/offline-independent-20261102. Base: dc14a451669992d39bad559a125a7b0196e410e4. Commit: **5c6ab4b7de7db320c9a0019a1c97500c2d9e08f6**.

Changed files only:
1. scripts/live_mt5_gateway.py — typed internal inventory-unavailable exception; distinguish None from empty; catch at execute_signal and return explicit block before market/request access.
2. tests/test_live_mt5_gateway.py — six None-query/mode cases, two owned-exposure cases, one empty/foreign control; repair pre-existing max-exposure fixture to use the gateway's own magic, matching the already-implemented ownership rule.

No retry policy, canonical rule, P-Gap formula, AB=CD anchor, fill model or configuration changed. Valid empty/foreign inventories retain prior behavior, owned exposure still blocks, query failures no longer authorize further execution. API-raised exceptions also prevent submission but are not newly classified into this result. Query success can still race external exposure changes; the patch is not a transaction or a complete gateway audit.

0001-fail-closed-exposure-inventory.patch is apply-ready commit evidence, not an upstream PR. PR_PROPOSAL.md describes suggested review scope. No remote write was attempted.

### Test results

Exact commands and environment prefix definitions are in COMMANDS.md; raw logs are included. Counts overlap across suites and must not be added as independent coverage.

| Run | Result | Exit |
|---|---|---:|
| Runner full existing tests before change | Collection stopped: six errors (five missing real-MT5/import dependencies, one Python3.9 union-annotation incompatibility) | 2 |
| Safe runner subset before change | 97 passed, 7 failed | 1 |
| New regression cases before production-code change | 3 passed, 6 failed, 10 deselected | 1 |
| Gateway after code change but before old-fixture repair | 18 passed, 1 failed (pre-existing unowned-object fixture) | 1 |
| Focused new cases after change | 9 passed, 10 deselected | 0 |
| Final gateway + recovery/lock/dedupe/trailing-helper/Telegram-env suites | 45 passed | 0 |
| Final broader runner subset, same six collection files excluded | 107 passed, 6 failed | 1 |
| Factory focused contracts/stages/session subset | 27 passed | 0 |
| Factory all 113 test files importing strategy_factory | 653 passed, 3 failed | 1 |
| V3 M1/discovery/robustness/exit/management/session/API/HTTP suite | 49 passed | 0 |
| Runner synthetic probes, final run | Geometry instability and fake trailing mutation demonstrated; missing helpers confirmed | 0 |
| Factory temporary-file race probe | Changed bytes accepted under old manifest hash | 0 |
| Modified gateway compile; git diff --check | Passed (compilation is not import/wiring verification) | 0; 0 |
| npm install --ignore-scripts --package-lock=false | Registry request returned HTTP403 for @types/node; no TS build/test run claimed | 1 |

Environment: Python3.9.25, Node24.22.1, npm11.19.1, isolated virtualenv; dependency versions recorded in environment.txt. No repository lockfile pins all dependencies. Factory's three failed fault-path tests call Exception.add_note, which requires Python3.11+. This is an environment/runtime mismatch; **not proof those tests fail under the intended Python3.11 CI**. Initial full-runner test failures include un-stubbed MT5 imports; installing/initializing MT5 was not used as a workaround.

Other final runner subset failures: two test_execution_mode_notices tests assume importable MetaTrader5; two V2 detector tests use exact binary-float equality; robustness matrix test expects rows absent from current matrix; monitor test expects fake tick content not present in rendering. These existed before this patch and were not hidden or speculatively repaired. See raw logs.

The first AST synthetic probe attempt failed due to missing TIMEFRAME_M1 on my fake object; adding that synthetic constant made the probe run. This was a fixture error, not repository evidence. Both logs are preserved. The available shell lacks rg (exit127); grep/Python inspection was used thereafter. No result is inferred from a failed command.

## 5. Dataset and research/statistical report

### Independently available and rehashed M1 bytes

Dataset paths below refer to the Factory replay worktree. Source timestamps are **labels as stored**; interpreting ISO Z labels does not independently validate broker/server clock convention. datasets.json contains exact hashes, counts, byte sizes and scan results for all eight acquisition CSVs.

| Dataset | Rows | Stored first → last | SHA-256 |
|---|---:|---|---|
| data/mt5-acquisition/xauusd-ecn-m1-2026-07.csv | 31,483 | 2026-07-01 01:00 → 07-31 23:57 | 482991df85c7143077ef3713c81f3c5ae14ae12311f6c03e3579f27f8048e34e |
| data/mt5-acquisition/xauusd-ecn-m1-2026-08.csv | 28,957 | 2026-08-03 01:00 → 08-31 23:58 | 8d9f4d9a82ff2fcbedfc8221ef62da1b4c518d037a000f09b8ec888077ca4a87 |
| data/mt5-acquisition/xauusd-ecn-m1-2026-09.csv | 17,069 | 2026-09-01 01:00 → 09-17 12:01 | 3b7212dc43f844807da120d89e6cbae9f63def4943fefdb003c54d630467cc2b |
| data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv | 28,815 | 2026-08-21 01:00 → 09-18 23:57 | 9df9a0ca0333c185396fb3407c7c816fd77a2ab57d88f71cea30a73462e75aa4 |

Basic independent numeric scans found zero invalid OHLC/nonfinite values and zero duplicate/nonincreasing timestamps in these CSVs. They contain 22/20/12/20 inter-row gaps over60s respectively. These gap counts are not missing-tradable-bar counts or a session-calendar certification. Monthly acquisition manifests themselves say AUDITED_FAIL with historical calendar UNVERIFIED; July/August/September list257/23/871 expected missing rows under their policy. Overlapping files are not independent datasets.

The Factory baseline DEV raw digest differs from committed LF bytes: converting LF→CRLF without modifying source reproduces the recorded DEV digest. This reconciles line endings, not exact raw-byte identity. Preserve raw and explicitly normalized digests separately. Independent reference/tick parity reports also record three spread mismatches and incomplete acquisition linkage. See factory-audit.md for all measured additional historical/availability hashes and limitations.

### Missing required newer research evidence

- Newer 30-day M1: repository document reports29,919 bars, 2026-09-24 07:57→10-23 23:57, SHA b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285. **Bytes absent here; not rehashed.**
- Frozen entry CSV: reported462 trade rows, SHA39ed87cd1f0be3e59b5f064b0bcf97a9787e5266df6e972aa07e5ea4d3608ab1. **Absent here.** Documentation distinguishes452 signal identities and ten duplicate-signal groups with different initial stops;462 is not automatically462 independent executable events.
- Local discovery receipt reports288 variants ×462 rows =133,056 trade rows and manifest SHA bea79456196e6e08b7186b1000eaec787d5ba6d697db0dd5c45bbb3322e49452. The receipt explicitly says underlying local bytes were not uploaded. This is a stored integrity receipt, not an independently reproduced experiment.
- Tick corpus: stored report claims10,817,858 quote rows and compressed SHA412a535b8d5f0413f329e5fde8a1f851591ee83c95fc25af38b287d6170a1347. **Not available/rehashed**; duplicate timestamps with different Bid/Ask imply sequence/multiplicity must be retained, not deduplicated. No tick fills inferred.

I did not substitute older July–September CSVs for the newer frozen-entry discovery inputs. No data download from MT5 was attempted.

### Experiment identity, metrics and uncertainty

**This audit's experiments were engineering fixtures, not market-strategy tests.** Real market observations were inspected for integrity only. New market trades=not generated; netR/winrate/PF/drawdown/CI/p-value=not estimated. Synthetic outputs have no market-performance interpretation. Engine snapshots for tests were the exact runner/replay commits above; engine-file digests are in source-hashes.json. Exact synthetic inputs/configurations are in probe scripts and committed tests.

Existing older RR2/Trail4 artifact reports1,522 signals,1,455 decisive,67 ambiguous,+527.28R,PF10.42 without modeled costs. These are **repository-reported, not rerun here**; complete input/code identity is absent. The historical backtest updates a stop using a bar's favorable extreme before testing the same bar's adverse extreme (scripts/run_sp2l_v3_xauusd_backtest.py:78-103), so OHLC ordering can produce path-sensitive profits beyond its explicitly flagged ambiguity. A constant-cost matrix and old weekly uncertainty results are described in factory-audit.md, not promoted to fresh evidence.

The newer replay engine improves the stated research proxy: skips entry-bar exits, marks open gaps and same-bar SL/TP ambiguous, applies completed-bar trailing on the next bar, and does not invent spread/slippage/commission (v3_exit_engine.py:44-53,93-139). These are explicit research semantics, not source-confirmed fills. It supplies paired fixed-entry comparisons, distribution and drawdown summaries, but uncertainty remains conditional on unresolved/missing outcomes and the assumed proxy.

Documented robustness design includes four chronological slices, parameter neighbors and common calendar-block max-t resampling over the288-way search. Missingness/studentization corrections require p-values to be recomputed. No corrected empirical p-value or confidence interval was independently available. A block bootstrap diagnostic is not a universal guarantee under dependence, regime shifts or informative missingness.

### Leakage/selection concerns

Repeated selection over288 exits; old81-way parameter sweeps; September repeatedly inspected/used as validation; overlapping raw windows;452 unique signals vs462 rows; conditional decisive-only statistics; intrabar execution/order ambiguity; no measured full costs; unresolved clock/calendar and source geometry; and missing exact historical input/engine lineage. Different filenames/hashes and passing provenance tests do not prove independence or lack of prior exposure.

### Required workflow stage disposition

| Ordered stage | This audit's disposition |
|---|---|
| Repository/branch discovery | Completed; pinned separate runner/Factory histories and PR status. |
| Architecture/source audit | Completed within reported snapshots; source meaning left unresolved where documented. |
| Dataset/evidence audit | Available bytes audited; required newer M1/entry/tick/discovery originals missing. |
| Synthetic fixtures | Completed for exposure gates; geometry/trailing and provenance-race probes; existing relevant tests run. |
| Deterministic engineering implementation | One fail-closed gateway fix committed locally; no strategy policy invented. |
| Automated tests | Results above; no claim all suites green. |
| Development market experiments | **Blocked for the intended newer frozen-entry run:** exact input bytes/provenance unavailable; no unrelated substitute. Synthetic engineering tests are not this stage. |
| Untouched validation | **Not run/locked:** upstream evidence/freeze incomplete and untouched exposure not established. |
| Robustness/stability market analysis | Existing methods/evidence audited, synthetic tests run; no new empirical run or p-value. Dependent on exact verified inputs/development results. |
| Fresh holdout | **Not accessed or run:** prerequisites do not justify it; no promotion or production recommendation. |

## 6. Direct final assessment

1. **Can the current runner be reliably tested offline?** Pure/config/gateway/recovery/lock components yes, using fakes; the current exact entrypoint is not a self-contained runnable offline target. Missing helpers, import-time wiring, mutable broker-dependent loop state and incomplete one-cycle integration fixtures prevent certification. No successful strategy execution is claimed.
2. **What prevents safe/reproducible execution?** Missing local dependencies, forming-bar/clock/identity inconsistencies, trailing permission bypass, intentionally fresh restart state, nontransactional state/notification/submission, incomplete downtime lifecycle recovery, model-vs-fill ambiguity and missing exact source-data/engine provenance. The exposure patch removes only one failure mode.
3. **Most important Factory engineering gap?** An enforceable immutable evidence boundary linking exactly validated data bytes, frozen entries, allowed config, measured engine/runtime identity, results and durable sample-exposure history. In particular, fix the demonstrated M1 reread race; then persist experiments and integrate verified authority before protected-sample reads. Interactive hashing alone is insufficient.
4. **What did I actually fix?** None inventory query results no longer become zero exposure; explicit block plus nine regressions and one old fixture repair, commit5c6ab4b7. Nothing deployed.
5. **What remains unresolved?** Complete P-Gap classification; AB=CD anchors/fields/tolerances; exact execution/fill/order-management semantics; full runner safety/restart behavior; newer data originals; acquisition/clock/calendar integrity; independent source authority; untouched split history; empirical selection/cost/dependence-aware validation.
6. **Evidence before production readiness?** Primary-source-complete adjudicated executable contract; integrated reviewed branch and clean import/one-cycle fault tests; all mutations fail closed; explicit restart/reconciliation/idempotency and atomic evidence policy; verified raw/tick acquisition manifests and chronology/quote sequence; immutable exact engine/runtime/config/dataset manifests; predeclared development/validation/robustness protocol with exposure/overlap controls and multiplicity/uncertainty/cost/path sensitivity; justified genuinely fresh holdout; independently reviewed results and explicit human production authorization. This audit does not authorize broker testing.
7. **Source-confirmed vs proposals?** Only the limited documented semantic concepts in the classification table are repository-source-confirmed. All audit fixes, regression contracts and proposed engineering safeguards are engineering work, not canonical strategy rules or validated trading signals.

## Deliverable map

- INDEPENDENT_AUDIT.md: principal report (this file).
- runner-audit.md and factory-audit.md: detailed static audit appendices, scoped to their stated base commits. Their statements that the sub-auditor ran no tests refer only to those static passes; this principal report records tests subsequently run by the orchestrating audit.
- COMMANDS.md, environment.txt, raw test logs: actual commands/results and runtime limitations.
- datasets.json, dataset_inventory.py: independently scanned acquisition bytes; source-hashes.json: exact inspected code digests.
- runner_synthetic_probes.py and runner-synthetic-results.json; factory_race_probe.py and factory-race-results.json: runnable synthetic reproductions, no real broker/API.
- refs.txt, recent-history.txt, pull-requests.json: discovery evidence.
- 0001-fail-closed-exposure-inventory.patch and PR_PROPOSAL.md: local change/review proposal.

No dataset, local secret/config file, account information or runtime trading journal is included in this audit bundle. All proposals remain unmerged.
