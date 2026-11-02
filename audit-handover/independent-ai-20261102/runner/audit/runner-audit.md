# Track A — independent Strategy A V3.1 runner audit

## Scope and method

- Audited clone: `/agent/workspace/sp2l-independent-audit`.
- Verified HEAD: `dc14a451669992d39bad559a125a7b0196e410e4`, requested `audit/offline-independent-20261102` snapshot. Initial Git status was clean.
- Method: read repository source, test source, documentation, Git tree and history only. **No tests executed; no runner imported or executed; no MT5 initialization, broker connection, process inspection/control, credential access, or network research performed.**
- The only authored file is this report, outside the audited clone. Account/credential/Telegram configuration values are intentionally absent.
- Findings below are **source-confirmed control-flow defects**, not observed broker incidents. Reproduction cases are proposed synthetic regressions, **not tests run during this audit**. Findings after A-01/A-02 are latent paths until the missing dependencies are supplied.
- No architecture rewrite is proposed. Fix recommendations are local gates, dependency completeness, state/key handling and focused tests.

## Executive conclusion

**Do not treat this commit as runnable or restart-safe on the strength of existing helper tests/compilation.** The committed V3.1 entrypoint imports a module absent from its tree, and the lifecycle path imports a second absent module. These are decisive packaging blockers. Independently, source inspection finds a forming-bar entry path; trailing that bypasses dry-run/runtime account checks; fail-open exposure queries; last-key-only duplicate protection; and restart/lifecycle timestamp mismatches. The recent recovery and OS-lock changes improve specific boundaries but do not establish end-to-end safety.

Priority:

| ID | Priority | Finding |
|---|---|---|
| A-01 | Blocker | Required top-level history log module absent from HEAD |
| A-02 | Blocker | Required tracked-deal history module absent; management aborts with owned inventory |
| A-03 | High | Entry detector consumes the live/forming M1 bar, then freezes the first intrabar geometry |
| A-04 | High | Trailing sends broker modifications despite dry-run flags; lacks per-modification Demo gate |
| A-05 | High | Exposure lookup failures become empty inventory and allow new submission |
| A-06 | High | Duplicate protection remembers only the last key, permitting an old key to reappear |
| A-07 | Medium | Execution-clock/transient submission failures permanently consume the candidate key |
| A-08 | Medium | Deal stale filtering compares broker/server timestamps with unshifted UTC start |
| A-09 | Medium | Dry-run pending expiry is marked CANCELLED and suppresses later real cancellation |
| A-10 | Medium | Pending-expiry evidence reports wrong age under nonzero server offset |
| A-11 | Medium | RR4 pending notification is labeled TP (1R) |

## Actual wiring and research boundary

The active candidate is **not** the old RR2/Trail3 monitoring profile. `scripts/run_sp2l_v3_1_xauusd_forward_test.py:12,42-49` imports `sp2l_v3_1_rr4_act40_config`, installs its detector functions into the shared runner, isolates state/event paths, disables the shared session restriction, and forces a 30-rate history fetch. `scripts/sp2l_v3_1_rr4_act40_config.py:9-23` fixes P-gap 1.0 price, body multiplier 1.5, maximum risk 10.0, TP 4R, activation/distance 0.40 price, volume 0.01, pending Limit and 30-minute TTL.

Detection (`...config.py:36-107`) is a three-candle directional body progression plus **non-adjacent** separation (`after.low > before.high + 1.0`, mirrored for sell); the first later lower-low/higher-high is the entry. Both directions use the **before-spike** candle extreme for SL (`:73,87`). `SL_ANCHOR="SPIKE_CANDLE_EXTREME_RESEARCH"` at `:20`, also shared-runner `:94`, is misleading metadata: it is not the middle/spike candle's extreme. TP is risk-based, not an executable AB=CD anchor model. Secondary entry is computed but never executed (`shared runner:1270`).

Do **not** report disagreement with canonical strategy as proof these research parameters are coding errors:

