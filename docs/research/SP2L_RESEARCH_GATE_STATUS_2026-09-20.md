# SP2L Research Gate Status — 2026-09-20

## Purpose

Single document summarizing the current SP2L research gate dashboard.

It is an audit/status document only. It does not modify strategy logic, does not
create trading rules, and does not promote any experimental result. Every gate
status is drawn from existing artifacts and checkpoints in this repository.

STATUS values are restricted to: **PASS · PARTIAL · BLOCKED · UNKNOWN**.

---

## Gate dashboard

| Gate | STATUS | Basis |
|---|---|---|
| Source Resolution | **PARTIAL** | Open blockers F10/F11/F12/F14 (plus F08/F13/F15/F16/round) remain unresolved; no primary evidence uniquely determines executable meaning. |
| Frozen Geometry | **BLOCKED** | No canonical geometry promoted; promotion guard active; depends on Source Resolution. |
| Validation | **LOCKED*** | Frozen-force harness + fixtures exist and are green (32 files / 124 tests), but nothing is canonical to validate at full scope. |
| Robustness / Stability | **PARTIAL** | Research evidence strong on 4-week MT5 surface; descriptive only, not promoted. |
| Fresh Holdout | **BLOCKED** | Boundary `2026-09-19 00:00Z` untouched; artifact = `HOLDOUT_DATA_UNAVAILABLE`. |
| MT5 data readiness | **PARTIAL** | Acquisition + provenance in place; historical applicability of session calendar UNVERIFIED; AUDITED_FAIL gap audits on monthly sets. |

\* `LOCKED` is the existing checkpoint wording for Historical Validation and means it cannot run for full scope while Frozen Geometry is BLOCKED — the nearest allowed STATUS is PARTIAL (scope blocked, infra ready). See **Validation** note below.

---

## 1. Source Resolution — PARTIAL

Status: **PARTIAL**.

Supporting evidence:
- F10/F11/F12/F14 source-discrimination pass: all four remain **PARTIAL / UNRESOLVED** (no newly verified primary artifact uniquely closes any executable blocker).
  - [SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md](docs/research/SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md)
  - [SP2L_F10_F11_F12_F14_SOURCE_PASS_INDEX_2026-09-19.md](docs/research/SP2L_F10_F11_F12_F14_SOURCE_PASS_INDEX_2026-09-19.md)
- Remaining blockers (2026-09-19 snapshot): P-Gap, F10 SL, F11 pending-order lifecycle, F12 trigger, F13 2X, F14 AB=CD, F15 bearish-mirror (symmetry NOT promoted), F16 round, F08 swing.
- Closure standard: a blocker closes only when direct source evidence uniquely determines executable meaning. Synthetic symmetry, convention, backtest performance, and implementation convenience are insufficient.

## 2. Frozen Geometry — BLOCKED

Status: **BLOCKED**.

Supporting evidence:
- No canonical geometry has been promoted from fixtures or experiments.
- Canonical-promotion no-go guard active: `research/harness/sp2l_canonical_promotion_no_go_guard_v1.ts`.
- Gate state unchanged across 2026-09-19 and 2026-09-20 checkpoints: Frozen Geometry BLOCKED, Production BLOCKED, Live trading DISABLED.
  - [SP2L_END_OF_DAY_STATUS_SNAPSHOT_2026-09-19.md](docs/research/SP2L_END_OF_DAY_STATUS_SNAPSHOT_2026-09-19.md)
  - [SP2L_MULTI_STAGE_PROGRESS_CHECKPOINT_2026-09-20.md](docs/research/SP2L_MULTI_STAGE_PROGRESS_CHECKPOINT_2026-09-20.md)

## 3. Validation — PARTIAL (scope-blocked; infrastructure ready)

Status: **PARTIAL**.

Notes:
- The historical-validation gate was previously labeled **LOCKED**. Under the
  restricted STATUS vocabulary, `LOCKED` maps to a deterministic reason: the full
  validation scope cannot run while Frozen Geometry is BLOCKED. The nearest
  allowed STATUS is **PARTIAL** — harness infrate exists and is green, but no
  canonical rule set is available for full validation.
- Green baseline: test suite = 32 files / 124 tests; `npm run build` passes.
- Harness present: frozen-geometry gate, 125R golden fixture, integrity
  invariants, fixture runner, validation-report contract
  (`research/harness/sp2l_*_v1.ts`).

## 4. Robustness / Stability — PARTIAL

Status: **PARTIAL**.

Supporting evidence (descriptive only — no parameter promoted):
- 4-week MT5 surface (2026-09-19): 158 trades, 103 W / 51 L / 4 A, decisive WR
  66.883%, +52R, PF 2.0196.
- 81-combination stability surface: all combinations positive in-sample;
  80/81 above 60% decisive WR.
- Statistical uncertainty limited by four weekly blocks; not an OOS claim.
- Multiple-testing guard artifact present
  (`SP2L_multiple_testing_guard_2026-09-19.json`).
- Artifacts: `artifacts/SP2L_*_2026-09-14_2026-09-18.json`, `_4week_*.json`,
  `author-replica-mt5-stability-snapshots.json`.

## 5. Fresh Holdout — BLOCKED

Status: **BLOCKED**.

Notes:
- Protected boundary: `2026-09-19 00:00 UTC`.
- Holdout artifact: `SP2L_fresh_holdout_2026-09-19.json` =
  `HOLDOUT_DATA_UNAVAILABLE`. No holdout signal/outcome consumed.
- The holdout may not be used early; it is reserved for after frozen geometry
  and validation.

## 6. MT5 data readiness — PARTIAL

Status: **PARTIAL**.

Notes:
- Acquisition toolchain and manifests exist for XAUUSD.ecn M1 (Otet Group MT5
  terminal, server OtetGroup-MT5).
- Provenance recorded per dataset (source, range, gaps, SHA-256, audit status)
  in [SP2L_MT5_PROVENANCE_MAP_2026-09-20.md](docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md).
- Timestamp basis is not assumed UTC; the session-calendar id
  `xauusd-ecn-session-current-observation-2026-09-17` has historical
  applicability **UNVERIFIED**.
- Gaps are session-boundary jumps (daily 23:58→01:00, weekend Fri→Mon), AUDITED_FAIL
  on monthly sets; the 08-21→09-18 4-week research set is gap-audited as
  research-only. No synthetic candles and no gap-filling.

---

## Status rollup

| Gate | STATUS |
|---|---|
| Source Resolution | PARTIAL |
| Frozen Geometry | BLOCKED |
| Validation (scope) | PARTIAL |
| Robustness / Stability | PARTIAL |
| Fresh Holdout | BLOCKED |
| MT5 data readiness | PARTIAL |

Gate sequence dependency: **Source Resolution → Frozen Geometry → Validation →
Robustness → Fresh Holdout → Production**. Production and Live trading remain
BLOCKED / DISABLED until all predecessors pass.

## Related

- [Research Artifact Index](docs/research/SP2L_RESEARCH_ARTIFACT_INDEX_2026-09-20.md)
- [MT5 Provenance Map](docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md)
- 2026-09-20 progress checkpoint: `docs/research/SP2L_MULTI_STAGE_PROGRESS_CHECKPOINT_2026-09-20.md`