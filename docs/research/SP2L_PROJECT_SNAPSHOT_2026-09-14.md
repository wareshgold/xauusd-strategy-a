# SP2L Project Snapshot — 2026-09-14

## Project state
Research-first / source-first deterministic XAUUSD Strategy A (SP2L = Spike → 2 Leg).
No unresolved geometry has been promoted to canonical rules.

## Current branch / commit
- Branch: `research/sp2l-g388-dataset-runner-2026-09-13`
- HEAD: `248c6e52ae7ce6cc045b88035de14683ffd14ad1`
- Latest commit: `docs: document G400 geometry freeze gate`
- PR: #124 — `research: validate G393 hypothesis batch on current branch`
- Base branch: `research/sp2l-g386-dev-harness-2026-09-13`
- Base SHA: `523bed70d0c935664a8d80e59c3f8c10c516bf12`

## CI gate state
G346/G347 path corrections and the existing affected research gates were green at the prior synchronized HEAD. G400 is newly added and its workflow is now attached to this branch; its purpose is to fail closed until source-critical geometry is resolved.

No blind rerun was used.

## G346 / G347 resolution
- G346 test path is corrected to the actual root-level test file `tests/sp2l-v2-g346-source-evidence-gap-hunt.test.ts`.
- G347 test path is corrected to the actual root-level test file `tests/sp2l-v2-g347-parameterized-geometry-research.test.ts`.
- G347 remains research-only. Its parameterized geometry candidates are explicitly non-canonical.
- No P-Gap formula, A/B/C/D anchor mapping, fill-as-C rule, or AB=CD tolerance was promoted.

## G399 semantic freeze
G399 freezes only the source-confirmed/source-supported semantic layer. It intentionally retains executable geometry as unresolved and cannot manufacture a canonical executable candidate.

## G400 geometry freeze gate
Added:
- `src/domain/research/sp2l-v2/G400GeometryFreezeGate.ts`
- `tests/sp2l-v2/g400-geometry-freeze-gate.test.ts`
- `.github/workflows/research-sp2l-g400-geometry-freeze-gate.yml`
- `docs/research/G400_GEOMETRY_FREEZE_GATE.md`

G400 currently reports **BLOCKED** with seven source-critical blockers:
1. P-Gap OHLC geometry/formula
2. A/B/C anchors and wick/body semantics
3. AB=CD equality tolerance
4. exact pending-limit price/fill semantics
5. entry trigger/persistence/activation/invalidation-before-fill semantics
6. structural stop boundary / executable stop price
7. TP1/TP2 mapping to executable prices

G400 is a gate, not a geometry freeze. Synthetic discrimination or profitable backtests cannot clear a source-evidence blocker.

## Source / geometry status
- G337: PASS — wick/body anchor source audit; exact OHLC mapping unresolved.
- G338: PASS — structural anchor/event source audit; semantic A/B/C/D roles supported, exact candle-field mapping unresolved.
- G346: PASS — source-evidence gap hunt; unresolved geometry remains explicitly unresolved.
- G347: PASS — parameterized geometry research; competing interpretations remain non-canonical.
- G397: PASS — synthetic geometry discrimination; no hypothesis promotion.
- G399: semantic core frozen; executable geometry remains unresolved.
- G400: BLOCKED by the seven source-critical geometry dimensions above.
- P-Gap executable geometry remains unresolved.
- AB=CD relationship is source-confirmed; exact A/B/C/D anchors and tolerance remain unresolved.
- Pending-limit entry is source-confirmed; fill price is not automatically geometric C.

## Research gate position
The project is still before FROZEN GEOMETRY.

Required sequence remains:
SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION

The green research harness validates source discipline and test integrity; it does not freeze Strategy A geometry and does not authorize historical optimization or production deployment.

## Documentation synchronization
The previously discussed Phase 48 source-geometry-freeze-readiness artifact is not present on this branch and is therefore not treated as part of the current branch state.

## Next research target
Use authoritative source material and targeted synthetic minimal-pair fixtures to resolve the seven G400 blockers. Start with the highest-information geometry questions, without choosing formulas or anchors in advance.

Do not optimize historical performance until geometry is frozen.
Do not alter production logic to resolve research/documentation gates.