- `docs/research/SP2L_PGAP_SOURCE_CEILING_CHECKPOINT_20260926.md` distinguishes source-confirmed identity and an adjacent strict non-overlap primitive from an unresolved complete pressure/role/ordering classifier. It explicitly rejects universal `Low[t] > High[t-2]`, `low[1] > high[3] + 1`, and tuned fixed thresholds as canonical shortcuts. V3.1's 1.0/non-adjacent construction is a research hypothesis, not source-confirmed P-gap qualification.
- `docs/research/SP2L_F14_ABCD_SOURCE_RESOLUTION_CHECKPOINT_20260926.md` confirms two-leg/equal-magnitude concepts, **not exact A/B/C/D anchors, field choice, equality tolerance or executable TP projection**. Fixed 4R is not source validation of AB=CD.
- `docs/research/SP2L_F11_PENDING_ORDER_LIFECYCLE_SOURCE_RESOLUTION_20260926.md:10-42,70-98` supports Limit orders, refresh/replacement and pending-to-position conceptually, but leaves deterministic replacement/cancellation, exact fill/touch/penetration and spread semantics unresolved. TTL30/GTC behavior is an implementation policy, not a sourced universal rule.
- `docs/research/SP2L_INTRABAR_OUTCOME_SEMANTICS_FORENSIC_20260926.md:39-51,91-104` explicitly disallows deriving fill ordering from OHLC. Broker fills and deals must remain observed facts; a theoretical touch or candidate is not a fill.
- `research/snapshots/SP2L_V3_1_RR4_ACT40_RUNNER_SNAPSHOT_20261101.md:70-83` itself labels results in-sample M1 research with tick sequencing, costs and holdout outstanding. This audit does not validate its reported performance.

## Detailed findings and recommended regressions

### A-01 — V3.1 cannot import from this committed tree

**Evidence:** `scripts/run_sp2l_v3_1_xauusd_forward_test.py:29-31` imports and instantiates `HistoryQueryFailureLogGate` from `sp2l_history_query_failure_log`. Neither that file nor a package of that name exists in HEAD (`git ls-tree -r --name-only HEAD`; `git grep` finds only these references). The earlier shared-runner import does not provide the missing module.

History explains the distinction between local history availability and deployable snapshot completeness: commit `343cc2f4cc943b98eee2ebe9601906b678c4e11c` adds the file on another history line, but `git merge-base --is-ancestor 343cc2f4 HEAD` returned 1. It is **not in this audited commit**. An operator's unrelated local module/PYTHONPATH could mask this defect but would make a clean checkout non-reproducible.

**Reproduction to add:** clean-tree static local-import closure check and safe entrypoint import with stubbed MT5/notification modules; no initialization or file/network effects allowed. Assert the helper is available from the repository. A Python compilation-only check is insufficient because compilation does not resolve imports.

**Minimal remedy:** include the reviewed dependency in the same deployable lineage and add an import/packaging gate.

### A-02 — First lifecycle pass with owned inventory imports another absent dependency

**Evidence:** `scripts/run_sp2l_v3_1_xauusd_forward_test.py:324-336` returns early only with no tracked orders/positions, otherwise imports `DealHistoryQueryError` and `collect_tracked_deals` from `sp2l_tracked_deal_history`. That module is also absent from HEAD. The import occurs **before** its try/except at `:337`, which only handles the helper's query exception. The shared main loop has no per-symbol outer exception guard (`shared runner:1228-1307`); its finally releases the lock and shuts down MT5 (`:1308-1314`).

Startup recovery now deliberately populates those owned IDs (`V3.1 runner:445-471`; recovery helper `:72-73`), so an otherwise successful recovery of any active owned object leads directly to this failure on the first lifecycle pass. With initially empty inventory, an accepted pending order creates tracked IDs (`shared runner:1279-1285`) and exposes the failure next poll. Earlier management may run first; this is not a safe all-or-nothing startup preflight.

