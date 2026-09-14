# SP2L Project Snapshot — 2026-09-14

## Project state
Research-first / source-first deterministic XAUUSD Strategy A (SP2L = Spike → 2 Leg).
No unresolved geometry has been promoted to canonical rules.

## Current branch / commit
- Branch: `research/sp2l-g388-dataset-runner-2026-09-13`
- HEAD: `b53afd684fbe03fe09066d19de49b325576fa71d`
- Latest commit: `research: register G404 structural stop boundary test`
- PR: #124 — `research: validate G393 hypothesis batch on current branch`
- Base branch: `research/sp2l-g386-dev-harness-2026-09-13`
- Base SHA: `523bed70d0c935664a8d80e59c3f8c10c516bf12`

## CI gate state
G346/G347 path corrections and the affected research gates are green at the current synchronized HEAD. G400 remains a blocking gate until source-critical geometry is resolved. G401, G402, G403, and G404 are source-resolution research gates and currently pass their deterministic guard suites while intentionally remaining unresolved.

No blind rerun was used.

## G346 / G347 resolution
- G346 test path is corrected to the actual root-level test file `tests/sp2l-v2-g346-source-evidence-gap-hunt.test.ts`.
- G347 test path is corrected to the actual root-level test file `tests/sp2l-v2-g347-parameterized-geometry-research.test.ts`.
- G347 remains research-only. Its parameterized geometry candidates are explicitly non-canonical.
- No P-Gap formula, A/B/C/D anchor mapping, fill-as-C rule, or AB=CD tolerance was promoted.

## G399 semantic freeze
G399 freezes only the source-confirmed/source-supported semantic layer. It intentionally retains executable geometry as unresolved and cannot manufacture a canonical executable candidate.

## G400 geometry freeze gate
G400 currently reports **BLOCKED** with seven source-critical blockers:
1. P-Gap OHLC geometry/formula
2. A/B/C anchors and wick/body semantics
3. AB=CD equality tolerance
4. exact pending-limit price/fill semantics
5. entry trigger/persistence/activation/invalidation-before-fill semantics
6. structural stop boundary / executable stop price
7. TP1/TP2 mapping to executable prices

G400 is a gate, not a geometry freeze. Synthetic discrimination or profitable backtests cannot clear a source-evidence blocker.

## Source-resolution gates
- G401: PASS — P-Gap source-resolution guard suite; executable P-Gap geometry remains unresolved.
- G402: PASS — AB=CD anchor source-resolution guard suite; A/B/C/D anchors, price field, wick/body semantics, and tolerance remain unresolved.
- G403: PASS — entry execution source-resolution guard suite; exact pending-limit price, trigger/persistence, fill semantics, and pre-fill invalidation remain unresolved.
- G404: PASS — structural stop boundary source-resolution guard suite; stop reference, boundary, price field, buffer, invalidation timing, and executable stop mapping remain unresolved.

G401–G404 passing means the research gates correctly preserve uncertainty and prevent unsupported promotion; it does not mean the underlying geometry has been resolved.

## Source / geometry status
- G337: PASS — wick/body anchor source audit; exact OHLC mapping unresolved.
- G338: PASS — structural anchor/event source audit; semantic A/B/C/D roles supported, exact candle-field mapping unresolved.
- G346: PASS — source-evidence gap hunt; unresolved geometry remains explicitly unresolved.
- G347: PASS — parameterized geometry research; competing interpretations remain non-canonical.
- G397: PASS — synthetic geometry discrimination; no hypothesis promotion.
- G399: semantic core frozen; executable geometry remains unresolved.
- G400: BLOCKED by the seven source-critical geometry dimensions above.
- G401: PASS / unresolved.
- G402: PASS / unresolved.
- G403: PASS / unresolved.
- G404: PASS / unresolved.
- P-Gap executable geometry remains unresolved.
- AB=CD relationship is source-confirmed; exact A/B/C/D anchors and tolerance remain unresolved.
- Pending-limit entry is source-confirmed; fill price is not automatically geometric C.
- Structural stop remains source-supported at the semantic level, but executable stop geometry is unresolved.

## Research gate position
The project is still before FROZEN GEOMETRY.

Required sequence remains:
SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION

The green research harness validates source discipline and test integrity; it does not freeze Strategy A geometry and does not authorize historical optimization or production deployment.

## Documentation synchronization
The previously discussed Phase 48 source-geometry-freeze-readiness artifact is not present on this branch and is therefore not treated as part of the current branch state.

## Next research target
Proceed to the next highest-information source-resolution question after G404, while preserving the seven G400 blockers as unresolved until authoritative source evidence resolves them. Do not choose formulas, anchors, tolerances, buffers, or execution semantics in advance.

Do not optimize historical performance until geometry is frozen.
Do not alter production logic to resolve research/documentation gates.
