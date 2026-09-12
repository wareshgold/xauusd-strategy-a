# SP2L G239 — P-Gap numeric fixtures and deterministic tests

**Date:** 2026-09-10  
**Scope:** research-only synthetic validation  
**Status:** `PASS_RESEARCH_FIXTURE_IMPLEMENTATION__CANONICAL_GEOMETRY_STILL_BLOCKED`

## Objective

Convert the G238 fixture specification into explicit numeric OHLC fixtures and deterministic tests without selecting a canonical SP2L P-Gap definition.

The implementation is intentionally isolated under `research/fixtures/` and is not imported by production strategy code.

## Fixture matrix

| Fixture | Purpose | Strict `High[t-2] < Low[t]` | Inclusive boundary | Body-only | Gap + source spike annotation | Breakout-context hypothesis |
|---|---|---:|---:|---:|---:|---:|
| F1 | Full-extrema separation | PASS | PASS | PASS | PASS | UNKNOWN |
| F2 | Body-only separation with wick overlap | FAIL | FAIL | PASS | FAIL | UNKNOWN |
| F3 | Exact-touch boundary | FAIL | PASS | PASS | FAIL | UNKNOWN |
| F4 | Generic gap, no breakout context | PASS | PASS | PASS | PASS | FAIL |
| F5 | Gap with explicit breakout context | PASS | PASS | PASS | PASS | PASS |
| F6 | Directional move without qualifying gap | FAIL | FAIL | FAIL | FAIL | UNKNOWN |
| F7 | Gap with weak/non-spike intervening candle | PASS | PASS | PASS | FAIL | UNKNOWN |
| F8 | Gap with explicit clear-spike/breakout annotation | PASS | PASS | PASS | PASS | PASS |

## Important design decision

The fixture code does **not** derive `spike` from a numeric threshold. The source has not yet supplied a deterministic spike-size formula, so the tests use an explicit source annotation field to test the logical conjunction `gap + spike` without inventing a threshold.

Likewise, no bearish P-Gap predicate is implemented. The bearish mirror remains unresolved at this gate.

## CI correction record

The first G239 CI execution exposed one fixture expectation error in F6: the OHLC values accidentally allowed the body-only candidate to pass even though the fixture was intended to represent a no-gap directional move. The CI result was `1 failed, 14 passed`.

F6 was corrected so that both full-extrema and body-only gap candidates fail. This is a fixture-data correction, not a strategy-rule optimization.

The corrected branch head is `45586b7fe808add6bb645daec9c61508fa8f77e3`.

## Gate interpretation

- Numeric fixture implementation: **PASS**
- Deterministic candidate tests: **implemented**
- Source geometry resolution: **OPEN**
- Canonical P-Gap formula: **NOT FROZEN**
- Bearish mirror: **NOT FROZEN**
- Historical optimization: **NOT USED**
- DEV authorization: **BLOCKED**
- Validation authorization: **BLOCKED**
- Fresh Holdout: **PROTECTED**
- Production BUY/SELL authorization: **BLOCKED**

## Next step

Run the corrected G239 fixture suite through CI and inspect the result. If green, retain the fixture layer as research infrastructure and continue source-resolution work rather than promoting the strict, body-only, inclusive, or breakout-context hypothesis to canonical Strategy A logic.
