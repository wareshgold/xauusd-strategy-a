# SP2L G231 — P-Gap Fixture CI Failure Correction

**Date:** 2026-09-10  
**Gate:** SYNTHETIC FIXTURES  
**Status:** `CORRECTED_CI_RERUN_PENDING`

## CI finding

G230 successfully wired the research-only P-Gap fixture tests into CI, and the first run executed the pytest step but failed.

Run: `34460297659`  
Commit: `cdf149832d4b043bf707aa772ddf041fe1a1b08e`

The failure was in the fixture expectation layer, not in the CI wiring or dependency installation.

## Root cause

PG-06 was designed to test the strict H1 boundary:

`High[t-2] == Low[t]`

Therefore H1 must fail under the strict `<` candidate.

However, the same OHLC values also produce a separated candle-body candidate. PG-06 had incorrectly declared `expected_body_only = FAIL`, which made the deterministic fixture self-inconsistent.

## Correction

PG-06 now declares `expected_body_only = PASS` while retaining:

- H1 = `FAIL`
- exact-touch boundary = preserved
- breakout context = `None`

This keeps the fixture's purpose precise: it discriminates strict full-extrema gap logic from body-only gap logic without conflating the two hypotheses.

## Safety boundary

No canonical P-Gap geometry is promoted. No production code is changed. No historical data or optimization is involved.

## Next validation

The next CI run must be inspected before recording a Synthetic Fixtures PASS.

## Gate impact

- Source Resolution: **BLOCKED at executable P-Gap geometry**
- Synthetic Fixtures: **CORRECTION APPLIED; CI RERUN PENDING**
- Frozen Geometry: **BLOCKED**
- DEV/VAL/Production: **UNCHANGED / NOT AUTHORIZED**
