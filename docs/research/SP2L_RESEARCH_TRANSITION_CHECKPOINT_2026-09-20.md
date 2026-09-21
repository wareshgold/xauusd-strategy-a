# SP2L Research Transition Checkpoint — 2026-09-20

## Purpose

Assess whether the project infrastructure is ready to transition beyond the
current **Source Resolution (PARTIAL)** stage into the downstream research
stages, and — where it is not — document exactly what is missing.

This checkpoint is documentation only:
- no strategy code changes;
- no execution code changes;
- no canonical rule created;
- every unresolved item is explicitly left unresolved.

Transition is not authorized here. This document only reports readiness.

## Summary disposition

| Area | Readiness | Controlling reason |
|---|---|---|
| 1. Frozen Geometry | **NOT READY — BLOCKED** | 7/7 required fields not `SOURCE_CONFIRMED`. |
| 2. Validation | **NOT READY — LOCKED (scope-blocked)** | Requires frozen canonical geometry; existing evidence descriptive only. |
| 3. Robustness / Stability | **READY AS EVIDENCE-ONLY / NOT READY FOR PROMOTION** | Harness + artifacts in place; all results descriptive. |
| 4. MT5 Data | **READY (with tracked caveats)** | Acquisition + provenance + session matrix in place; timestamp caveat remains UNVERIFIED; no live execution. |

---

## 1. Frozen Geometry readiness

**Status: BLOCKED — not freeze-ready.**

Required fields for `Frozen Geometry = READY` (all seven must be
`SOURCE_CONFIRMED`): `entry`, `invalidation`, `limitRefresh`, `trigger`,
`twoX`, `abcd`, `pGap`.

Current state (from the [Canonical Validation Readiness Ledger](docs/research/SP2L_CANONICAL_VALIDATION_READINESS_LEDGER_2026-09-16.md) and the 2026-09-19/20 audits):

| Field | Status |
|---|---|
| `entry` | UNRESOLVED / PARTIAL |
| `invalidation` (F10) | UNRESOLVED / PARTIAL |
| `limitRefresh` (F11) | UNRESOLVED / PARTIAL |
| `trigger` (F12) | UNRESOLVED / PARTIAL |
| `twoX` (F13) | UNRESOLVED / PARTIAL |
| `abcd` (F14) | UNRESOLVED / PARTIAL |
| `pGap` | **UNRESOLVED** |

**What is missing before freeze:** each field needs a primary source that
uniquely determines its executable meaning (exact price anchor, index, buffer,
tolerance, precedence, formula). `SOURCE_CONFIRMED executable fields = 0 / 7`.

**Dependencies that are unresolved:**
- P-Gap OHLC construction is the most severe unresolved dependency and is a
  stated prerequisite for the valid-breakout/trigger chain.
- F12 trigger precedence depends on the P-Gap prerequisite.
- F15 bearish source geometry is not promoted.

**Can any portion freeze?** No. The gate rule is all-or-nothing: any single
`CANDIDATE`/`UNRESOLVED` field keeps the gate `BLOCKED`. Frozen Geometry must
remain **BLOCKED**.

---

## 2. Validation readiness

**Status: NOT READY for formal validation — LOCKED (scope-blocked).**

**Are existing backtest/robustness artifacts descriptive only?** Yes. The
repeated standing statement across the 2026-09-16 → 2026-09-20 artifacts is
that the robustness/backtest evidence is **descriptive/research evidence only**
and is **not** untouched validation.

**What blocks formal validation:** canonical geometry is not frozen. Untouched
validation requires a frozen rule set; nothing is canonical to validate at full
scope. Therefore Validation remains **LOCKED / scope-blocked** (mapped to
PARTIAL under the restricted status vocabulary).

**Is the validation pipeline ready or does it need change?** The harness
pipeline exists and is green (frozen-geometry gate, golden fixture, integrity
invariants, fixture runner, validation-report contract; test baseline 32 files /
124 tests). It does **not** need structural change — it is **ready to run once
geometry is frozen**. What it needs is a canonical input, not a pipeline change.
No pipeline change is proposed.

---

## 3. Robustness / Stability status

**Status: READY as an evidence repository; NOT READY for parameter/rule
promotion.**

Artifact-by-artifact classification (all under `artifacts/`):

