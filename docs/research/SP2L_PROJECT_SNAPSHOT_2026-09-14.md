# SP2L Project Snapshot — 2026-09-14

## Project state
Research-first / source-first deterministic XAUUSD Strategy A (SP2L = Spike → 2 Leg).
No unresolved geometry has been promoted to canonical rules.

## Current branch / commit
- Branch: `research/sp2l-g388-dataset-runner-2026-09-13`
- HEAD: `34ba854c3b48320d84322b6e3203c5f1560fdf36`
- Commit: `fix: correct G347 test path`
- PR: #124 — `research: validate G393 hypothesis batch on current branch`
- Base branch: `research/sp2l-g386-dev-harness-2026-09-13`
- Base SHA: `523bed70d0c935664a8d80e59c3f8c10c516bf12`

## CI gate — current HEAD
The Actions runs created for HEAD `34ba854c3b48320d84322b6e3203c5f1560fdf36` completed successfully for the affected research gates, including G397. The G347 correction therefore resolved the remaining Semantic V2 test-path failure chain.

No blind rerun was used.

## G346 / G347 resolution
- G346 test path is corrected to the actual root-level test file `tests/sp2l-v2-g346-source-evidence-gap-hunt.test.ts`.
- G347 test path is corrected to the actual root-level test file `tests/sp2l-v2-g347-parameterized-geometry-research.test.ts`.
- G347 remains research-only. Its parameterized geometry candidates are explicitly non-canonical.
- No P-Gap formula, A/B/C/D anchor mapping, fill-as-C rule, or AB=CD tolerance was promoted.

## Source / geometry status
- G337: PASS — wick/body anchor source audit; exact OHLC mapping unresolved.
- G338: PASS — structural anchor/event source audit; semantic A/B/C/D roles supported, exact candle-field mapping unresolved.
- G346: PASS — source-evidence gap hunt; unresolved geometry remains explicitly unresolved.
- G347: PASS — parameterized geometry research; competing interpretations remain non-canonical.
- G397: PASS — synthetic geometry discrimination; no hypothesis promotion.
- P-Gap executable geometry remains unresolved.
- AB=CD relationship is source-confirmed; exact A/B/C/D anchors and tolerance remain unresolved.
- Pending-limit entry is source-confirmed; fill price is not automatically geometric C.

## Research gate position
The project is still before FROZEN GEOMETRY.

Required sequence remains:
SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION

The current green CI status validates the research harness/path integrity; it does not freeze Strategy A geometry and does not authorize historical optimization or production deployment.

## Documentation synchronization
The previous `SP2L_PROJECT_SNAPSHOT_2026-09-13.md` was stale relative to the current HEAD. This snapshot records the actual HEAD and current CI gate state.

A previously discussed Phase 48 source-geometry-freeze-readiness artifact is not present on this branch at this HEAD and is therefore not treated as part of the current branch state. It must not be assumed present until explicitly added and validated on this branch.

## Next gate
Proceed with source-resolution / synthetic-fixture discrimination needed to close the remaining geometry gaps, while preserving all unresolved dimensions as unresolved until authoritative evidence distinguishes them.

Do not optimize historical performance until the geometry is frozen.
Do not alter production logic to resolve CI/documentation issues.
