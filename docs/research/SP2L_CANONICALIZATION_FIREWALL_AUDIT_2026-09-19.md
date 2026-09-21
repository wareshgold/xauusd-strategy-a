# SP2L Canonicalization Firewall Audit — 2026-09-19

## Purpose

Verify that the current research/holdout/live-execution paths do not silently promote the author-replica candidate geometry into canonical Strategy A or production execution.

## Findings

### Research candidate path

`scripts/run-author-replica-mt5-nonoverlap-stability.py` explicitly declares itself research-only and uses a candidate signal implementation.

Its current candidate implementation contains concrete P-Gap, spike, entry, and SL expressions. Those expressions are therefore treated as **author-replica research geometry**, not frozen Strategy A source geometry.

The script also applies configurable research parameters:

- P-Gap price threshold
- spike body multiplier
- maximum SL distance
- TP R multiple

This is acceptable for the archived robustness experiment because the experiment is explicitly labelled candidate/research and is not used to define source meaning.

### Fresh Holdout path

`scripts/run-author-replica-mt5-fresh-holdout.py` imports the existing author-replica signal implementation but freezes its configuration and records integrity flags.

It explicitly records:

- parameter sweep = false
- parameter tuning = false
- post-result subperiod selection = false
- source geometry changed = false
- fill semantics changed = false
- unresolved AB=CD defined from holdout = false
- Leg1=Leg2 promoted = false

The current holdout status remains data-unavailable because no eligible post-boundary M1 history was returned. No result is therefore being used to promote geometry.

### Live execution gateway

`scripts/live_mt5_gateway.py` is correctly separated from Strategy A discovery.

The gateway:

- accepts an externally produced APPROVED signal;
- validates signal fields;
- does not calculate P-Gap;
- does not calculate AB=CD;
- does not select Entry/SL/TP from market geometry;
- does not define trigger semantics;
- defaults `LIVE_TRADING_ENABLE=false`;
- preserves duplicate-signal rejection;
- keeps public Telegram output branded Nexora.

Therefore the gateway is an execution boundary, not a canonical Strategy A rule engine.

## Boundary decision

No canonicalization leakage was identified in the reviewed paths.

However, the author-replica signal implementation remains a concrete candidate geometry implementation. It must continue to be treated as **non-canonical** until the Frozen Geometry gate passes.

The existence of a deterministic implementation in the research runner is not evidence that the source has supplied the same deterministic rule.

## Required guard

Any future code change that moves candidate expressions from the author-replica/research namespace into canonical Strategy A modules must require an explicit source-resolution review and Frozen Geometry gate update.

Backtest performance, robustness, stability, or holdout behavior must never be accepted as the reason for that promotion.

## Gate impact

- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Parameter Robustness: POSITIVE RESEARCH EVIDENCE
- Parameter Stability: INCONCLUSIVE
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Execution infrastructure: READY / GUARDED
- Live Trading: DISABLED
- Production Authorization: BLOCKED

No strategy rule, signal, parameter, or execution setting was changed by this audit.
