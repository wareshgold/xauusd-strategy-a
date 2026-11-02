# Factory and dataset/research evidence audit

## Scope and method

Read-only review of `/agent/workspace/sp2l-independent-audit`, checked HEAD `dc14a451669992d39bad559a125a7b0196e410e4`. No checkout, repository-script/test execution, module imports, broker/MT5 calls, or changes to existing files were performed. Inspection used Git object reads, text/JSON reads, small CSV scans, and SHA-256. This report is the only new deliverable. Sensitive runtime journals and credential files were excluded from the substantive review; no account identifiers, credentials, or messaging destinations are reproduced. This is a static audit, not an independently executed replay or test certification.

**Citation convention:** unprefixed paths are at audited HEAD. `F:path:line` means the Git object at Factory branch `origin/research/factory-candidate-lab-20261010`, commit `83939ec42e76ed362f510f974af88a3b0da2f630`; these files are **not present in the audited HEAD tree**. `S:` means `origin/research/snapshot-factory-post-pr374-20261031`, `97360b746cac35177af910cd5ddcec2c7330edec`. Other branch prefixes are defined where used. Lines refer to actual source/object text, not generated audit line numbers.

## Executive findings

1. **Two materially divergent workstreams, not one integrated baseline.** HEAD has no `src/strategy_factory` directory or Factory scripts. Factory exists in a separate remote branch: merge-base with HEAD `493eae922ce887946eb888ae7c55f3cf2d82b177`; `git rev-list --left-right --count HEAD...F` = **55 / 916**. Factory protections or green CI from that branch cannot be represented as deployed on HEAD. The Factory checkpoint explicitly calls itself separate/non-promoting (`S:research/snapshots/SP2L_FACTORY_POST_PR374_STATUS_SNAPSHOT_20261031.md:3-8,36-41`).
2. **Source completeness, not backtest return, is the upstream blocker.** HEAD's source audit has **0/7 executable fields fully source-confirmed**, and frozen geometry remains BLOCKED (`docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md:39-47,99-120`). Factory agrees: all manifest rules are NON_CANONICAL and 18 blocking questions remain (`F:src/strategy_factory/sp2l_manifest.py:83-119`). Research configurations are not canonical rules.
3. **Material Factory holdout authorization gap in the inspected Factory baseline.** Holdout checks immutable role, a caller-supplied frozen boolean defaulting true, snapshot identity, upstream identity, and distinct artifact hashes, but does not require independently authenticated source/frozen-geometry authority before reading holdout bytes. Snapshot validation checks self-hash, not truth/approval. Detailed evidence below. A divergent hardening proposal exists; it is not baseline behavior.
4. **Actual local data are modest M1/OHLC datasets and evidence summaries, not the referenced tick/discovery corpus.** There is no `data/raw`, no local GZIP/Parquet market dataset, no 30-day M1 source, frozen 462-row entry CSV, or controlled-discovery evidence manifest located by filename inventory. Referenced tick bytes, acquisition manifest, and newer discovery outputs remain machine-local evidence, not independently verified here.
5. **Strong historical replay numbers have important model limitations.** The committed RR2/Trail4 artifact reports 1,522 signals, 1,455 decisive, 67 ambiguous, net +527.28R and PF 10.42 without modeled costs; these are completed-M1 proxy outputs. The implementation moves a stop using a bar's favorable extreme and then tests that same bar's opposite extreme, leaving within-bar path uncertainty beyond the explicit SL+TP ambiguity flag. The artifact lacks an exact input-data digest and code/engine hash.
6. **Local manifests already flag data-quality failures.** July/August/September acquisitions are AUDITED_FAIL with historical session calendar UNVERIFIED. The one-row smoke dataset is AUDITED_PASS in one policy and AUDITED_FAIL in the strict policy despite identical bytes. PASS labels must be interpreted with their actual policy and window, not as dataset completeness.

## 1. Architecture and responsibility boundaries

### HEAD

- The foundation documents a deterministic detector pipeline and separates risk from strategy (`README.md:19-28,30-58`). Its stale foundation status at `README.md:5-7` is not an accurate inventory of all later research code.
- HEAD contains TypeScript domain/backtest components (`src/domain/strategy-a/*`, `src/backtest/*`), a source/fixture harness (`research/harness/*`), Python acquisition/analysis/replay scripts, MQL5 research code, and committed result artifacts. These are distinguishable from the Python Factory branch.
- Canonical promotion guard requires every geometry field to be SOURCE_CONFIRMED (`research/harness/sp2l_canonical_promotion_no_go_guard_v1.ts:9-31`). This verifies a provenance label on supplied fields; it does not independently acquire source evidence.

### Factory branch F