History: `60c64d8f945b69eb46a0bbda003581d4c0fb5546` adds the helper on another history line; ancestor check against HEAD returned 1. `23e16adb` later changes that external helper; neither availability nor its behavior can be credited to this tree.

**Regression:** stubbed single-poll integration with (a) recovered pending, (b) recovered position, (c) newly placed order. Require all lifecycle dependencies to resolve **before** any broker mutation; never test against real MT5. Empty-inventory-only startup tests will miss this.

### A-03 — Entry generation sees the forming bar and freezes a provisional low/high

**Evidence:** shared `rates()` at `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py:377-381` calls `copy_rates_from_pos(..., 0, count)`. V3.1 wrapper `:48-49` changes count to 30, not start position. The full result is passed without trimming at shared `:1246-1249`. Config `find_first_entry()` at `:65-97` scans through `len(candles)-1`, which includes bar 0/the last returned forming bar. `find_latest_candidate()` `:99-107` can therefore return its current extreme as entry. Timestamp/direction key (`shared:1250-1251`) suppresses later intrabar geometry revisions after the first attempt.

This differs from the explicit completed-candidate model in `scripts/run_sp2l_v3_xauusd_backtest.py:61-76`. The trailing path correctly fetches position 1, but that does not make **entry** detection completed-bar-safe.

**Concrete fixture (newest four rates, pad earlier rates as needed):** before O100/H101.1/L99.9/C101; spike O102/H106.2/L101.8/C106; after O107/H108.2/L106.9/C108; current forming O108.5/H109/L106.5/C108.6. Three setup bodies satisfy the code; low106.5 is already a BUY trigger, SL99.9, risk6.6, TP132.9. With ask108.7, the pending entry is placeable before this M1 closes. If the same bar later makes low104, the completed result's entry would be104, but the identical timestamp/direction key prevents reevaluation of the submitted106.5 geometry.

**Regression:** several polls in the same minute with changing bar-0 extremes: no candidate/submission until completion; then exactly one candidate using completed OHLC. Mirror for SELL. Compare offline completed-bar detection and forward input boundaries explicitly. This is a research-model determinism defect, **not an assertion that a canonical entry must occur on any particular candle**.

### A-04 — Trailing bypasses dry-run and per-request Demo checks

**Evidence:** `scripts/run_sp2l_v3_1_xauusd_forward_test.py:52-110` queries matching-magic positions, calculates an eligible completed-bar stop, and calls `mt5.order_send(request)` directly. It never checks `LIVE_TRADING_ENABLE`, `ALLOW_REAL_EXECUTION` or `account_info()` on this path. `_validate_execution_clock()` includes a Demo check at `:489-495`, but is attached only to `execute_candidate` at `:517-521`, not trailing. Main's account check (`shared:1157-1159`) is startup-only. Pending cancellation, in contrast, checks both flags and current Demo status (`shared:787-799`).

**Reproduction:** recover an owned BUY entry100, oldSL99, TP104, entry timestamp before eligible bar; bar high101; current bid101.2 and zero minimum stop distance. Set either execution flag false. `trail_positions()` still submits SL100.6. Separately return a non-Demo/missing current account after startup and the same trailing path still calls `order_send` if the terminal exposes a matching owned position. Actual mid-run account switching is a scenario to test, not an observed event.

**Regression:** parameterize both flags and current account mode/missing account across all mutation paths; `order_send` must never be called when blocked. Test recovered positions as well as new ones. Centralize only the small shared mutation permission predicate if helpful; no execution rewrite needed.

### A-05 — Poll-time exposure guard fails open on query error

**Evidence:** `scripts/live_mt5_gateway.py:134-154` converts `positions_get(None)` and `orders_get(None)` results to empty lists, then counts owned exposures. `execute_signal():228-231` checks that count, allowing processing toward actual `order_send` at `:341`. The new startup recovery correctly distinguishes None from empty (`scripts/sp2l_v31_startup_recovery.py:30-37`) but only at startup; it does not fix later gateway inventory failures.

