# SP2L Test Readiness Matrix — 2026-09-16

## Objective

Minimize time from source resolution to deterministic testing without promoting unresolved geometry into canonical Strategy A rules.

## Current gate

- Source Resolution: PARTIAL
- Synthetic Fixtures: ADVANCED
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF

## Source status

| Field | Source status | Test-engine treatment |
|---|---|---|
| F09 Entry anchor | PARTIAL | parameterized/unresolved; no universal latest-HL rule |
| F10 Stop/invalidation | PARTIAL | separate structural invalidation interface; exact OHLC unresolved |
| F11 Limit refresh | PARTIAL | refresh event modeled; numeric threshold unresolved |
| F12 Trigger family | PARTIAL | 1/2/3 candle + Bar/Key-Bar variants represented; classifier unresolved |
| F13 2X | PARTIAL | optional second position represented; exact formula unresolved |
| F14 AB=CD | PARTIAL | Leg2≈Leg1 semantic relation represented; A/B/C/D unresolved |
| P-Gap | UNRESOLVED | no executable formula |

## Engineering work that is allowed now

1. Build fixture runners that accept explicit candidate geometry rather than hidden defaults.
2. Separate signal geometry from execution/fill assumptions.
3. Emit provenance for every geometry field: SOURCE_CONFIRMED, CANDIDATE, or UNRESOLVED.
4. Fail closed when a production/canonical test requests an unresolved field.
5. Keep synthetic discrimination tests independent from historical performance metrics.
6. Prepare deterministic metric/report schemas so validation can begin immediately after geometry freeze.

## Engineering work that is not allowed now

- Historical win-rate optimization.
- Selecting the best candidate geometry from backtest results.
- Inventing stop buffers or ATR substitutions.
- Inventing P-Gap or AB=CD equations/tolerances.
- Treating 2X examples as a universal formula.
- Generating production BUY/SELL decisions.

## Exit condition for historical testing

Historical testing may start only after the source-resolution record explicitly freezes all fields required by the executable Strategy A specification, with no unresolved geometry silently defaulted.

## Fast-path principle

The fastest legitimate path is parallel preparation: finish source evidence and test infrastructure concurrently, then enter Untouched Validation immediately after Frozen Geometry becomes GREEN. Performance cannot be used to resolve source ambiguity.
