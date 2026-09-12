# SP2L G229 — P-Gap Synthetic Fixture Test Report

**Date:** 2026-09-10
**Gate:** SYNTHETIC FIXTURES
**Status:** `FIXTURE_TESTS_ADDED_CI_PENDING`

## Scope

G228 converts the previously specified P-Gap discrimination cases into deterministic research-only Python fixtures and tests. The implementation is intentionally source-neutral: it evaluates candidate predicates without selecting a canonical SP2L P-Gap geometry.

## Implemented candidate predicates

1. H1 generic bullish Gap candidate: `High[t-2] < Low[t]`.
2. Body-only bullish Gap candidate: earlier body high below current body low.
3. H2 wrapper: H1 plus an explicitly supplied breakout-context boolean.

The H2 wrapper returns `UNKNOWN` when the contextual mapping is not supplied. It therefore does not invent which candle, close, or location rule is canonical.

## Fixture coverage

- PG-01: clean bullish wick gap.
- PG-02: wick overlap with body separation; discriminates full-extrema vs body-only candidates.
- PG-03: generic gap with explicitly supplied breakout context.
- PG-04: generic gap with context absent/false; distinguishes generic gap from context-gated candidate.
- PG-05: adjacent separation without the H1 t-2 relation; indexing discriminator.
- PG-06: exact-touch boundary; verifies strict `<` rather than accidental `<=`.
- insufficient-history case: returns `UNKNOWN` rather than guessing.

## Internal correction from G227

The original G227 table marked PG-03 H2 as PASS. That was too strong because the fixture did not encode a source-unique close/location mapping. G228 treats the contextual input explicitly and keeps the mapping outside the predicate. This prevents the test suite from freezing an invented Breakout-Gap formula.

## Expected test outcome

All G228 fixture assertions are deterministic and internally consistent. CI execution is required before recording a PASS for the repository test gate.

## Safety boundary

These tests must remain research-only. They do not authorize:

- canonical P-Gap production detection;
- generic FVG substitution;
- a frozen P-Gap formula;
- bearish geometry;
- historical optimization;
- BUY/SELL generation.

## Gate impact

- Source Resolution: **BLOCKED at executable P-Gap geometry**
- Synthetic Fixtures: **IMPLEMENTED; CI PENDING**
- Frozen Geometry: **BLOCKED**
- DEV/VAL/Production: **UNCHANGED / NOT AUTHORIZED**

## Provenance

- Source hypothesis matrix: G227
- Three-example source cross-check: G226
- Generic/Breakout Gap cross-check: G225
- G228 implementation: `research/fixtures/sp2l_pgap_synthetic_fixtures_g228.py`
- G228 tests: `research/fixtures/test_sp2l_pgap_synthetic_fixtures_g228.py`