**Reproduction:** startup succeeds; a later candidate arrives while a previous owned pending/position remains at the broker. Mock either/both current exposure queries as None, while tick/symbol/account permissions are otherwise valid. With default maximum one exposure (`gateway:52`), returned exposure zero permits a second submission despite unknown inventory. No claim is made that the broker will fill it; bypassing the client exposure cap is sufficient.

**Regression:** valid empty tuples may allow submission; None from **either** inventory query must return an inventory-unavailable block and make zero `order_send` calls. Include mixed successful/failed query results and foreign-magic objects.

### A-06 — Last-key-only dedupe permits reexecution of an earlier key

**Evidence:** shared loop `:1250-1251` only compares against `state['seen'][symbol]`; both successful and failed attempts replace this one value (`:1288-1299`). The V3.1 detector recomputes the maximum candidate from a **sliding 30-rate window** (`V3.1 runner:48-49`, config `:99-107`). It has no monotonic trigger watermark or set of all attempted IDs. A candidate's *setup* can expire from the window even while a different setup with an earlier trigger remains. The maximum can therefore move backward. Any key sequence A, B, A passes all three equality checks.

**Reproduction design:** two overlapping setups: older setup S1 has a later first trigger T1; younger setup S2 has earlier first trigger T2. When S1 ages out before S2, the latest candidate changes from T1 back to T2. If T2 was handled previously, its identity is handled again. Ensure T2/T1 are after session cutoff; mock no current exposure after previous cancellation/close. Even an exposure-blocked replay still makes duplicate candidate/order-attempt evidence and overwrites the last key.

**Regression:** drive deterministic find outputs A, B, A through a mock poll loop, including a sliding-window OHLC version of the case, and require at most one submission for each research signal identity. If strict chronological processing is intended, assert that the watermark never regresses. Make any deliberate retry policy separate from signal discovery.

### A-07 — Transient execution/clock failure consumes a signal permanently

**Evidence:** V3.1 `_guarded_execute_candidate()` raises on missing/stale/mismatched clock or non-Demo account (`:489-519`). Shared loop catches any exception (`:1273-1276`) then unconditionally marks the key seen in the failure branch (`:1298-1305`). The next poll skips the identical key at `:1251`, even if ticks, account or permissions have recovered. Exposure-blocked or unavailable-market submissions are also consumed this way.

**Reproduction:** candidate C is new; tick age121 seconds causes clock-block exception. Next poll age1 second with exactly the same candidate. The runner never retries C. In contrast, comments about failing closed/deferred cutoff may suggest recovery is possible; cutoff recovery (`V3.1:549-565`) does not recover keys lost at execution.

**Regression:** classify retryable guard/pre-submit failure versus deliberately terminal signal rejection. If the intended policy truly is one attempt regardless of transient failure, document and event-label permanent abandonment rather than silently implying a recoverable gate. Avoid blindly retrying uncertain broker submissions: first reconcile broker result/ownership.

### A-08 — Lifecycle stale cutoff is on a different clock from the deals

**Evidence:** V3.1 explicitly documents broker/server epochs for candidate timestamps and shifts the session cutoff (`:529-540`). Pending age similarly uses pinned server clock (`:195-200,227-252`). But lifecycle suppression uses `int(_RUN_STARTED_UTC.timestamp())` and compares raw `deal.time` directly (`:365-385`) with **no offset conversion**. Fresh startup state deliberately erases prior deal and observation markers (`:134-137,575-576`), and recovered owned positions cause their entry history to be queried.

**Reproduction under the runner's stated server-clock convention:** process starts at UTC12:00; broker offset+2. An owned position entered at UTC11:50 has raw deal timestamp13:50. It is pre-start but passes `13:50 >= 12:00` and can send an old OPENED notification on recovery, contradicting `:125-127,371-374`. With a negative offset, genuinely post-start deals can instead be marked stale and irretrievably added to `state['deals']`.