- `StrategyResearchFactory` is a research gate orchestrator, deliberately excluding geometry, signals, MT5 orders, and production decisions (`F:src/strategy_factory/factory.py:37-43`). Its simple `production_eligible` property is four PASS gates (`:15-19`), and evaluator methods accept supplied booleans/counts (`:48-87`); this facade alone is not an authoritative certification boundary.
- Domain model: Stage, GateStatus, and StrategyPassport with source/geometry/code/data revisions, execution model, parameter set, canonical=false (`F:src/strategy_factory/models.py:8-53`). StrategyCompiler refuses unresolved/noncanonical manifests and non-source-confirmed rules (`F:src/strategy_factory/compiler.py:29-61`).
- Layering: test specification → dataset registry/usage → job/run identity → execution adapter/receipt → evidence acceptance → research provenance/audit/readiness snapshot → immutable research records → explicit station handoff → validation/robustness/holdout/forward preparation. The runner verifies job/spec/dataset identity before adapter execution (`F:src/strategy_factory/runner.py:66-154`); end-to-end provenance binds job, run, receipt, evidence, snapshot, and audit (`F:src/strategy_factory/research_provenance.py:38-171`).
- Operational orchestration is distinct from research meaning: durable job events, worker state, recovery planning/application, and read-only dashboard telemetry. Historical design describes immutable journal snapshots, fail-closed invalid journals, manual reconciliation of interrupted dispatch, and no automatic repair/replay (`F:artifacts/factory/SP2L_FACTORY_CANDIDATE_LAB_SNAPSHOT_20261010.md:58-85`). Those are documented/test claims, not tests rerun by this audit.
- Synthetic E2E goes through the same registry/runner/orchestrator/evidence machinery but labels SYNTHETIC_ONLY, production decisions 0, and excludes Holdout/Forward/MT5 (`F:artifacts/factory/SP2L_FACTORY_CANDIDATE_LAB_SNAPSHOT_20261010.md:166-171`). It is infrastructure proof, not a real strategy-performance result.

## 2. Frozen candidates, sessions, manifests, and engine identity

### Distinguish three forms of “frozen”

**A. Frozen research implementation at HEAD:**

| Config | Version / scope | Declared parameters and session | Evidence |
|---|---|---|---|
| `scripts/sp2l_v3_config.py` | V3 TRAIL10 20261001, research only | PGap 1.0; spike 1.5; maxSL 10; TP 1R; trail 10 pip = 1.0 price; pending limit research; TTL 30 min; ALL_MARKET_HOURS | `:1-23` |
| `scripts/sp2l_v3_rr2_trail4_config.py` | V3 RR2 TRAIL4 20261001, research only | same geometry parameters; TP 2R; trail 4 pip = 0.4 price; same TTL/session | `:1-23` |
| `scripts/sp2l_v3_1_rr4_act40_config.py` | V3.1 RR4 ACT40 TRAIL40 20261101 | TP 4R; TRAIL_PIPS 4; 0.1 price/pip; TTL 30; ALL_MARKET_HOURS | `:9-23` |

V3.1's docstring still says RR2/Trail4 (`:4`) despite its RR4 version/TP; its config has no separate activation variable in the first 23 lines. Activation behavior cannot be certified from the filename alone. Its bar-after-entry safety helper uses strictly later bar start timestamps (`:114-134`). No runner was imported or executed here.

The original V3 official snapshot records baseline commit `113e79c77f0f3130e06cf08043cfbe85c255e416`, and explicitly labels RESEARCH VARIANT / NOT CANONICAL (`docs/research/SP2L_V3_OFFICIAL_SNAPSHOT_20261001.md:3-7`). It calls completed-bar trailing a research execution variant (`:24-25,38-44`). These declarations do not resolve source semantics.

**B. Factory candidate identity framework, not proof a real candidate has been approved:** `CandidatePlan` freezes declared development dataset SHA, execution/geometry/source fingerprints, base revision, fixed parameters and finite grid; defaults max_candidates=64 (`F:src/strategy_factory/candidate_lab.py:42-107`). Canonical JSON hashing covers plan metadata/parameters and generates deterministic candidate IDs/fingerprints (`:109-161`). Source/geometry fingerprints are required nonempty strings; this local plan validation does not itself establish source authority (`:78-83`). Candidate observations must reconcile counts and be net of declared costs (`:197-230`). Do not confuse this default 64-limit scheduler with the older 81-point author-replica matrix.

**C. Frozen Factory demo session contract:** `DemoForwardSession` binds gate/handoff, strategy/manifest/execution identities, independently named holdout/forward datasets and hashes, and tuning/production flags (`F:src/strategy_factory/forward_session_factory.py:23-65`). It validates PREPARED, forbids post-holdout tuning and production_decision, and verifies its canonical payload hash (`:67-96`). Preparation requires a PASS Fresh-Holdout-to-Forward gate (`:115-148`). It does not run the existing forward runner (`:3-8`). No persisted real session object was established in this HEAD tree.

