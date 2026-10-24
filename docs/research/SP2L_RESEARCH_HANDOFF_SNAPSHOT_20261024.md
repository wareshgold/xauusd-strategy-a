# SP2L Research Handoff Snapshot — 2026-10-24

**Purpose:** durable checkpoint so the next research session can resume without reconstructing prior work or repeating source audits.

## 1. Repository and safety state

- Repository: `wareshgold/xauusd-strategy-a`
- Active research branch: `research/strategy-b-vs-rr2-backtest-protocol-20261024`
- PR: [#341](https://github.com/wareshgold/xauusd-strategy-a/pull/341)
- PR state at snapshot time: OPEN, DRAFT, NOT MERGED.
- Last verified branch/PR head before adding this snapshot: `4bc381e0ac8637b1d802228ae12359a3d04fd49f`
- PR metadata before this snapshot: 57 commits, 22 changed files.
- This snapshot is research-only. Do not merge PR #341 unless the user explicitly asks after review.

## 2. Non-negotiable project rules

The SP2L workflow is:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

- Source meaning outranks backtest performance. Only source-confirmed rules may become canonical.
- Never invent P-Gap formula, AB=CD anchors/tolerance, fill semantics, exit semantics, or execution rules.
- Missing/conflicting evidence remains `UNKNOWN` / `AMBIGUOUS`.
- AI may support research, engineering, validation, documentation, and analytics; it must not autonomously define canonical rules or generate production BUY/SELL decisions.
- Do not connect to MT5, start/restart/stop runners, submit orders, alter active forward tests, or modify live config/state/logs/snapshots.
- Do not run destructive Git operations (`reset`, `clean`, mass staging/cleanup) or overwrite evidence.
- Do not alter unrelated Strategy B or RR2/TRAIL4 execution code to make legacy CI green.

## 3. Work completed

### Source and protocol mapping
- `docs/research/STRATEGY_B_VS_RR2_TRAIL4_BACKTEST_PROTOCOL_20261024.md`
  - Comparison protocol and explicit limits.
- `docs/research/RR2_TRAIL4_EVENT_ADAPTER_FIELD_MAP_20261024.md`
  - RR2/TRAIL4 runner field mapping. Runner `ts_utc` is observation/write time, not broker execution time. Telegram lifecycle rows do not preserve all fields needed to prove actual fills.
- `docs/research/STRATEGY_B_EVENT_ADAPTER_FIELD_MAP_20261024.md`
  - Strategy B request/response vs broker-confirmed deal distinction. Checked-in source does not establish a durable normalized event ledger or a broker-deal history export.
- `docs/research/IMMUTABLE_PAIRED_REPLAY_EVIDENCE_INTAKE_CONTRACT_20261024.md`
  - Required immutable package, hashes, time/source version evidence, row accounting, missing/conflicting evidence and replay eligibility statuses.
- `docs/research/EXACT_BROKER_DEAL_JOIN_AUDIT_20261024.md`
  - Exact-ID audit tool input contract, status semantics and invocation.

### Read-only tools and tests
- `scripts/audit_sp2l_exact_deal_join_readonly.py`
  - Offline JSONL audit; uses exact `deal_id`, does not join by timestamp proximity, infer fills from OHLC, or substitute requested volume for executed volume. Reports hashes, rejected rows, duplicate IDs, conflicts, unmatched events/deals and incomplete execution fields. Refuses to overwrite an existing report path.
- `tests/test_audit_sp2l_exact_deal_join_readonly.py`
  - Synthetic cases for exact match, unmatched event/deal, duplicate deal ID, multiple events claiming one deal, conflicting order IDs, same timestamp with different IDs, missing execution time/price/volume, runner observation time distinct from execution time, malformed row retention, deterministic repeat and missing event ID.
- `scripts/validate_sp2l_event_ledger_readonly.py` and `tests/test_validate_sp2l_event_ledger_readonly.py`
  - Existing source evidence invariants: stable source row reference and artifact hash for source-observed records; actual fill rows need deal ID, positive execution price and volume; proxy/derived rows cannot be mislabeled as actual fills.
- `.github/workflows/research-readonly-replay-audits.yml`
  - Includes compilation and test execution for the new exact-deal join audit and related read-only fixture suites.

## 4. Latest verified CI state before this snapshot commit

- [Read-only replay audits — run 40075628823](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40075628823): **SUCCESS** on `4bc381e0ac8637b1d802228ae12359a3d04fd49f`. Job steps include compilation, replay audit tests, synthetic evidence contract fixtures, source-parity arithmetic fixtures, event-ledger lifecycle fixtures, schema validation, and exact broker-deal join tests; all passed.
- [Legacy SP2L fixture suite — run 40075628837](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40075628837): **FAILURE** during TypeScript build, before deterministic tests ran.
- Observed legacy build errors include TS5097 import paths ending in `.ts`; `volume: number | undefined` incompatible with exact optional property typing; unresolved modules `PositionManager.js`, `BrokerConstraintGate.js`, `TrailingStopSafety.js`, `PositionModificationAdapter.js`; stale tests supplying `timeframe` to `Candle`; and test `Correction` fixtures missing required indices. These failures are unrelated to the new Python audit. Do not repair these as part of this research step without a separately scoped request.
- A passing read-only audit workflow validates the research tools/fixtures only; it does not validate historical trade truth or prove profitability.

## 5. Known source and evidence constraints

### Strategy B source
- Inspected code includes `scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py` and `scripts/strategy_b_pythontraderbot_live/Meta.py` on the Strategy B source branch `research/strategy-b-pythontraderbot-execution-20261022`.
- Source audit says Strategy B uses XAUUSD M1 and polls the forming M1 candle every 0.5 seconds; source-reported settings include spike multiplier 1.5, P-Gap 100 broker points, max SL distance 1,000 broker points (conversion depends on broker point), TP 0.9R, 0.01 lot, magic 8, EMA60/trend filter on. These are source inventory facts, not confirmation that a historical execution can be reproduced.
- Market-order request or `order_send` response is not by itself proof of a broker-confirmed deal. Actual broker deal export remains missing.

### RR2/TRAIL4 source
- Inspected baseline is `SP2L_V3_XAUUSD_RR2_TRAIL4_20261001`: XAUUSD M1, P-Gap 1.0 price, spike multiplier 1.5, max SL distance 10.0, TP_R 2.0, trail 4.0 × pip size 0.1 = 0.40 price units, pending TTL 30 minutes, all market hours, volume 0.01.
- This is a source/config inventory only. Do not change TP_R/trailing or reinterpret order/fill semantics.
- Runner event logger's `ts_utc` is write/observation time. Existing `TELEGRAM_DEAL_LIFECYCLE` records do not provide original broker deal time and dedicated executed volume needed for a verified deal ledger.

### Historical replay evidence already audited
- One replay JSON previously audited: SHA-256 `5bebae140d5ed511b1fd7732178160493ab577341c8d14125b3344ed59a2253b`, 56,951 bytes, requested 2026-09-01 00:00 UTC through 2026-09-23 00:00 UTC, actual first 2026-09-01 01:00 UTC and last 2026-09-22 23:58 UTC. The raw/filtered/out-of-window counts and apparent performance were structural audit outputs only, not validation of signals/fills/accounting/profitability.
- Separate `artifacts/mt5_xauusd_m1_10000.json` was not in GitHub; 10,000 bars covered 2026-09-08T04:20Z through 2026-09-17T10:05Z. Exact timestamp overlap alignment does not prove a complete-month dataset or historical strategy parity.
- Unresolved: historical server timezone mapping/DST, fill semantics, intrabar trailing ordering, overlap/exit accounting, shared transaction costs and source-rule parity.

## 6. Next steps — ordered

1. **Protect this checkpoint:** keep this file in PR #341 and update it after material research changes, recording exact commit SHA, CI links, files changed, and remaining blockers.
2. Review the exact-deal join audit for correctness on edge cases, especially duplicate event IDs, one-to-many links, malformed rows, and stable deterministic output. Add synthetic cases only where a specific gap is identified.
3. Confirm the workflow triggers include all relevant new tool/test/docs paths and that the latest read-only workflow remains green after this snapshot commit.
4. Investigate the legacy fixture suite separately only if needed; do not mix unrelated TypeScript repairs into the event-evidence audit.
5. When actual immutable artifacts are available, create a **new** evidence package: original Strategy B broker-deal export, RR2/TRAIL4 event JSONL snapshot, RR2/TRAIL4 broker-deal export, shared market data, exact source/config commit and hashes, timezone evidence, and explicit UTC window. Never overwrite prior snapshots.
6. Before normalization, hash original bytes. Preserve original fields and document every normalization. Do not manufacture missing IDs, timestamps, prices, volume, or fills.
7. Run exact-ID join audit on stable offline copies. Review all unmatched, ambiguous, duplicate, rejected, and incomplete rows. Only then decide whether a replay is eligible for offline review.
8. Keep all replay results research-only until source semantics are resolved, geometry is frozen from source evidence, untouched validation/robustness/fresh holdout are completed, and a human review explicitly authorizes the next phase.

## 7. Evidence gate / current blocker

**A true paired historical replay is still blocked.** Required broker-confirmed deal exports and immutable event snapshots have not been verified as available in this branch. Do not fabricate sample historical records to make a replay appear complete. Synthetic tests are implementation tests only.

The next productive work can continue offline on deterministic audit coverage and CI. A real-data join cannot be honestly completed until the source artifacts are supplied or located and their provenance is verified.

## 8. Snapshot maintenance format

For every subsequent handoff, append or update:
- timestamp (UTC);
- exact branch head SHA;
- new/modified paths and commit SHAs;
- latest relevant workflow run IDs and conclusions;
- tests actually run (not just scheduled);
- source artifacts actually present and their SHA-256 values;
- blockers and next ordered action;
- explicit confirmation that live MT5/forward state was not touched.

Never describe a queued/running workflow as passed. Never claim a source artifact exists unless its bytes/path were actually verified.


## 9. Snapshot publication / latest check (2026-10-24 07:51 UTC)

- Snapshot created at `be619be90b2ccb70aa61e52b249180d0c8b7e6a6`; this file's content blob at the subsequent verification was `5c3d2963d37e3ba1030b9bfcf4ba9f2404342c1e`.
- Added a durable link to this snapshot in the main comparison protocol and added this snapshot path to the read-only workflow's path filters.
- Latest verified PR head before this addendum: `9cddb34b6b565b480539c5438708a96dee92caba`; PR #341 remained OPEN / DRAFT / NOT MERGED, 60 commits and 23 changed files.
- [Read-only replay audit run 40075771254](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40075771254) completed **SUCCESS** at commit `0cc97009ade6fc74256a345c4e5d23f48c5b1026`.
- At the time of this check, runs [40075781218](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40075781218) (read-only audit) and [40075781268](https://github.com/wareshgold/xauusd-strategy-a/actions/runs/40075781268) (legacy fixture suite) were queued for head `9cddb34b6b565b480539c5438708a96dee92caba`. They must not be described as passed until completed.
- The legacy fixture run on `4bc381e0ac8637b1d802228ae12359a3d04fd49f` failed at TypeScript build step; deterministic tests were skipped. Detailed errors are summarized in section 4.
- Current next action remains: verify the newest read-only CI after the snapshot/protocol/workflow changes; separately inspect the legacy build failure only if scoped and necessary; then continue deterministic evidence audit improvements without touching live environments.