| Artifact | Category | Evidence / Experiment |
|---|---|---|
| `SP2L_rr_sensitivity_1R_2R_3R_2026-09-14_2026-09-18.json` | RR sensitivity | **EXPERIMENT** (descriptive) |
| `SP2L_rr_trailing_3x4_matrix_2026-09-14_2026-09-18.json` | RR × trailing grid | **EXPERIMENT** |
| `SP2L_trailing_stability_matrix_5_10_15_20pip_2026-09-14_2026-09-18.json` | trailing grid | **EXPERIMENT** |
| `SP2L_trailing_10pip_m1safe_2026-09-14_2026-09-18.json` | trailing 10-pip M1-safe | **EXPERIMENT** |
| `SP2L_trailing_10pip_management_experiment_2026-09-14_2026-09-18.json` | trailing management | **EXPERIMENT** |
| `SP2L_candle_level_evidence_2026-09-14_2026-09-18.json` | candle-level dependency | **EXPERIMENT** |
| `SP2L_candle_level_dependency_stability_2026-09-14_2026-09-18.json` | candle-level dependency stability | **EXPERIMENT** |
| `SP2L_candle_level_assumption_dependency_2026-09-14_2026-09-18.json` | candle-level assumption | **EXPERIMENT** |
| `author-replica-mt5-nonoverlap-stability.json` | non-overlap stability | **EXPERIMENT** |
| `SP2L_parameter_stability_4week_81_matrix_2026-09-19.json` + main effects + statistical uncertainty + multiple-testing guard | 4-week surface | **EXPERIMENT** (with S5 multiple-testing guard PASS; descriptive uncertainty limits) |

**Which are evidence, which are pure experiment:** none of the robustness
artifacts is canonical source evidence. They are **descriptive experiments**
that document observed stability on a research data window. The only items that
carry *source-evidence* weight are the source-resolution artifacts
(transcript/frames/BATCH audits), and those establish concepts, not rules.

**Gate note:** the 2026-09-19 Combined Readiness Audit classified Parameter
Stability as **INCONCLUSIVE — NO PASS / NO FAIL** (one materially weaker week;
development-sample not untouched validation). This must not be misread as
robustness acceptance.

---

## 4. MT5 Data readiness

**Status: READY for research use, with tracked caveats. Live execution stays
DISABLED.**

**Acquisition:** complete. Deterministic XAUUSD.ecn M1 acquisition toolchain
(`mt5_acquire_xauusd_m1*.py`, `mt5_export_xauusd_m1.py`) and acquisition
manifests (`data/mt5-acquisition/*.manifest.json`) exist.

**Provenance:** recorded per dataset in the [MT5 Provenance Map](docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md) — source, symbol, timeframe, UTC range, bars, gaps, SHA-256, audit status, allowed use.

**Session matrix:** session-availability audits and the multi-week matrix exist;
the MT5 session calendar acquisition (`Sp2lSessionCalendarDump.mq5`) captures
raw broker-reported trade/quote sessions without interpretation.

**Timestamp caveat (explicitly tracked):** the MT5 candle timestamp basis is
**not assumed UTC**; the session-calendar id
`xauusd-ecn-session-current-observation-2026-09-17` has historical applicability
**UNVERIFIED**. UTC is canonical for *stored historical* datasets (established by
the downloader), but the live MT5 terminal's timestamp basis carries the caveat.
Any timestamp-dependent result inherits this tracked assumption.

**Allowed usage / limits:**
- Research datasets may power replica / stability / holdout work only under the
  frozen research configuration; expanding coverage is not a tuning opportunity.
- No synthetic candles, no gap-filling.
- The **Fresh Holdout** boundary `2026-09-19 00:00 UTC` is untouched
  (`HOLDOUT_DATA_UNAVAILABLE`).

**Live execution: DISABLED** (`LIVE_TRADING_ENABLE=false`). No live execution is
enabled by this checkpoint. Execution infra remains READY / GUARDED FOR DRY-RUN
only.

---

## Gate rollup — who can transition

| Gate | Status | Can transition? |
|---|---|---|
| Source Resolution | **PARTIAL** | Not yet — no new primary evidence; 0/7 executable fields confirmed |
| Frozen Geometry | **BLOCKED** | No — all-or-nothing rule, 7/7 fields below SOURCE_CONFIRMED |
| Validation | PARTIAL (scope blocked) / LOCKED | No — requires frozen canonical geometry |
| Robustness / Stability | PARTIAL (descriptive only) | Evidence-only; not promotable |
| Fresh Holdout | BLOCKED | No — boundary untouched; `HOLDOUT_DATA_UNAVAILABLE` |
| MT5 Data | PARTIAL (ready w/ caveats) | Yes for research use; live execution stays DISABLED |
| Production / Live | BLOCKED / DISABLED | No |

**Conclusion:** the project is **infrastructure-ready for the research pipeline
but not gate-ready to advance past Source Resolution.** Downstream stages
(Validation, Robustness promotion, Fresh Holdout, Production) can only move when
Frozen Geometry reaches READY, which requires new primary source evidence that
uniquely resolves the executable fields. No such evidence is in the archive
(confirmed by the 2026-09-20 full re-audit).

## Related

- [Source Resolution Closure Report](docs/research/SP2L_SOURCE_RESOLUTION_CLOSURE_REPORT_2026-09-20.md)
- [Gate Status Dashboard](docs/research/SP2L_RESEARCH_GATE_STATUS_2026-09-20.md)
- [Combined Readiness Audit](docs/research/SP2L_COMBINED_READINESS_AUDIT_2026-09-19.md)
- [Canonical Validation Readiness Ledger](docs/research/SP2L_CANONICAL_VALIDATION_READINESS_LEDGER_2026-09-16.md)
- [MT5 Provenance Map](docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md)