# SP2L Research Artifact Index — 2026-09-20

## Purpose

Single location mapping every research artifact in this repository to its
category, file, and status. Nothing here grants canonical status to any
geometry. This index exists so future passes can find the right artifact
without re-searching the tree, and so the categories stay explicit.

## Categories

- **EVIDENCE** — claims with a primary/author-controlled source or a direct artifact audit. Highest tier short of frozen.
- **VALIDATION** — results from the frozen-gate harness and fixture runners. Not canonical; they test behavior under a defined contract.
- **EXPERIMENT** — statistical/robustness measurements. Descriptive only. Never select parameters from these.
- **DIAGNOSTIC** — acquisition/timestamp/provenance auditing and tooling output. Describes data, not strategy.

Alignment with gates:
EVIDENCE → Source Resolution · VALIDATION → Frozen Geometry · EXPERIMENT → Robustness/Stability · DIAGNOSTIC → data/audit layer.

---

## 1. Source evidence archive

Primary-author / author-associated source chain. Highest authority available.

| Ref | File | Status |
|---|---|---|
| Batch chain | `docs/research/SP2L_BATCH10...29*.md` | EVIDENCE — concept-level; executable anchors unresolved |
| F10/F11/F12/F14 pass index | [SP2L_F10_F11_F12_F14_SOURCE_PASS_INDEX_2026-09-19.md](docs/research/SP2L_F10_F11_F12_F14_SOURCE_PASS_INDEX_2026-09-19.md) | EVIDENCE — all four PARTIAL / UNRESOLVED |
| Discrimination pack (harness) | [sp2l_source_discrimination_pack_v1.ts](research/harness/sp2l_source_discrimination_pack_v1.ts) | EVIDENCE-boundary harness — not strategy rules |
| Discrimination status | [SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md](docs/research/SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md) | EVIDENCE — gate state for F10/F11/F12/F14 |
| P-GAP cross-reference | [SP2L_PGAP_EVIDENCE_CROSS_REFERENCE_2026-09-16.md](docs/research/SP2L_PGAP_EVIDENCE_CROSS_REFERENCE_2026-09-16.md) | EVIDENCE — P-GAP ≠ common gap; no formula frozen |
| 2X / trigger / AB=CD primary transcript | [SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md](docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md) | EVIDENCE — 2X & trigger & AB=CD variance documented |
| Author video artifact (Batch 17) | [SP2L_BATCH17_UPLOADED_PRIMARY_VIDEO_EVIDENCE_F13_F14_2026-09-16.md](docs/research/SP2L_BATCH17_UPLOADED_PRIMARY_VIDEO_EVIDENCE_F13_F14_2026-09-16.md) | EVIDENCE — primary local video (69m 15s) |

Opening blocker map:
F10 SL anchor · F11 pending-order lifecycle · F12 trigger taxonomy · F14 AB=CD anchors.
All remain **PARTIAL / UNRESOLVED**. Do not convert any of these into entry/exit logic.

## 2. Validation (frozen-gate harness & fixtures)

| Artifact | File | Status |
|---|---|---|
| Golden fixture | [sp2l_125r_golden_fixture_v1.ts](research/harness/sp2l_125r_golden_fixture_v1.ts) + `tests/sp2l-125r-golden-fixture.test.ts` | VALIDATION |
| Geometry contract | [sp2l_geometry_contract_v1.ts](research/harness/sp2l_geometry_contract_v1.ts) | VALIDATION |
| Integrity invariants | [sp2l_integrity_invariants_v1.ts](research/harness/sp2l_integrity_invariants_v1.ts) | VALIDATION |
| Fixture runner | [sp2l_fixture_runner_v1.ts](research/harness/sp2l_fixture_runner_v1.ts) + `tests/sp2l-fixture-runner.test.ts` | VALIDATION |
| Frozen geometry gate | [sp2l_frozen_geometry_gate_v1.ts](research/harness/sp2l_frozen_geometry_gate_v1.ts) + `tests/sp2l-frozen-geometry-gate.test.ts` | VALIDATION |
| Validation report contract | `research/harness/sp2l_validation_report_v1.ts` + `tests/sp2l-validation-report.test.ts` | VALIDATION |
| Canonical promotion no-go guard | [sp2l_canonical_promotion_no_go_guard_v1.ts](research/harness/sp2l_canonical_promotion_no_go_guard_v1.ts) | VALIDATION — blocks fixture→canonical promotion |

