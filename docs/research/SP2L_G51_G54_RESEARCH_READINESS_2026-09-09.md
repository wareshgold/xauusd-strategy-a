# SP2L G51-G54 Research Readiness Bundle — 2026-09-09

## Scope
This bundle advances strategy-neutral research infrastructure after the real G50 XAU/USD M1 dataset acquisition. It does not freeze Strategy A geometry and does not generate BUY/SELL signals.

## G51 — M1 to M5
`research/engine/data.py` already provides fixed-bucket OHLC aggregation. `research/engine/timeframes.py` adds a strict M1→M5 wrapper with UTC bucket anchoring and an explicit rule: incomplete or gapped five-minute buckets are omitted rather than synthesized.

This is data transformation only. It is not a Strategy A rule.

## G52 — Dataset readiness
`research/engine/dataset_package.py` loads the committed dataset manifest and produces deterministic split summaries. It checks that every chunk reports PASS quality and that chronological split boundaries are contiguous.

The package treats DEV, VAL, and FRESH_HOLDOUT as separate chronological research periods. It does not expose FRESH_HOLDOUT for parameter selection.

## G53 — Neutral baselines
`research/engine/baselines.py` defines:
- an explicit flat/null model: zero trades and zero return;
- a descriptive long-only price baseline from first open to final close, with simple path drawdown.

These are benchmarks only. They do not infer or implement Strategy A behavior.

## G54 — Synthetic execution harness
The existing strategy-neutral event/backtest infrastructure from G35 remains the execution harness. Its purpose is to test fill, stop, target, expiry, and intrabar-path mechanics before any Strategy A geometry is frozen. OHLC/OLHC path policies remain synthetic conventions and must not be interpreted as source rules.

## Fixture coverage
`research/engine/test_readiness_g51_g53.py` covers:
- deterministic M1→M5 aggregation;
- UTC bucket anchoring;
- rejection of incomplete/gapped buckets;
- chronological split-contiguity checks;
- null and price baseline behavior.

## Gate state
- G50 data acquisition/integrity: PASS based on the committed real dataset.
- G51 data transformation: READY/PASS at unit-test level.
- G52 dataset readiness package: READY/PASS at unit-test level.
- G53 neutral baseline primitives: READY/PASS at unit-test level.
- G54 synthetic execution harness: existing G35 infrastructure remains READY; no new Strategy A semantics are introduced here.
- Frozen Geometry: **BLOCKED**.
- Historical Strategy A validation: **LOCKED** until source geometry B1–B6 is resolved/frozen.

## Non-negotiable boundary
No P-Gap formula, Entry anchor, SL boundary, trigger acceptance rule, AB=CD anchor/tolerance, Leg2 projection, session filter, or pending-order replacement threshold is invented by this bundle.

No historical profitability result may be used to decide what the source means.