### Audit-computed source SHA-256 (exact HEAD bytes)

These hashes identify inspected code **now**, not necessarily the code that generated historical artifacts:

| Source | SHA-256 |
|---|---|
| `scripts/sp2l_v3_config.py` | `139e001352073a198bd81181be788ce40c07b08a018d1ca054d569621b87f064` |
| `scripts/sp2l_v3_rr2_trail4_config.py` | `94a3dc8e4d872a6af36d18e4ccad4575fb5b746c8db909ecd2edcd20f4e6fc53` |
| `scripts/sp2l_v3_1_rr4_act40_config.py` | `4817de67fdfb38f739c77a37e62f41f4496eaf06c861c0bd90a0a16a4f14b25b` |
| `scripts/run_sp2l_v3_xauusd_backtest.py` | `ed16597289f98b6251dd7e6608de87349c623dd2a00289f2b02bb6d4be6fdfaa` |
| `scripts/run_sp2l_v3_xauusd_exit_matrix.py` | `a621ae918c7d265af0076599eaff37044a07f3103ea3a92366442e2a87f9f9ed` |
| `scripts/run_sp2l_v3_xauusd_exit_matrix_costed.py` | `efcd36ba47ee8857801675913173f48d842b06d04fd992196b19110a1ea1a63e` |

**Historical reproducibility blocker:** backtest result fields contain version/config/window/count/summary/trades but no input-data SHA, git commit, or engine-source hash (`scripts/run_sp2l_v3_xauusd_backtest.py:116-126`). The generated snapshot literally says “Commit/branch must be recorded from Git after pull” (`:136-139`; actual RR2 snapshot `artifacts/v3/SP2L_V3_XAUUSD_RR2_TRAIL4_3M_20261001T101458Z_SNAPSHOT.md:2-13`). Its SHA hashes output JSON (`scripts/run_sp2l_v3_xauusd_backtest.py:130-148`), not engine or source data. Output integrity is not full input/code provenance.

## 3. Provenance, split gates, and concrete gaps

### What is implemented on F

- Dataset roles DEVELOPMENT / UNTOUCHED_VALIDATION / FRESH_HOLDOUT; nondevelopment must be immutable (`F:src/strategy_factory/test_contract.py:8-16,24-44`). Execution BAR_CLOSE_RESEARCH and TICK_FEASIBLE are explicit, not interchangeable.
- Registry records artifact identity, location, raw SHA, byte size and format; fingerprints combine metadata and content fingerprint (`F:src/strategy_factory/datasets.py:9-34,68-86`). Registry is explicitly **in-memory**, persistence deferred (`:89-98`). Same identity cannot change role/revision/artifact (`:100-151`), and same holdout content cannot be reused under another ID in its explicit guard (`:171-179`). This is not an external access-control system.
- Usage ledger is also in-memory and rejects development/optimization/parameter-fit purposes on validation/holdout (`F:src/strategy_factory/usage.py:50-82`). This does not establish that all outside scripts or prior human inspections were isolated.
- Receipt v2 separates adapter `input_fingerprint` from `dataset_content_sha256`; exact synthetic exception is restricted to `type(adapter) is SyntheticExecutionAdapter`, DEVELOPMENT, purpose SYNTHETIC_INFRASTRUCTURE_TEST, and null dataset SHA (`F:src/strategy_factory/acceptance.py:21-53`). Non-synthetic v2 must match both registered and observed raw SHA. v1 remains readable and skips this dataset verification (`:21-22`), with `dataset_verified=false` exposed (`:173`).
- `ExecutionReceipt.engine_revision` is required nonempty but not constrained to an independently measured code hash (`F:src/strategy_factory/execution.py:24-54`); binding compares test, strategy revision and semantics (`:77-98`). An engine revision label is not byte-level engine attestation.
- Dataset provenance evaluator compares **supplied** observed SHA/artifact against registry identity (`F:src/strategy_factory/dataset_provenance.py:43-121`); dataset registry explicitly does not read market-data bytes (`F:src/strategy_factory/datasets.py:68-73`). Concrete file-reading composition boundaries must produce that observation honestly.
- Validation and holdout factories do read and SHA-check their explicit artifacts and lock registration (`F:src/strategy_factory/validation_factory.py:88-139`; `F:src/strategy_factory/holdout_factory.py:115-167`). Forward preparation rejects unfrozen strategy/post-holdout tuning (`F:src/strategy_factory/forward_preparation.py:39-76`) and binds completed holdout record/artifact/SHA (`:78-103`).

