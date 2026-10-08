# OFFICIAL PROJECT SNAPSHOT — 2026-10-08

## Project
XAUUSD Strategy A / SP2L (Spike → 2 Leg)

## Snapshot purpose
Official handoff before the next work session. This snapshot freezes the current research position and the exact next objective.

## Repository
- Repo: wareshgold/xauusd-strategy-a
- Local path: D:\Mirzaei\Private\1\xauusd-strategy-a
- Branch: research/sp2l-starnet-engine-integration-20261007
- Snapshot base merge: 82c8a16f18f73558bc75667ac6845d1684f5d7f5
- Latest comparison-boundary fix: befec09c752e8d7ba9d10ff75d4e39ad5351c853

## Source Resolution status
FROZEN RESEARCH BASELINE.

Do not reopen Source Resolution unless new evidence materially changes the implementation or invalidates the current research baseline.

The AlirezaSadabadi implementation is an external implementation/reference only. It is not canonical and must not replace the current source-aligned research baseline.

## Factory status
The Factory now contains the boundary for a provenance-locked 1v1 comparison between:
1. Current internal SP2L V3 research implementation.
2. AlirezaSadabadi/PythonTraderBot SP2L implementation.

Added:
- src/strategy_factory/external_strategy.py
- src/strategy_factory/strategy_comparison.py
- src/strategy_factory/strategy_comparison_runner.py
- tests/test_strategy_comparison.py

External reference:
- repository: AlirezaSadabadi/PythonTraderBot
- path: code/SP2L/SP2L_Advanced_Bot_Optimized.py
- upstream ref: main
- captured blob SHA: 602c6b79d86189e044b9520689d963b746d74b5c
- role: EXTERNAL_REFERENCE

The comparison contract requires:
- exact common dataset identity
- identical execution semantics
- identical execution input fingerprint
- accepted research runs
- immutable provenance fingerprints

The comparison report is descriptive only:
- no automatic winner
- no canonical R inference
- no production eligibility
- no source promotion

## Forward test
Current RR2/TRAIL4 forward test remains independent and must not be modified by the comparison work.

Active research runner/profile:
SP2L_V3_XAUUSD_RR2_TRAIL4_20261001

The forward runner is not being replaced by the external implementation.

## Next objective
Build the ACTUAL historical-data adapters and execute a true 1v1 benchmark:

COMMON FROZEN DATASET
    ↓
Internal SP2L V3
    +
Alireza SP2L
    ↓
same execution assumptions
    ↓
trade-by-trade alignment
    ↓
descriptive metrics
    ↓
statistical comparison

First comparison should isolate the SP2L core as much as practical. Do not silently import Alireza-specific filters, optimization, or management rules into the internal Strategy A.

## Required discipline
- No parameter tuning from the comparison result.
- No backtest-decides-source.
- No AI-decides-canonical.
- No guessed R mapping.
- No mass cleanup of active forward-test artifacts.
- Keep Forward Evidence and R/Trade-Return source boundaries fail-closed.
- The ultimate goal remains a reproducible statistical edge, followed by construction of the user's own Strategy A on top of the validated research base.

## Resume command
After pulling the snapshot:
git pull --ff-only

Then continue with:
ACTUAL BACKTEST ADAPTERS → COMMON DATASET → 1v1 RUN → TRADE ALIGNMENT → VALIDATION.
