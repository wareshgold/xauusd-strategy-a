# V4 Phase 16 — Data Provenance Investigation (Direct)

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `b521adb5`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Date:** 2026-10-28

## Scope and method
Inspected actual files in repo, git history, acquisition manifests, run summary, and prior audits. Computed hashes/sizes/rows/schemas/timestamp ranges directly from current CSV files. No datasets modified; no declared hashes changed.

## Git history (relevant)
- `1dfb2bbf research: archive MT5 acquisition and stability artifacts 2026-09-19` added `data/mt5-acquisition/*` (and related artifacts). No earlier commits found modifying those specific files in recent history.

## Per-dataset findings
### July 2026 (`data/mt5-acquisition/xauusd-ecn-m1-2026-07.csv`)
- Schema/header: `timestamp,open,high,low,close,tick_volume,spread,real_volume`
- Size: 1968716 bytes | Lines: 31484 | Rows: 31483
- Timestamp range: `2026-07-01T01:00:00Z` → `2026-07-31T23:57:00Z`
- Current SHA256: `0215c22898ac5b867bd51096cbbe59e50d0623597eb64aa56d9937c9088f4936`
- Manifest (`xauusd-ecn-m1-2026-07.manifest.json`): provider `MetaTrader5 terminal API`, terminal `Otet Group MT5 Terminal`, server `OtetGroup-MT5`, symbol `XAUUSD.ecn`, timeframe `M1`, retrieval `2026-09-17T09:03:01.014726Z`, `artifact_sha256` (declared) `482991df85c7143077ef3713c81f3c5ae14ae12311f6c03e3579f27f8048e34e`, `expected_active_bar_count` 31740, `returned_bar_count` 31483, `audit_status` AUDITED_FAIL, session calendar `xauusd-ecn-session-current-observation-2026-09-17` marked `UNVERIFIED`, large list of missing expected timestamps (gaps documented).
- **Declared vs current:** MISMATCH (declared != current). Manifest hashes the artifact it references but is not an independent third-party archive.

### August 2026 (`data/mt5-acquisition/xauusd-ecn-m1-2026-08.csv`)
- Schema/header: same
- Size: 1810823 bytes | Lines: 28958 | Rows: 28957
- Timestamp range: `2026-08-03T01:00:00Z` → `2026-08-31T23:58:00Z`
- Current SHA256: `c7bac957eba4e4c2b8606c19913b25dec7b6c71adcda7fbfac3992d362c8eac7`
- Manifest: retrieval `2026-09-17T09:01:35.325425Z`, declared `artifact_sha256` `8d9f4d9a82ff2fcbedfc8221ef62da1b4c518d037a000f09b8ec888077ca4a87`, expected/returned differ, `audit_status` AUDITED_FAIL, session calendar UNVERIFIED.
- **Declared vs current:** MISMATCH

### September 2026 (`data/mt5-acquisition/xauusd-ecn-m1-2026-09.csv`)
- Schema/header: same
- Size: 1067490 bytes | Lines: 17070 | Rows: 17069
- Timestamp range: `2026-09-01T01:00:00Z` → `2026-09-17T12:01:00Z`
- Current SHA256: `1bb2dcdc163e13fa08487c5d7a68905325e9be50104a57aedbe0bbde7055f1d4`
- Manifest: retrieval `2026-09-17T09:01:38.990389Z`, declared `artifact_sha256` `3b7212dc43f844807da120d89e6cbae9f63def4943fefdb003c54d630467cc2b`, expected/returned differ, `audit_status` AUDITED_FAIL, session calendar UNVERIFIED.
- **Declared vs current:** MISMATCH

## Session calendar provenance
- All manifests reference `session_calendar_id: xauusd-ecn-session-current-observation-2026-09-17` with `session_calendar_historical_applicability: UNVERIFIED` and evidence date 2026-09-17. No separate immutable session-calendar definition file with independent provenance found in inspected paths. **Provenance: UNVERIFIED.** Cannot infer authoritative session labels from timestamps alone.

## Independent original-source copies
Searched repo for other copies of these specific CSVs/hashes. No other copies of the exact files found. No external archive URL/hash from a third party recorded. Git history shows them added as retrieved artifacts.

## Decisions
| Month | Decision | Rationale |
|---|---|---|
| July 2026 | **UNRESOLVED_PROVENANCE** | Retrieved via MT5 terminal API per manifest; declared hash differs from current hash; no independent original archive copy with provable origin chain found. Gaps/missing bars documented. |
| August 2026 | **UNRESOLVED_PROVENANCE** | Same as above. |
| September 2026 | **UNRESOLVED_PROVENANCE** | Same as above. Holdout marked BLOCKED/NOT_VALIDATED due to integrity issues. |

## Missing evidence (precise)
1. **Immutable original artifact**: An independent archive (export from MT5/history provider with its own hash, or broker export) obtained at acquisition time, preserved unchanged, with hash matching either declared or current and provenance recorded.
2. **Acquisition chain**: Signed/export logs, terminal session logs, or provider export metadata linking retrieval to immutable source.
3. **Session calendar**: Authoritative historical session/calendar definition with provenance for the periods analyzed.
4. **Hash reconciliation**: Explanation of why declared vs current differ (re-export/reformat/copy) with evidence.

## Next practical acquisition action
Obtain fresh immutable exports for the exact periods from the original source (broker/MT5 history center export with checksums) into a new evidence location, record provenance (who/when/source/export params), compute hashes before any processing, and compare against these artifacts. Do not overwrite existing evidence; create new artifacts if needed.

## Verdict
Data provenance remains **UNRESOLVED** for all three months. Manifests document retrieval but are not independent proof of origin; hash mismatches persist. Session calendar provenance **UNVERIFIED**. This blocks treating the datasets as fully authenticated provenance-wise. Statistical reproducibility of described aggregates is separate from provenance authentication.

**Scientific verdict unchanged:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`
