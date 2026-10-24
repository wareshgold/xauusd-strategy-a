# SP2L Artifact Index & Provenance Map — Checkpoint — 2026-09-20

## Scope

Added two research/audit artifacts to give future passes a single entry point
for navigating evidence, validation, experiments, and datasets. No strategy
geometry was changed and no rule was promoted.

## Added

1. **Research Artifact Index**
   `docs/research/SP2L_RESEARCH_ARTIFACT_INDEX_2026-09-20.md`
   - Categories: EVIDENCE / VALIDATION / EXPERIMENT / DIAGNOSTIC.
   - Sections: source-evidence archive, frozen-gate harness & fixtures,
     robustness experiments, MT5 datasets, gate status rollup.
   - Explicitly keeps F10/F11/F12/F14 marked PARTIAL / UNRESOLVED and the
     source-discrimination harness as an evidence-boundary check, not rules.

2. **MT5 Provenance Map**
   `docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md`
   - Per-dataset row: source, symbol, timeframe, range, bars, gaps, SHA-256,
     audit status, allowed use.
   - Covers monthly acquisitions, session-aware/smoke tests, and
     session-availability/forensic sets.
   - Documents timestamp-basis caveat (session calendar applicability
     UNVERIFIED) and the no-synthetic-candle / no-gap-fill standing rules.
   - Consistent with `SP2L_DATA_PROVENANCE_CONTRACT_2026-09-17.md`.

## Verification

- `npm run build` — PASS.
- `npm test` — 32 files / 124 tests PASS (baseline unchanged).

## Gate state (unchanged)

- Source Resolution: PARTIAL
- Frozen Geometry: **BLOCKED**
- Historical Validation: LOCKED
- Robustness / Stability: RESEARCH EVIDENCE ONLY
- Fresh Holdout: UNTOUCHED — boundary `2026-09-19 00:00Z`
- Execution infrastructure: READY / GUARDED FOR DRY-RUN
- Production: BLOCKED · Live trading: DISABLED

## Related

- [Research Artifact Index](docs/research/SP2L_RESEARCH_ARTIFACT_INDEX_2026-09-20.md)
- [MT5 Provenance Map](docs/research/SP2L_MT5_PROVENANCE_MAP_2026-09-20.md)