### Findings requiring resolution before relying on “fresh” isolation

**H1 — independent authority is not enforced at inspected baseline holdout entry (high).** `F:src/strategy_factory/holdout_factory.py:43-46` defaults a caller assertion of frozen revision true. `:64-113` validates snapshot and identity, not source PASS / canonical approval. `:138-164` then reads/registers holdout bytes. `ReadinessSnapshot.validate()` verifies structure and its own digest only (`F:src/strategy_factory/snapshot.py:55-78`); runner calls that check (`F:src/strategy_factory/runner.py:110-124`) before adapter execution (`:152-154`), without a role-specific independent authority requirement in that inspected path. A self-consistent blocked or caller-constructed snapshot is not source authorization. This is a static missing-precondition finding, not an exploit/test execution claim.

Relevant **unmerged/divergent proposal** `origin/research/fresh-holdout-source-authority-hardening-20261031` = `d703e8cd3ce9fc488791d3da7576dde9741bf9e8` introduces trusted-verifier composition, required manifest/passport/ledger, canonical passport, independently verified source and frozen geometry (`src/strategy_factory/fresh_holdout_authority.py:3-8,43-94`). Its diff from F adds/changes eight files. Do not credit those checks to F or HEAD; review integration separately.

**H2 — hash distinction is weaker than temporal/sample independence (high).** Holdout factory checks source SHA and artifact ID differ (`F:src/strategy_factory/holdout_factory.py:115-127`); these do not prove non-overlapping rows or absence of prior inspection. The TestDataset interval check is lexical start<end (`F:src/strategy_factory/test_contract.py:35-44`) and the shown registry anti-reuse compares full identities/hashes, not row intersections (`F:src/strategy_factory/datasets.py:171-179`). No claim that an arbitrary recut/re-encoding is genuinely untouched can follow from these checks alone. Require a declared split/exposure ledger and row/time-overlap checks at the authorized data boundary.

**H3 — old “holdout ready” language is superseded by upstream blockage (high).** September freeze audit declares development/robustness Aug24–Sep18, holdout from Sep19, no tuning, but also acknowledges unresolved geometry/time semantics (`docs/research/SP2L_FRESH_HOLDOUT_FREEZE_AUDIT_2026-09-19.md:7-11,43-55,72-84`). Its READY FOR UNTOUCHED HOLDOUT wording (`:86-96`) cannot override the source audit's no-new-validation/fresh-holdout gate (`docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md:99-120`) or later Factory stage snapshot (`S:research/snapshots/SP2L_FACTORY_POST_PR374_STATUS_SNAPSHOT_20261031.md:74-85`). September is also explicitly reused as the exit-matrix validation slice; it is not a globally unexposed sample.

## 4. Actual local datasets and quality

SHA-256 below was measured over exact local bytes. Counts/date endpoints were read directly from small CSV/JSON data, without executing repository tools. For eight acquisition CSVs, basic scan found **0 adjacent duplicate timestamps, 0 lexicographically reversed timestamps, 0 malformed eight-field/basic-positive-OHLC violations**. This is not full numeric/type, clock, gap, session, or feed-completeness certification. Their manifest SHA values match measured local raw bytes.

### Acquisition CSVs (`data/mt5-acquisition/`)

| Filename | Rows | Observed first → last (labels as stored) | SHA-256 | Manifest disposition |
|---|---:|---|---|---|
| `xauusd-ecn-m1-2026-07.csv` | 31,483 | Jul01 01:00 → Jul31 23:57, 2026 | `482991df85c7143077ef3713c81f3c5ae14ae12311f6c03e3579f27f8048e34e` | AUDITED_FAIL; 31,740 expected / 257 missing |
| `xauusd-ecn-m1-2026-08.csv` | 28,957 | Aug03 01:00 → Aug31 23:58 | `8d9f4d9a82ff2fcbedfc8221ef62da1b4c518d037a000f09b8ec888077ca4a87` | AUDITED_FAIL; 28,980 expected / 23 missing |
| `xauusd-ecn-m1-2026-09.csv` | 17,069 | Sep01 01:00 → Sep17 12:01 | `3b7212dc43f844807da120d89e6cbae9f63def4943fefdb003c54d630467cc2b` | AUDITED_FAIL; 17,940 expected / 871 missing |
| `xauusd_ecn_m1_2026-08-21_2026-09-18.csv` | 28,815 | Aug21 01:00 → Sep18 23:57 | `9df9a0ca0333c185396fb3407c7c816fd77a2ab57d88f71cea30a73462e75aa4` | invalid rows=0; 20 observed gaps; no calendar completeness proof |
| `xauusd-ecn-m1-session-aware-test-2026-09-17.csv` | 181 | Sep16 22:00 → Sep17 02:00 | `9be20f3533c97d24cc1d35b367141747c7203e11a4a697eaeb5a5250a40e228e` | AUDITED_FAIL |
| `xauusd-ecn-m1-session-aware-test-2026-09-17-v2.csv` | 181 | same | same SHA as previous | AUDITED_PASS under changed jump policy; calendar still UNVERIFIED |
| `xauusd-ecn-m1-smoke-2026-09-17.csv` | 1 | Sep16 01:00 only | `f07d0264f3ccc0d22cdc20a1802e499491ca3adaea21496ebcbfa2d1985bd471` | AUDITED_PASS despite request of 61 minutes |
| `xauusd-ecn-m1-smoke-strict-2026-09-17.csv` | 1 | same | same SHA as previous | AUDITED_FAIL |