**Regression:** +2, 0 and negative offsets; recovered pre-start entry plus a genuine post-start close. Only the close should be newly delivered, without replaying historical entry. Normalize all lifecycle cutoff operands to one verified basis. **Caveat:** broker-specific MT5 timestamp convention must be verified offline against approved evidence; the defect is an internal inconsistency under the explicit convention already assumed by this runner, not an external claim that every MT5 server encodes epochs this way.

### A-09 — Dry-run expiry is treated as a confirmed cancellation

**Evidence:** V3.1 `_run_scoped_pending()` claims only confirmed cancellation suppresses retries and skips `ticket:EXPIRY_NOTIFIED:CANCELLED` (`:220-223`). Shared `_cancel_pending_order()` returns `{ok:True,dry_run:True}` with disabled flags (`:787-793`), sets `outcome='CANCELLED'` solely from `ok` (`:810`), and writes that exact marker (`:839`). Thus the V3.1 skip condition cannot distinguish simulation from cancellation.

**Reproduction:** expired owned pending, valid fresh clock, flags false; first poll records CANCELLED without removing anything. Enable flags later in the same process while broker order remains. Later expiry calls skip the ticket forever. Even without changing flags, logged cancellation is false as a broker fact.

**Regression:** dry-run should log simulated/skipped cancellation without confirmed terminal marker; real success alone creates it. Failed cancel remains retryable. Include transition from blocked/dry-run to allowed execution.

### A-10 — Cancellation age in evidence uses host UTC, not the age that triggered it

**Evidence:** V3.1 eligibility computes `(time.time()+server_offset - order.time_setup)/60` (`:227-252`), but the delegated shared `_cancel_pending_order()` recomputes `(time.time()-setup_ts)/60` (`:777-778`) and writes/displays this value (`:811-815,831`).

**Reproduction:** broker offset+2, true order age31 minutes, TTL30. Correct scoped eligibility cancels it; the evidence records approximately **-89 minutes**. At offset-2 it overstates age by120 minutes. This pollutes audit evidence even when cancellation itself was correct.

**Regression/remedy:** pass the already verified age or normalized now/clock basis into cancellation evidence; assert nonzero-offset TTL boundary and logged age agree. Never obtain a second permissive/guessed clock merely for display.

### A-11 — RR4 notification claims TP (1R)

**Evidence:** active config `TP_R=4.0` (`config:15`). V3.1 notification wrapper (`runner:35-40`) only substitutes display pip size, delegating unchanged text to shared `send_signal()`. Shared `:721` hard-codes `TP (1R)` beside the actual 4R price. The price is not changed; the descriptive claim is wrong. Retry delivery uses the same function (`shared:1235`).

**Regression/remedy:** derive the target-R label from active config/candidate risk, or use neutral TP wording. Render RR4 and an unrelated RR profile with fake notifier; assert labels match numbers. No message sending is necessary.

## Persistence, recovery and restart findings

### Improvements source inspection confirms

- `scripts/sp2l_v31_startup_recovery.py:30-73` distinguishes failed inventories from valid empty tuples, validates supported owned order types and positive IDs, and adds only exact symbol/magic ownership. It validates the supplied single-symbol snapshot before mutation.
- Recovery executes after the singleton acquisition and before the poll loop (`shared:1179-1202`). V3.1 persists recovered IDs before logging success (`V3.1:469-479`), a useful correction in `0b3fcebd`.
- Startup Demo validation is before management (`shared:1157-1159`). Cleanup finally now covers post-initialize startup, lock acquisition and polling; release itself is nested in a finally that still shuts down MT5 (`:1155-1314`). **Initialize returning false at :1151-1153 is before the guard**; no claim is made that MT5 requires shutdown on false without API-specific evidence.
- `scripts/sp2l_runner_lock.py` uses persistent inode OS locks rather than PID-check/unlink ownership: POSIX flock / Windows byte-range locking (`:27-45`), fsynced owner metadata after reserved byte (`:89-115`), persistent metadata not deletion on release (`:135-162`). File metadata is not the lock. Existing process/worktree coordination requires all participants to use the same resolved lock path; old lock-unaware processes remain outside this protection, as runbook `:9-11` warns.

