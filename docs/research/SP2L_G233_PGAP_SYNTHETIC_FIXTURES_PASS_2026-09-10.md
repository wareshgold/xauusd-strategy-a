# SP2L G233 — P-Gap Synthetic Fixtures PASS

**Date:** 2026-09-10  
**Gate:** SYNTHETIC FIXTURES  
**Status:** `PASS_RESEARCH_ONLY`

## Validation target

G228/G231 research-only P-Gap discrimination fixtures were executed by the dedicated CI workflow introduced in G230.

## CI evidence

Workflow: `Research P-Gap fixtures`  
Run: `34460543562`  
Run number: `5`  
Head tested: `e1de3094f6fc3f498455e696e384acbb74ce86e1`  
Conclusion: `success`  
Job: `pytest-pgap-fixtures`  
Pytest step: `python -m pytest -q research/fixtures/test_sp2l_pgap_synthetic_fixtures_g228.py`  
Result: `success`

The fixture correction recorded in G231 was therefore validated by CI. The corrected PG-06 expectation is consistent with the intended discrimination: strict full-extrema H1 fails on exact touch while the body-only candidate may still pass.

## What this PASS establishes

- deterministic research fixture execution is wired into CI;
- the G228 candidate predicates are covered by executable tests;
- exact-touch, insufficient-history, wick/body discrimination, and explicit-context handling are tested;
- the fixture suite is internally consistent after the G231 correction.

## What this PASS does NOT establish

This gate does **not** establish the canonical SP2L P-Gap geometry.

It does not prove:

- P-Gap = generic three-candle Gap;
- P-Gap = Breakout Gap;
- P-Gap = Pressure Gap;
- P-Gap = FVG;
- exact candle indexing;
- wick versus body boundaries;
- minimum gap size;
- mandatory close-at-previous-high condition;
- bearish mirror geometry;
- overlap/touch tolerance for the canonical rule.

No historical optimization, profitability result, or production signal logic is used as source evidence.

## Gate decision

**Synthetic Fixtures: PASS.**

**Source Resolution: remains BLOCKED at executable P-Gap geometry.**

**Frozen Geometry: remains BLOCKED.**

**DEV / VAL / Fresh Holdout / Production: unchanged and not authorized.**

## Next step

Proceed to the next source-resolution pass: targeted inspection of raw SP2L real examples where the actual candles and the P-Gap region coexist, with the objective of uniquely mapping the source-drawn P-Gap boundaries to candle OHLC. Any candidate geometry remains research-only until source uniqueness is demonstrated.