Evidence lines: month manifests each `:8-17`; July `:391-467`, August `:147-243`, September `:955-1011` carry invalid jumps/hash/status. Historical calendar applicability is UNVERIFIED at each `:14`. Session-aware original `:14-31` versus v2 `:14-33`; smoke original `:8-26` versus strict `:8-22`. Overlapping CSV copies are not independent samples and must not be blindly concatenated.

Expanded Aug21–Sep18 source manifest: `data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.manifest.json:9-18,160-168`; 41,760 requested calendar bars vs 28,815 observed. A missing calendar minute is not automatically missing tradable data. Raw labels containing Z do not settle broker clock semantics; session time-alignment gate remains UNRESOLVED/TRADING_USE BLOCKED (`docs/research/MT5_SESSION_MATRIX_TIME_ALIGNMENT_GATE_2026-09-20.md:5-21`).

**Byte-identity reconciliation:** Factory DEV audit records candidate raw SHA `09fb33790e46539df7ea072d0796a84f1136b242e32e28b365ccd2c604dd8cae` (`F:artifacts/factory/DEV_DATASET_AUDIT_20261010.md:45-51`), different from local/committed LF bytes `9df9...`. A non-writing stream transformation from LF to CRLF produces exactly `09fb...`. This demonstrates a line-ending explanation, not price corruption or exact raw-byte parity. Keep raw hashes distinct and explicitly version any normalized-row contract. The same DEV audit reports 3 spread mismatches against a machine-local independent reference even though all 28,815 timestamps/OHLC/volume match (`:11-43`); matching rows still do not establish tick/fill parity (`:53-60`).

### Twelve Data historical JSON (`data/historical/`)

| File | Candles | Stored timestamp range | SHA-256 |
|---|---:|---|---|
| `xauusd-1min.json` | 10,000 | 2026-08-20 13:05 → Aug27 11:44 | `fd3f341dbf96c84cda91008a304ddc6286ca583d06f6f8069e55d11f466765f3` |
| `xauusd-5min.json` | 10,000 | 2026-07-23 18:25 → Aug27 11:40 | `c6bc707579ea6d032c0787ab2b1ced4ff1cfebf03bd0e7b3fc7c73f5b5baa45e` |

Top-level source/timezone metadata is in each JSON `:1-6`; `data/reports/dataset-audit.json:2-21,23-39` reports PASS, no duplicates/invalid OHLC/nonchronology/gaps for both. This is a stored audit result, not independently replicated feed quality. M5 covers a longer interval than the 10,000-bar M1 file; the complete M5 source cannot be reconstructed from that M1 window alone.

### Availability/forensic CSVs (`data/mt5-session-availability/`)

These are raw availability observations or daily summaries, not independent strategy-validation datasets:

| File stem | Rows | Coverage/type | SHA-256 |
|---|---:|---|---|
| `xauusd_ecn_m1_availability_2026-09-07_2026-09-14` | 6,753 | observed Sep07 01:00 → Sep11 23:57 | `9028506fc357a42bd8b7c6bc72fe6bfb36acabdd9d6d95bcfb2f8e114228e4ca` |
| `xauusd_ecn_m1_availability_contiguous_2026-07-06_2026-09-14.daily` | 50 | daily availability records | `a488489788dc1a0ae7822855401f0eeacf1c90317744ec78f8e66aa706a9566b` |
| `xauusd_ecn_m1_availability_june_to_july_2026.daily` | 20 | daily availability records | `349dd50d86ab1e9b1d682720b473a324aa5b4c815fe67ed56e84823dcbdf586b` |
| `xauusd_ecn_m1_availability_matrix_2026Q1_Q3.daily` | 10 | selected daily observations, not full Q1–Q3 history | `601d583a7059bf9cd3e04f9985185d8b4419485f31848c6b2a0d9a33fd5902c5` |
| `xauusd_ecn_m1_availability_seasonal_dst_2026_may_oct.daily` | **0** | header only; all eight requested windows NO_DATA / NO_DATA_IN_REQUESTED_INTERVAL | `150bbd3c44ce86699d0e638800420a9319b971627da7b4e76c57cc5c8c0cee80` |
| `xauusd_ecn_m1_forensic_2026-06-19` | 1,322 | Jun19 01:00 → Jun22 04:00 | `860cb8790d5e57c62527c10e85ba2b11730d0da2fb420f880eabd4d678444542` |
| `xauusd_ecn_m1_forensic_2026-07-03` | 1,322 | Jul03 01:00 → Jul06 04:00 | `3a8be2155724340cf2143e9b318a188bbf6f1d572af42e5d4956f4aaba51c30f` |
| `xauusd_ecn_m1_forensic_2026-09-07` | 1,418 | Sep07 01:00 → Sep08 04:00 | `e1913e2de4a3bb3f83a9179456ff99fd214f96b119db0ad39f803b3f3e257a2a` |