### Limits not solved by these changes

- V3.1 does not resume persisted signal/notification/deduplication state: it unconditionally replaces `load_state` with fresh state and disables reconciliation (`V3.1:575-576`). This is intentional session isolation, **not durable exactly-once recovery**. State fields written to disk should not be described as recoverable continuity without qualification.
- Startup recovers **currently active** orders/positions only. A pending/position closed while the process was down is absent from both snapshots and cannot be recovered by these IDs alone. Its final lifecycle/accounting may be missing. This is a recovery scope limit, not proof that broker execution failed.
- Recovery stores position **ticket** (`recovery helper:65-73`) whereas deal links use **position_id** (`shared:953-961`). The tracked-history implementation is missing from this tree, so behavior when MT5 identifier differs from ticket cannot be verified. Add a regression for distinct `ticket` and `identifier`; do not assume they are always interchangeable.
- `save_state()` uses `Path.write_text` to truncate/write in place (`shared:568-580`), not temp+atomic replace, no fsync. A crash or concurrent monitor read can observe partial JSON. More importantly, restarting ignores this file anyway. Recommend atomic replacement for coherent monitor/evidence reads; do not claim that atomic writes alone fix recovery.
- Submission/result/persistence and external notification delivery are not atomic. A successful send followed by process death before the delivered marker is saved cannot provide exactly-once notification semantics. Existing separate `deal_events` vs `deals` is a useful per-process distinction, but fresh-state restarts discard both.
- The loop has no general per-poll exception recovery. Unexpected lifecycle errors, state write failure or `order_send` exception in trailing end the process, leaving broker GTC pending orders and broker-held SL/TP intact. TTL is local runner policy (`gateway:321` sets GTC), not a broker-enforced expiration guarantee while the runner is down. Test/describe this explicitly rather than promising TTL enforcement through downtime.
- Trailing evaluates only the latest completed M1 bar (`V3.1:58-63`); it does not replay every completed bar missed during a poll gap/restart or retain a durable maximum favorable extreme. This is a sampling limitation of the stated policy, not evidence for canonical intrabar behavior.
- `trail_attempts` is per-process memory and not serialized by shared save_state; one unsuccessful broker response suppresses that ticket/bar until the next bar (`V3.1:85-86,110-112`), while restart can retry it. Test desired retry semantics and precision/tick-size rejection separately.

## Determinism and market-data validation

The config functions appear deterministic for an identical valid ordered finite OHLC sequence; max-candidate tie-breaking is explicitly `(trigger_time,direction)` (`config:107`) and first qualifying invalid-risk trigger rejects the setup (`:75-76,89-90`). That does **not** establish deterministic forward-vs-replay behavior:

1. Forming-bar snapshots make outcomes depend on poll timing (A-03).
2. Sliding setup-window membership and one-key dedupe can move discovery backward (A-06).
3. Restart intentionally changes available deduplication/recovery state.
4. Offset inference rounds tick-host difference and permits cache reuse (`shared:118-146`); the session cutoff caches its inferred offset permanently (`V3.1:536-540`). Execution/expiry are stricter and pinned, so discovery and execution can disagree across stale feeds or clock/DST transitions. Treat a cached wrong cutoff as a candidate eligibility risk; regression should verify no stale backlog execution when offset inference changes.
5. Neither `rates()` nor this config validates ascending unique timestamps, contiguous M1 coverage, finite values, or valid OHLC ranges. The detector compares array neighbors, not minute-separated candles. Add input-boundary regressions for duplicate timestamps, reversed rates, missing minutes/weekend gaps, NaN/infinity and malformed OHLC; choose an explicit research rejection/defer policy. This audit does not invent a source-required gap threshold.

## Test source review and why CI is insufficient

**No tests were executed.** Test names/assertions below describe source coverage, not passing outcomes.

