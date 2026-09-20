# SP2L PR #236 — Separation Plan — 2026-09-20

## Purpose

Plan to split PR #236 (`research/sp2l-mt5-session-matrix-2026-09-17-x` →
`main`) so that the **research/session-matrix infrastructure** can move onto the
research path while the **incomplete execution infrastructure** remains isolated
on a separate execution branch.

This plan:
- does **not** modify SP2L strategy logic;
- does **not** delete history or any file;
- proposes branch/file movement only — merge execution is a separate,
  human-gated step.

## Audit basis

Verified directly in a temporary worktree at PR head `2c3aa57`:
- `npm run build` (`tsc --noEmit`) → **93 errors**, including 5 missing-module
  errors in `src/execution` (imports reference `PositionManager`,
  `TrailingStopSafety`, `BrokerConstraintGate`, `PositionModificationAdapter`,
  which do not exist on the PR branch).
- `npx vitest run` → 30 test files present; **28 pass / 2 fail**
  (`PositionModificationPipeline.test.ts` — cannot run, imports missing;
  `sp2l-author-replica-candidate.test.ts` — bearish-mirror assertion fails on
  this lineage).
- `src/domain/*`, `src/backtest/*` (the strategy core) are **identical** on
  `main` and the PR branch — untouched.

Conclusion: the PR is **not currently mergeable**. The blocker is entirely the
isolated `src/execution/**` cluster.

## Classification

### RESEARCH / SESSION-MATRIX — KEEP on the research path

All other 170 files are research infrastructure:

| Group | Files |
|---|---|
| MT5 acquisition | `scripts/mt5_acquire_xauusd_m1*.py`, `mt5_export_xauusd_m1.py`, `SP2L_MT5_*_RUNBOOK/EXECUTION/NEXT_STEP` |
| Session matrix | `scripts/mt5_session_availability_*.py`, `mt5_session_boundary_diagnostic.py`, `Sp2lSessionCalendarDump.mq5`, `research/mt5/README_SESSION_CALENDAR.md`, session-availability findings |
| Provenance | `scripts/mt5_mql5_symbol_session_metadata.mq5`, symbol-session-metadata diagnostics, `SP2L_DATA_PROVENANCE_CONTRACT`, manifest template + JSON manifests |
| Diagnostics | `scripts/mt5_acquisition_diagnostic*.py`, `mt5_copy_rates_from_*.py`, `mt5_*_session_metadata_diagnostic.py` |
| Audit | `scripts/audit-baseline-extreme-r.mjs`, `tests/metric-accounting-audit.test.ts`, `SP2L_*_AUDIT/NOTE` docs |
| Manifests / artifacts | `data/mt5-acquisition/*.manifest.json`, `artifacts/mt5_xauusd_m1_10000.json` |
| Docs | `docs/research/*`, `docs/checkpoints/*`, and `docs/execution/*.md` **(research documents only — no code)** |
| Harness / fixtures | `research/harness/sp2l_*_v1.ts`, `research/fixtures/sp2l_*`, `research/engine/*.py` |
| CI harness passing | `.github/workflows/research-*.yml`, `tsconfig.sp2l-harness.json` |

`docs/execution/*.md` are **documents**, self-marked "RESEARCH / EXECUTION-LAYER
ONLY. No production enablement." They contain no executable code and may stay
with the research docs; only `src/execution/**` is the compile-incompatible
execution code.

### EXECUTION — ISOLATE on a separate execution branch

| File | Reason |
|---|---|
| `src/execution/TrailingExecutionStateMachine.ts` | imports `./PositionManager.js` — missing |
| `src/execution/TrailingExecutionStateMachine.test.ts` | depends on above |
| `src/execution/mt5/BrokerConstraintEvaluation.ts` | imports `./BrokerConstraintGate.js` — missing |
| `src/execution/mt5/BrokerConstraintEvaluation.test.ts` | depends on above |
| `src/execution/mt5/PositionModificationPipeline.ts` | imports `./BrokerConstraintGate.js`, `../TrailingStopSafety.js`, `./PositionModificationAdapter.js` — all missing |
| `src/execution/mt5/PositionModificationPipeline.test.ts` | cannot run; imports missing |

Also note: these four missing dependencies (`PositionManager`,
`TrailingStopSafety`, `BrokerConstraintGate`, `PositionModificationAdapter`)
exist on the **current session branch**
(`research/sp2l-live-mt5-telegram-2026-09-19`), not on this PR branch. Any
execution line must be reconciled with the branch containing those modules, or
the imports added — never by altering strategy geometry.

## Proposed actions (no execution, no deletion)

1. **Create a research slice** (`research-*` or reuse this session-matrix branch)
   containing the RESEARCH group above only — no `src/execution/**`.
2. **Create/keep a separate execution branch** containing ONLY
   `src/execution/**` + the 3 test files, clearly labeled
   "execution-shell / not-yet-compilable on this lineage".
3. **Merge gate discipline:** a research-path merge requires
   `npm run build` + `npm test` green with the slice. The execution slice does
   not enter `main` until its missing modules are supplied and it compiles.
4. **Do not delete** any file of the PR history; branch divergence preserves it.

## Guard state (unchanged)

- Frozen Geometry: **BLOCKED**
- Source Resolution: **PARTIAL**
- Production / Live: **BLOCKED / DISABLED**
- The research split introduces no canonical strategy rules.

## Owner decision needed

None blocking this plan — it only classifies and moves file sets. The actual
merge of either slice is a separate, human-gated action and is not performed
here.