**Current gate (2026-09-20):** Frozen Geometry **BLOCKED**. Test/build green: 32 files / 124 tests.

## 3. Robustness experiments (descriptive only)

All under `artifacts/`. Never used to select parameters.

| Artifact | Range | Notes |
|---|---|---|
| `SP2L_author_replica_2026-09-14_2026-09-18.json/.xlsx` | 2026-09-14 → 18 | author-replica run |
| `SP2L_author_replica_4week_stability_matrix.json/.xlsx` | 4-week | stability matrix |
| `SP2L_author_replica_parameter_robustness_matrix.json/.xlsx` | 4-week | 81-combination surface |
| `SP2L_parameter_stability_4week_81_matrix_2026-09-19.json` | 4-week | 80/81 > 60% WR desc |
| `SP2L_rr_sensitivity_1R_2R_3R_2026-09-14_2026-09-18.json` | 4-day | RR experiments |
| `SP2L_rr_trailing_3x4_matrix_2026-09-14_2026-09-18.json` | 4-day | RR×trailing grid |
| `SP2L_trailing_stability_matrix_5_10_15_20pip_2026-09-14_2026-09-18.json` | 4-day | trailing grid |
| `SP2L_trailing_10pip_m1safe_2026-09-14_2026-09-18.json` | 4-day | 10-pip M1-safe |
| `SP2L_trailing_10pip_management_experiment_2026-09-14_2026-09-18.json` | 4-day | management experiment |
| `SP2L_temporal_rolling_stability_2026-09-14_2026-09-18.json` | 4-day | rolling stability |
| `SP2L_candle_level_dependency_stability_2026-09-14_2026-09-18.json` | 4-day | candle-level deps |
| `SP2L_performance_decomposition_2026-09-14_2026-09-18.json` | 4-day | performance decomposition |
| `SP2L_statistical_uncertainty_2026-09-14_2026-09-18.json` / `_4week_2026-09-19.json` | 4-day / 4-week | uncertainty bounds |
| `SP2L_multiple_testing_guard_2026-09-19.json` | 4-week | multiple-testing guard |
| `SP2L_parameter_main_effects_4week_2026-09-19.json` | 4-week | main effects |
| `SP2L_fresh_holdout_2026-09-19.json` | — | **HOLDOUT_DATA_UNAVAILABLE** — boundary `2026-09-19 00:00Z` untouched |
| `author-replica-mt5-stability-snapshots.json` | MT5 4-week | stability snapshots |

Top-line descriptive finding (2026-09-19): 158 trades, 103 W / 51 L / 4 A,
decisive WR 66.883%, +52R, PF 2.0196. Research-only.

## 4. MT5 datasets & provenance

Full per-dataset provenance in the separate [MT5 PROVENANCE MAP](docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md).
Datasets are **DIAGNOSTIC/EVIDENCE for data characteristics**, never canonical strategy input until gates pass.

| Dataset | Range (UTC) | Bars | Gaps | Audit |
|---|---|---|---|---|
| `xauusd-ecn-m1-2026-07.csv` | 2026-07 | 31,483 | 257 | AUDITED_FAIL |
| `xauusd-ecn-m1-2026-08.csv` | 2026-08 | 28,957 | 23 | AUDITED_FAIL |
| `xauusd-ecn-m1-2026-09.csv` | 2026-09-01→17 | 17,069 | 871 | AUDITED_FAIL |
| `xauusd_ecn_m1_2026-08-21_2026-09-18.csv` | 08-21→09-18 | 28,815 | 20 | research_only |
| `xauusd-ecn-m1-session-aware-test-2026-09-17-v2.csv` | 09-16 22:00→09-17 02:00 | 181 | 0 | AUDITED_PASS |
| `xauusd-ecn-m1-session-aware-test-2026-09-17.csv` | same | 181 | 0 | AUDITED_FAIL |
| `xauusd-ecn-m1-smoke-2026-09-17.csv` / `-strict` | 09-16 00:00→01:00 | 1 | 0 | PASS / FAIL |

## 5. Status rollup

| Gate | Status (2026-09-20) |
|---|---|
| Source Resolution | PARTIAL |
| Frozen Geometry | **BLOCKED** |
| Historical Validation | LOCKED |
| Robustness / Stability | RESEARCH EVIDENCE ONLY |
| Fresh Holdout | UNTOUCHED — boundary `2026-09-19 00:00Z` |
| Execution infrastructure | READY / GUARDED FOR DRY-RUN |
| Production / Live | BLOCKED / DISABLED |