- `scripts/test_sp2l_v3_1_trailing_bar_guard.py` covers pre-entry/same-minute exclusion, post-entry acceptance, seconds fallback and missing timestamps for the **pure helper**. It does not call actual `trail_positions`, prove completed-bar entry detection, dry-run safety, account switching, order precision or broker response handling. It is not listed in the current forensic CI workflow.
- `scripts/test_sp2l_v31_startup_recovery.py` covers owned/foreign inventory, valid empty versus None, invalid tickets/types and extending existing state. It never imports the V3.1 entrypoint or exercises recovery -> persist -> first management poll -> deal collection. Thus it cannot see A-01/A-02.
- `scripts/test_sp2l_deal_lifecycle_dedupe.py` tests the standalone set-claim helper and list normalization. It does not cover actual history queries, delivery retry, timestamp basis or restart's deliberate fresh state.
- `scripts/test_sp2l_runner_lock.py` includes persistent metadata, separate-process contention/owner death, invalid PID, no-op release and creation failure. Useful cross-platform safety coverage; not end-to-end runner singleton coverage and not protection against a legacy lock-unaware process.
- `tests/test_pending_order_expiry.py:18-20,47-65` imports the **shared runner**, not the V3.1 wrapper; uses the older magic and UTC-like `time_setup` fixture (`:76-81`). Its generic idempotence/dry-run assertions cannot prove strict advancing-tick/pinned-offset TTL behavior or A-09/A-10.
- `tests/sp2l-determinism-invariants.test.ts` and other TypeScript strategy tests concern separate TS paths, not this monkey-patched Python V3.1 loop. Do not use their existence as end-to-end V3.1 proof.
- `.github/workflows/sp2l-forensic-checks.yml:23-36` runs detector/helper/lock and reconciliation tests and `py_compile` on four modules. `py_compile` **does not resolve the two missing imports**, execute startup wiring, or prove safe broker calls. A green compile/helper pipeline can coexist with an unimportable entrypoint.

## Proposed authorized next test phase (not run here)

Use fake MT5, fake clock, fake notifier, temporary state/event paths and an instrumented executor. Ensure imports cannot initialize MT5 or read local secret files. Prefer a bounded one-cycle integration harness over an unrestricted real runner.

1. **Packaging gate:** tracked local dependency closure; import V3.1 with only external APIs stubbed, ensuring both history modules are real reviewed repository modules.
2. **First-poll integration:** empty inventory, recovered pending, recovered position, failed inventory, failed state persistence, unsupported owned order, lock conflict. Startup success must follow durable ownership write, and zero broker sends before permission gates.
3. **Mutation permission matrix:** both flags, Demo/non-Demo/missing account for submit, cancel and trail; simulated account change after startup.
4. **Completed-bar/detection parity:** bar0 revision, first completed trigger, both directions, equal low/high boundary, risk0/max10/just-over10, before-spike SL anchor, no unsupported canonical assertions.
5. **Identity/retry:** A/B/A candidate sequence, disappearing setup/window rollback, same-key geometry change, transient clock failure, uncertain submission result with broker reconciliation before any retry.
6. **Clock matrix:** pinned +2/0/negative offsets, stale unchanged tick, advancing-but-stale tick, missing pin, invalid pin, cache mismatch, host-clock jump and inferred-cutoff transition. Verify both action eligibility and logged ages.
7. **Lifecycle/restart:** recovered old entry and new close, downtime close, distinct position ticket/identifier, partial fill/deal-entry variants if supported, history None vs empty, failed delivery retry, event/deal marker dedupe across an explicitly chosen restart policy.
8. **Persistence and operational faults:** interrupted write, monitor reading mid-write, logging/write errors, failed trailing response, runner-down TTL and latest-bar-only management after skipped minutes.

Keep source-confirmed strategy concepts, research parameter choices, observed broker execution and hypothetical test expectations separate in every result artifact. Nothing in this report authorizes starting a runner or contacting a broker.
