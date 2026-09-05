# Nested Conditional Information Protocol

## Purpose

Replace the previous partial-Spearman diagnostic with a direct information-theoretic test of whether later post-entry path state contains incremental information about final trade outcome after earlier path state is known.

## Primary nested hypothesis

For final outcome `Y = final R` and post-entry MAE checkpoints:

1. `I(Y; T1_MAE)` — information already visible at T1.
2. `I(Y; T2_MAE | T1_MAE)` — incremental information arriving at T2 after T1 is known.
3. `I(Y; T3_MAE | T1_MAE, T2_MAE)` — incremental information arriving at T3 after T1 and T2 are known.

A positive marginal association at T2 or T3 is not sufficient. The relevant quantity is the conditional mutual information of the newly observed state.

## Estimator

The implementation uses empirical discrete conditional mutual information:

`I(Y; X | C) = H(Y | C) - H(Y | C, X)`

Values are reported in nats.

Continuous variables are discretized with equal-frequency quantile bins. Bin edges are fitted **only on DEV** and then frozen for VAL. Three fixed bin counts (3, 4, 5) are reported together; none is selected as a winning parameter.

## Null test

For each conditional-information measurement, the candidate feature is permuted within exact control strata while the outcome and controls remain fixed. The empirical p-value is computed from 499 deterministic permutations using seed `20260905` plus a feature/bin offset.

This tests whether the candidate contains information about the outcome beyond the specified controls under a conditional-independence null.

## Chronological protocol

- Historical data only.
- Delay exactly 1.
- PRE window: first 10,000 candles used by this research branch.
- DEV: first 6,000 candles.
- VAL: next 4,000 candles.
- Fresh Holdout is excluded completely.
- No threshold optimization.
- No production Strategy A changes.
- Same-candle ambiguity remains excluded through the baseline trade join.

## Interpretation gate

No candidate is promoted because CMI is merely positive. A useful lead should show a non-trivial incremental CMI that is reasonably stable across fixed bin counts and survives the chronological VAL evaluation without requiring a parameter choice discovered from VAL.

The analysis is diagnostic until a separate hypothesis is frozen and subjected to the project's normal DEV → VAL → Fresh Holdout promotion protocol.
