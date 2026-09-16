# SP2L Metric Audit Checklist — 2026-09-16

## Scope

Audit the existing backtest metric semantics before any baseline statistic is considered validation evidence.

## Required assertions

- [ ] Candidate count is reported separately from closed-trade count.
- [ ] OPEN outcomes are counted and reported separately.
- [ ] AMBIGUOUS outcomes are counted and reported separately.
- [ ] Same-bar SL+TP is not silently ordered.
- [ ] Risk distance is positive and extreme-small-risk candidates are surfaced.
- [ ] Extreme R-multiple trades are surfaced for forensic review.
- [ ] Win rate denominator is explicitly documented.
- [ ] Expectancy denominator is explicitly documented.
- [ ] Profit factor treatment when there are no losses is documented.
- [ ] Max drawdown population and ordering are documented.
- [ ] No metric excludes observations without an explicit reason.
- [ ] Re-running the same inputs is deterministic.

## Current known behavior

`BacktestEngine` evaluates each valid candidate twice and calculates metrics from trades whose `rMultiple` is non-null. `OPEN` and `AMBIGUOUS` outcomes therefore do not enter the current closed-trade metrics. A same-candle SL and TP touch is returned as `AMBIGUOUS` with null `rMultiple`. This is an implementation fact to test, not a claim that the policy is canonical market execution semantics.

## Acceptance gate

Metric audit PASS means the accounting semantics are explicit, tested, deterministic, and reproducible. It does not mean the Strategy A geometry is frozen or that the baseline has predictive validity.
