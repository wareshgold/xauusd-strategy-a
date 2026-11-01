# SP2L Strategy A — V3 Entry Freeze / Exit Discovery Audit Snapshot

- Snapshot date: 2026-11-01
- Snapshot branch: `research/snapshot-v3-entry-freeze-audit-20261101`
- Snapshot base commit: `2600e0286e350666be0c1f272bffe5ca77afd39c`
- Audited PR: [#378](https://github.com/wareshgold/xauusd-strategy-a/pull/378)
- Audited head branch: `research/m1-integrity-gate-v3-entry-freeze-20261101`
- Scope: Strategy A V3 frozen entry population and research-only M1 exit discovery.
- Nature: immutable audit checkpoint on a separate branch; no merge, no local worktree mutation, no MT5 execution.

## 1. PR #378 remote state

- Title: freeze V3 entry population and gate preserved M1 data for exit discovery.
- State at audit: OPEN / Draft / Unmerged.
- Base: `research/factory-candidate-lab-20261010`
- Base SHA: `83939ec42e76ed362f510f974af88a3b0da2f630`
- Head SHA: `2600e0286e350666be0c1f272bffe5ca77afd39c`
- Compare: 63 commits ahead, 0 behind; 14 changed files.
- Four head workflows completed successfully:
  - SP2L forensic deterministic checks — run `41277400817`
  - Factory Research Tests — run `41277400763`
  - Factory Journal Lock Cross-Platform Tests — run `41277400836`
  - Full Repository Test Suite — run `41277400776`
- No inline review threads were present at audit time.
- A PR conversation comment was added (comment ID `6554068911`) documenting the M1-gap replay issue and requested fail-closed treatment.

## 2. Frozen research inputs declared by PR #378

### M1 source
- File: `xauusd_ecn_m1_30d.csv`
- Bars: 29,919
- Declared coverage: `2026-09-24T07:57:00Z` through `2026-10-23T23:57:00Z`
- SHA-256: `B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285`

### V3 entry population
- File: `a_trail_0_40_activated_proxy_v3_trades.csv`
- Rows declared: 462
- SHA-256: `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`
- Entry identity and risk columns are reused; previous target and exit outcomes are ignored.
- All 288 exit variants are designed to share the same frozen population.

## 3. Audit findings

### PASS / supported by inspected implementation
- Frozen entry loader verifies exact raw-byte SHA-256, exact CSV header, Strategy A rows, one source variant, BUY/SELL direction, timezone-aware M1-aligned entry times, chronological order, duplicate identity rejection, exact M1 timestamp lookup, and finite positive entry/SL/risk values.
- M1 integrity gate checks schema, declared symbol/timeframe/window, timestamp alignment/order, duplicate timestamps, OHLC consistency, non-negative volume/spread fields, raw-byte SHA-256, and reports gaps without filling or classifying them.
- Same-bar SL+TP is marked ambiguous.
- Trailing stop updates use completed-bar information and become effective on the next bar.
- Frozen-entry mode is explicit through both `--entry-population-artifact` and `--entry-population-sha256`; both must be supplied together.
- Outputs include JSON, summary CSV, trades CSV, and a run snapshot.
- PR explicitly labels the work research-only; no canonical SP2L geometry, production decisioning, or broker fill semantics are authorized.

### BLOCKER before DEVELOPMENT matrix execution
- **M1 gaps are reported but not treated as replay interruptions.**
- `replay_trade` iterates consecutive array rows without checking whether their timestamps differ by more than 60 seconds.
- If a gap occurs while a trade is open, an unobserved interval may contain an SL/TP/trailing event. The next observed bar can currently be treated as a decisive outcome despite the missing interval.
- Required conservative research behavior: mark a trade gap-exposed as ambiguous (e.g. `M1_GAP_WHILE_OPEN`), assign no realized exit price/R/USD, and exclude it from decisive statistics. Report the gap-exposed count separately. Do not classify gaps as sessions/closures without source-backed calendar evidence.
- Until fixed and tested, PR #378 must remain Draft/unmerged and the 288-variant matrix must not be run on this implementation.

### Additional unresolved audit items (not to be silently converted into rules)
- Loader does not enforce a hard-coded 462 row count; current exact SHA pins the declared artifact, but an explicit expected-population count could be defense in depth.
- Loader does not validate directional SL placement or derive/compare `risk_price` from entry and SL. These semantics must be checked against the actual V3 exporter/source before adding any formula or tolerance.
- Entry proxy is not a confirmed broker fill.
- Spread, slippage, and commission are not modeled.
- M1 OHLC replay cannot establish intrabar path or broker fill semantics.
- Gap report alone does not establish whether gaps are market closures or missing observations.

## 4. DEVELOPMENT boundary and next sequence

1. Fix and test gap-aware replay so trades exposed to missing M1 intervals cannot be counted as decisive.
2. Re-run focused integrity/replay tests and all four CI workflows.
3. Run the controlled 288-variant matrix only with the preserved M1 CSV and the exact frozen V3 entry CSV + SHA-256; never allow entry recomputation for this run.
4. Preserve run artifacts and hashes outside the research worktree.
5. Analyze ambiguity/gap exposure, R, net USD, PF, drawdown, and stability. Do not select a winner from the same discovery sample as if it were validation.
6. Proceed to untouched validation/robustness only under a separately frozen protocol and data boundary.

## 5. Governance and non-claims

- V3 Entry is treated as the existing baseline population, not proof that canonical SP2L geometry is resolved.
- No P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules are invented.
- Source Resolution remains unresolved/skipped by the current project decision and is not used to stall exploratory development, but unresolved semantics remain explicitly non-canonical.
- No Discovery backtest was run in this GitHub audit.
- No MT5 terminal was accessed; no order, forward test, or production action occurred.
- CI success validates software checks only, not statistical edge or trading readiness.
- Local branch, HEAD, dirty state, untracked evidence, and MT5 runtime state were not inspected; this GitHub-only snapshot makes no claim about them.
- No production BUY/SELL decisions are generated or authorized.