Seasonal manifest explicitly marks RAW_AVAILABILITY_MATRIX_ONLY and no session-close/UTC/DST/holiday inference (`data/mt5-session-availability/xauusd_ecn_m1_availability_seasonal_dst_2026_may_oct.manifest.json:8-57,59-68`). Its filename must not be used as proof of DST coverage.

`data/research/sp2l-feature-validation/observations.csv` has 28,815 derived rows from Aug21–Sep18 and SHA `6dcf2afc21e7d06ddae402ff073d6064de76eedc6a815132bbd371e37126ddf5`. Its feature states are unknown, not validated labels: header/first row `:1-2`; integrity report says counts preserved and unknown states retained (`data/research/sp2l-feature-validation/observations_integrity_report.json:2-9`). Reports/trade CSVs under artifacts are output evidence, not replacement raw market data.

## 5. Machine-local / branch-only evidence that is not available for independent byte audit

### Tick corpus

Factory report says the compressed tick artifact/manifest are local ignored files and not committed (`F:artifacts/factory/DEV_TICK_BIDASK_AUDIT_20261028.md:5-22`). Claimed compressed bytes: 111,124,585; rows: 10,817,858; SHA `412a535b8d5f0413f329e5fde8a1f851591ee83c95fc25af38b287d6170a1347`; observed 2026-08-21 01:00:05.864Z → Sep18 23:57:56.609Z. These were **not rehashed locally in this audit**.

Stored observations: 12,389 adjacent repeated timestamps, 7,429 duplicate groups, 6,895 groups with differing Bid/Ask, no adjacent reversals, 20 gaps >60 seconds including a 3.399h gap; all Last and Volume zero (`F:artifacts/factory/DEV_TICK_BIDASK_AUDIT_20261028.md:42-62`). Preserve quote order/multiplicity; do not infer trade prints, traded volume, calendar closures, or feed completeness.

Divergent proposal `T = origin/research/factory-dev-tick-receipt-20261028`, commit `90401a47c4f89ca6a313117c297e326596ce8f9d`: `artifacts/factory/DEV_DATASET_REGISTRATION_PROPOSAL_20261028.json:2-42` records limited-development approval, manifest observed SHA `3a3fce2df05ddb8bd904ec63647c258aa04fe1e7fd423b05e06a8920f8473669`, local receipt SHA `760ef49fb1d5e90d94bcddf28be2f2a8fc8d6a87b53c37141328b37dc7c5629`, but provenance UNANCHORED. It expressly forbids strategy backtests/holdout/canonical/fill/production use (`:72-94,129-151`), and says Draft/unmerged. This is not a merged Factory dataset registration.

The independent M1 reference `sp2l_runtime_m1_20250925_20260925.csv` is also machine-local; only the comparative report is available (`F:artifacts/factory/DEV_DATASET_AUDIT_20261010.md:11-19,45-51`). No byte audit of that reference is claimed.

### Newer frozen-entry / exit-discovery proposals

`M = origin/research/m1-integrity-gate-v3-entry-freeze-20261101`, commit `5f808175a40fe52ba95512ce42258a3bccd77910`, identifies:

- `xauusd_ecn_m1_30d.csv`, 29,919 bars, Sep24 07:57 → Oct23 23:57, SHA `b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285`.
- `a_trail_0_40_activated_proxy_v3_trades.csv`, 462 rows, SHA `39ed87cd1f0be3e59b5f064b0bcf97a9787e5266df6e972aa07e5ea4d3608ab1`.

