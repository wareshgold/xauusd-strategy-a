# SP2L G47 — CI Integrity

Date: 2026-09-09
Gate: G47
Status: FIX APPLIED; CI RUN REQUIRED

## Failure found

The latest Research engine workflow failed in `test_metrics_are_r_based_and_directional` because the fixture expected profit factor `1.0` while its trades actually produced `+2R` and `-1R`, giving profit factor `2.0`.

This was a test-fixture inconsistency, not evidence of a Strategy A result.

## Fixes

- Corrected the R-metric fixture to use symmetric `+1R/-1R` outcomes when asserting profit factor `1.0`.
- Corrected stale `sp2l_engine` imports in research tests to the current `research.engine` package.
- Expanded the CI workflow from one test file to the complete `research/engine` suite.
- CI installs the pinned research dependency file, including cross-platform timezone data.

## Boundary

No Strategy A geometry, BUY/SELL detector, optimization, or profitability claim is introduced by this gate.

## Next decision

The branch must reach green CI across the complete research-engine suite before G47 is marked PASS. Only then should end-to-end provider acquisition proceed.
