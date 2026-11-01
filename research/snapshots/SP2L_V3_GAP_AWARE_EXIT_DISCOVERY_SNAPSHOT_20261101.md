# SP2L Strategy A — V3 Frozen Entry / Gap-Aware Exit Discovery Snapshot

- Snapshot date: 2026-11-01
- Snapshot branch: `research/snapshot-v3-gap-aware-replay-20261101`
- Snapshot base / audited PR head: `32ce4f4cb6fb4e24691f0e8a65d3f6c333e9db50`
- Audited PR: [#378](https://github.com/wareshgold/xauusd-strategy-a/pull/378)
- PR branch: `research/m1-integrity-gate-v3-entry-freeze-20261101`
- Base branch: `research/factory-candidate-lab-20261010`
- Base SHA: `83939ec42e76ed362f510f974af88a3b0da2f630`
- Nature: separate immutable checkpoint; PR remains Draft/unmerged; no MT5 execution or local worktree changes.

## 1. GitHub state at checkpoint

- PR #378 remains OPEN / Draft / Unmerged.
- Compare against Factory base: 66 commits ahead, 0 behind.
- 14 changed files.
- Final PR head: `32ce4f4cb6fb4e24691f0e8a65d3f6c333e9db50`.
- Four workflows for the final head completed successfully:
  - SP2L forensic deterministic checks — run `41278264443`
  - Factory Research Tests — run `41278264384`
  - Factory Journal Lock Cross-Platform Tests — run `41278264598`
  - Full Repository Test Suite — run `41278264438`
- Full repository pytest job completed successfully; cross-platform journal-lock jobs on Ubuntu and Windows completed successfully.
- No merge was performed.
- PR conversation audit/fix comments:
  - Initial audit finding: comment `6554068911`
  - Gap-aware replay implementation note: comment `6554078563`

## 2. Fixed research inputs declared by PR #378

### Preserved M1 data
- File: `xauusd_ecn_m1_30d.csv`
- Bars: 29,919
- Declared UTC coverage: `2026-09-24T07:57:00Z` through `2026-10-23T23:57:00Z`
- SHA-256: `B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285`

### Frozen V3 entry population
- File: `a_trail_0_40_activated_proxy_v3_trades.csv`
- Declared rows: 462
- SHA-256: `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`
- Entry fields reused: direction, setup/entry timestamps, entry proxy, initial SL, risk.
- Previous V3 target and exit outcomes are ignored.
- All 288 exit variants share this one entry population when the two frozen-artifact CLI arguments are supplied.

## 3. Audit finding and implementation completed

### M1 gap replay issue — addressed in code
The initial PR reported missing M1 intervals but replayed adjacent array rows as if they were consecutive minutes. This could create false decisive outcomes when an open trade crossed an unobserved interval.

The PR branch now:
- Exposes `m1_gap_detected(previous_time, current_time)` in `src/strategy_factory/m1_integrity.py`.
- Checks each replay interval from the frozen entry bar forward.
- If a trade remains open across a timestamp delta greater than 60 seconds, marks it:
  - `ambiguous=true`
  - reason `M1_GAP_WHILE_OPEN`
  - no realized exit price, R, or USD
- Excludes that trade from decisive performance statistics.
- Reports `gap_exposed` separately in matrix summaries and summary CSV.
- Records the gap policy in output execution/exit metadata and generated snapshot.
- Adds focused tests for consecutive M1 timestamps versus missing-minute intervals.

Relevant PR-branch commits:
- `8559b1cc3e60f862233f625d1b5540bf93ad88c9` — gap detector
- `31392e04890cfda9f2a63f2738efa636d50b90f0` — gap-aware replay
- `32ce4f4cb6fb4e24691f0e8a65d3f6c333e9db50` — missing-minute tests

## 4. Remaining research qualifications

- The loader verifies SHA-256, schema, Strategy A identity, one source variant, BUY/SELL direction, timezone-aware M1-aligned entry times, chronology, duplicate identity, exact M1 timestamp lookup, and finite positive entry/SL/risk values.
- It does not assert a hard-coded 462-row count. The exact current artifact SHA pins the declared file; a separate expected-count assertion remains optional defense in depth.
- It does not validate directional SL placement or derive/compare `risk_price` from entry and SL. Do not invent a formula or tolerance; first verify V3 exporter/source semantics.
- Entry proxy is not a confirmed broker fill.
- Spread, slippage, and commission remain unmodeled.
- M1 OHLC cannot establish intrabar path or broker fill semantics.
- Gaps are reported, not filled or classified as market closures; no session calendar is inferred.
- Same-bar SL+TP remains ambiguous.
- Discovery ranking is exploratory and subject to multiple-comparison/selection bias; no winner is validated by this same sample.

## 5. Next action — DEVELOPMENT run is ready for user-side execution after local preflight

The code-level M1-gap blocker is fixed and all four CI workflows are green. The next operation requires the user's local Windows environment and preserved files; this GitHub session cannot verify their current bytes or MT5 symbol metadata.

Before running:
1. Verify local M1 CSV SHA-256 equals `B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285`.
2. Verify frozen V3 entry CSV SHA-256 equals `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`.
3. Run from a clean, reviewed checkout of the PR head; preserve all existing local modifications/untracked evidence and take a preflight snapshot first.
4. Use both `--entry-population-artifact` and `--entry-population-sha256`; do not allow entry recomputation.
5. Direct outputs to a new external evidence directory and preserve JSON, summary CSV, trades CSV, run snapshot, and hashes.
6. Inspect `gap_exposed`, total ambiguous share, and all decisive metrics before any candidate interpretation.

This is a DEVELOPMENT research run only. Do not access validation or Fresh Holdout data and do not start MT5 order execution.

## 6. Governance and non-claims

- V3 Entry is the fixed existing baseline population, not proof of canonical SP2L geometry.
- Source Resolution remains unresolved/skipped under the current project decision; unresolved P-Gap, AB=CD anchors/tolerance, fill semantics, and execution semantics remain non-canonical.
- No statistical edge has yet been demonstrated by the 288-variant matrix.
- CI success validates software tests, not trading performance or production readiness.
- No local branch, HEAD, dirty state, untracked evidence, or MT5 runtime was inspected.
- No production BUY/SELL decisions are generated or authorized.