Evidence: `M:docs/research/M1_DATA_INTEGRITY_GATE_V3_ENTRY_POPULATION.md:12-19`. It notes 462 trade identities but only 452 signal identities; ten signal groups have two different initial stops, not independent live-executable trades (`:47-57`). Gap verdict is PASS_WITH_GAPS, without synthetic repair or inferred calendar cause (`:37-43`); costs remain omitted and no untouched/holdout/edge claim is created (`:58-67`). Neither input exists in this checkout.

`R = origin/research/v3-exit-robustness-20261101`, commit `01256593215176b766865cbd04f86bc252474bc3`, documents a machine-local controlled-discovery evidence manifest and output directory (`R:docs/research/v3-exit-robustness-audit.md:5-21`); these outputs are not local here. The proposal describes four chronological slices, local neighbors and a 288-way common moving-block max-t diagnostic (`:23-35`). Later missingness/studentization corrections require the p-value to be **recomputed**, not carried forward (`:38-48`). No new numerical robustness conclusion can be independently certified from the documentation alone.

## 6. Replay metrics, uncertainty, and robustness

### Committed older V3 results: integrity verified, causal/execution meaning limited

- `artifacts/v3/SP2L_V3_XAUUSD_RR2_TRAIL4_3M_20261001T101458Z.json:2-30`: 90,637 bars; July1→Oct1; 1,522 signals, 1,455 decisive, 1,399 wins, 56 losses, 67 ambiguous; WR 96.1512%; +527.27955R; PF 10.41571. Measured JSON SHA `5d9629a4c6a4923fff93b03f0e10d521b00e2e924968248bd9fbe95cdb4f3932`, exactly matching snapshot `:13`. This confirms output bytes, not source input/code identity.
- Costed matrix JSON measured SHA `e60c989a3241ec9eaed00b0f310cc6111663862181e3505f742158c75ba4718c`, matching `artifacts/v3/SP2L_V3_EXIT_MATRIX_COSTED_3M_20261001T093445Z_SNAPSHOT.md:22`. RR2_TRAIL4 reports same 1,455 decisive / 67 ambiguous; 1,228 wins / 227 losses after costs; WR 84.3986%; +409.12889R; PF 6.82002. Its September slice is 534 signals / 506 decisive / 28 ambiguous, +120.80553R / PF 4.78706. Read directly from that JSON's `matrix[variant=RR2_TRAIL4]` object. Costs are constant 0.20 spread, 0.05 stop slippage, exact TP, not measured tick-by-tick execution (`scripts/run_sp2l_v3_xauusd_exit_matrix_costed.py:30-38,58-63,134-150`; snapshot `:11-20`).
- TRAIN/VALIDATE split uses signal timestamp string, not necessarily entry/exit exposure boundaries (`scripts/run_sp2l_v3_xauusd_exit_matrix_costed.py:42-49,152-155`). It does not by itself purge positions/events crossing the split or prove no parameter selection after seeing validation outcomes. It explicitly labels the timestamp frame server-clock.

**Replay/model blockers:**

1. `scripts/run_sp2l_v3_xauusd_backtest.py:22-40` downloads fresh terminal data, sorts and deduplicates. It does not preserve/fingerprint source snapshot bytes in its result. Local monthly files stop before the full 90,637-bar July→Oct input and cannot recreate that exact run on their own.
2. Config `find_first_entry` looks at later completed candle extremes to assign theoretical entry (`scripts/sp2l_v3_rr2_trail4_config.py:65-96`); backtest starts outcomes on the next bar (`scripts/run_sp2l_v3_xauusd_backtest.py:68-76`). This is a theoretical historical proxy, not a demonstrated pending-order fill simulation with activation/TTL/Bid-Ask constraints. It does not prove an executable at-the-time fill.
3. Backtest updates BUY stop from the bar high before testing the same bar low (`scripts/run_sp2l_v3_xauusd_backtest.py:78-90`); SELL mirror uses low then high (`:92-103`). A stop can be declared hit on a low/high occurring before the favorable extreme that created it. Only simultaneous active SL+fixed TP is flagged ambiguous. Therefore 67 is **not** an exhaustive count of all intrabar path-sensitive cases; do not interpret high WR as tick-feasible evidence.
4. Ambiguous cases are excluded from decisive stats (`scripts/run_sp2l_v3_xauusd_backtest.py:112-125`), so reported WR/netR are conditional on resolution. A complete result should retain unresolved/ambiguous exposure and evaluate path/cost bounds without inventing returns.

### Older author-replica uncertainty and parameter surface

`docs/research/SP2L_STATISTICAL_UNCERTAINTY_RESULTS_2026-09-19.md:3-26` reports Sep14–18: 38 signals, 37 decisive, 27 wins/10 losses/1 ambiguous; Wilson 95% WR 57.02%–84.60%; 20k bootstrap PF 1.466–8.347. Same document explicitly says exchangeable-trade bootstrap does not model temporal dependence, not fresh holdout, and execution costs unreconstructed (`:45-58`). These limitations are material, not optional footnotes.

The 81-combination author-replica grid baseline has 158 signals/154 decisive, WR66.883%, +52R, PF2.020, weekly WR min52.941%, with all 81 combinations positive in-sample (`docs/research/SP2L_PARAMETER_ROBUSTNESS_ANALYSIS_2026-09-19.md:18-51,53-74`). Only six combinations keep all four weeks >60%, and source/selection/cost/completeness limitations remain (`:103-144`). This is the same development sample, not independent robustness validation. Do not pool its trades with the V3 3-month result as if one frozen strategy/sample.

Factory statistical framework provides Wilson, normal-approximation mean-return intervals, exact two-sided sign test and comparison-count multiplication (`F:src/strategy_factory/statistics.py:114-142,145-189`), while explicitly hardcoding canonical/production eligibility false (`:71-94`). Mean interval is degenerate for n<2 (`:125-131`); no dependence modeling exists in that function. Factory robustness matrices bind member provenance, require same strategy/manifest/role/semantics and unique run IDs (`F:src/strategy_factory/robustness.py:141-154,201-234`), but those invariants are not a new empirical result or proof all members use independent data.

## 7. Source boundaries and stage disposition

Source concepts are not executable formulae. HEAD source audit distinguishes partial entry/SL/order/trigger/2X/ABCD from unresolved PGap; exact indexing, OHLC anchors, threshold/equality boundaries, sizing/fill/lifecycle and bearish symmetry remain unresolved (`docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md:39-47,51-97`). Factory manifest retains these as blocking questions rather than guessing (`F:src/strategy_factory/sp2l_manifest.py:94-111`). No strategy rules are proposed by this audit.

| Stage | Evidence-based disposition | Blocking next evidence |
|---|---|---|
| Source resolution | Incomplete / blocked for executable canonical rules | Authoritative source artifact closing exact meaning; documented adjudication, not performance inference |
| Synthetic fixtures | Infrastructure fixtures exist; strategy geometry not fully freezeable | Source-derived fixture contracts, explicit unresolved behavior |
| Frozen geometry | BLOCKED | Approved source-complete versioned geometry and independent authority |
| Development strategy performance | Research variants exist; canonical Factory performance blocked | Identified exact data bytes + acquisition provenance + approved adapter/execution contract + engine/config hashes |
| Untouched validation | Not established for canonical strategy | Predeclared candidate/split/exposure protocol; genuinely uninspected independent dataset; overlap checks |
| Robustness/stability | Older descriptive in-sample evidence only; newer branch-only methodology not independently rerun | Dependence-aware/cost/path/gap analysis on verified inputs, multiplicity inventory, corrected bootstrap output |
| Fresh holdout | BLOCKED | Source/freeze authority checks integrated before any holdout read; verified new sample and access/exposure ledger |
| Forward/production | Factory contracts do not authorize production; existing research runner is a separate workstream | Complete upstream research + operational reconciliation + explicit governance approval |

This agrees with the later Factory status checkpoint (`S:research/snapshots/SP2L_FACTORY_POST_PR374_STATUS_SNAPSHOT_20261031.md:60-85,99-103`): infrastructure CI is not source confirmation, validated statistical edge, holdout eligibility, or production readiness. The reported 821 passing tests in that checkpoint (`:27-34`) are historical CI evidence only; this auditor did not run them.

## 8. Prioritized research-stage blockers for the parent audit

1. Preserve branch boundaries: do not silently attribute F/T/M/R hardening or data approvals to HEAD.
2. Close source/freeze authority and the Factory holdout pre-read enforcement gap before any protected-data access. Review the divergent trusted-authority proposal without treating its existence as merged verification.
3. Obtain byte-preserved local-only tick/discovery inputs, manifests, acquisition/producer/run linkage and corrected robustness outputs through an approved evidence channel; local references alone are insufficient.
4. Record exact engine/config/source-dataset SHA, revision and execution semantics in future manifests. Preserve both raw-byte and explicitly normalized hashes; do not silently normalize CRLF/LF.
5. Reconcile M1 clock/session/gap status and spread-source mismatch. AUDITED_FAIL or header-only seasonal files cannot establish complete session coverage.
6. Treat existing replay as completed-OHLC proxy research. Quantify intrabar path/ambiguity/cost uncertainty and implement separately approved execution semantics rather than infer them from attractive returns.
7. Establish a global sample-exposure/split ledger: September has been repeatedly analyzed; different SHA/ID does not mean independent or untouched data. No numeric research result in this audit justifies a strategy-rule promotion.
