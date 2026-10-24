# SP2L Stage 0 Baseline Audit — Existing Matrix Inventory
Date: 2026-10-17
Review type: static source/artifact inspection on `research/factory-candidate-lab-20261010` at base commit `5c9f6fe2167885d16a1367b54a8c49449d907274`.
No code executed, no MT5 connected, and no local artifacts changed.

## Executive result

The repository already contains several research matrices. Do not build a duplicate optimizer until their overlap, units, entry population, and replay semantics are reconciled. The immediate blocker is not a lack of parameter-grid code; it is establishing which engine/config/data population matches the user's current RR2/TRAIL4 forward implementation.

## Existing relevant research assets

- `scripts/run_sp2l_v3_historical_trailing_matrix.py`: 240 variants per window = 6 activation values × 10 trailing distances × 2X ON/OFF × RR1/RR2. Uses MT5 M1 history and a V2 detector/entry geometry; constants declare `PIP_SIZE = 0.01`. Same-bar SL/TP is ambiguous. Its 1M and 3M windows overlap (the 1M interval is nested within 3M), so the shorter window is not independent validation.
- `scripts/run_sp2l_v3_mt5_actual_trailing_matrix.py`: uses actual MT5 deal history to construct an observed-trade population, then runs counterfactual exits; its pip conversion is imported from `sp2l_v3_config.py`.
- `scripts/sp2l_v3_config.py`: frozen V3 research config declares `XAU_PIP_SIZE_PRICE = 0.1`, `TRAIL_PIPS = 10`, `TRAIL_DISTANCE_PRICE = 1.0`, `TP_R = 1.0`, `P_GAP_PRICE = 1.0`, `MAX_SL_DISTANCE = 10.0`, `ORDER_MODE = PENDING_LIMIT_RESEARCH`, and `SL_ANCHOR = SPIKE_CANDLE_EXTREME_RESEARCH`. This is a research config, not a source-confirmed canonical rule.
- `scripts/analyze-sp2l-rr-trailing-matrix.py`: older 3×4 R:R/trailing matrix over archived candle evidence; declares `PIP_SIZE = 0.10`, preserves archived entry/SL, updates trailing from favorable candle extremes for the next candle, and marks same-bar SL/TP as ambiguous.
- `scripts/run_sp2l_xauusd_forward_parameter_matrix.py`: much broader matrix that changes P-Gap, spike multiplier, max SL, TP R, and pending TTL. It explicitly labels these as research-only, but those parameters include unresolved entry/stop geometry and must not be mixed into the first exit-only optimization phase.
- `docs/research/SP2L_V3_TRAILING_RESEARCH_RECORD_20261001.md` and `docs/research/SP2L_V3_HISTORICAL_TRAILING_USD_SNAPSHOT_20261004.md`: record prior large sensitivity results and warn that they are diagnostic only, same-bar ambiguity and nested windows limit inference, and no parameter is canonical.
- `artifacts/forensic/SP2L_FORWARD_BACKTEST_PARITY_AUDIT_20260926.md`: records known unresolved parity items: session eligibility mismatch, research pending-limit vs historical touch semantics, timestamp interpretation, fill semantics, and stop anchor.

## Critical findings / risks

### A. Pip/point convention conflict — STOP before any new matrix

At least two matrix paths use different unit constants:
- V2/historical matrix declares `PIP_SIZE = 0.01`.
- Older archived candle matrix declares `PIP_SIZE = 0.10`.
- Current V3 config declares `XAU_PIP_SIZE_PRICE = 0.1`; the V3 historical/actual matrix imports it.

The user environment has previously identified `XAUUSD.ecn` with point=0.01, digits=2 and a user-requested convention of 1 pip = 1 MT5 point = 0.01 price units. That does not automatically rewrite old experiments. Before running any grid, document a per-experiment unit contract and preserve historical result labels. Do not compare Trail4 from the 0.01 path with Trail4 from the 0.1 path as if they were the same distance.

### B. Existing matrix may not be the current forward implementation

The historical matrix reuses V2 detector/entry geometry and counterfactual M1 OHLC. The V3 config uses different research constants and pending-order semantics. The actual-trade matrix begins from already observed MT5 deals, then replays alternate exits. These are different estimands:
- signal-population exit replay;
- counterfactual exits for observed fills;
- actual forward outcomes.

They must be reported separately and cannot be treated as interchangeable evidence.

### C. Same-bar / trailing ordering

The matrix code often treats same-bar SL and TP contact as ambiguous, which is the correct conservative direction absent tick-level ordering. But any method that first updates a trailing SL from the same M1 high/low and then checks the candle low/high may still imply intrabar ordering that OHLC cannot prove. Confirm the exact loop ordering and compare with a next-bar-only variant or tick replay where reliable ticks exist. Do not erase ambiguous outcomes to make the top candidate look stronger.

### D. The 2X counterfactual needs a correctness test

In the historical matrix, the `two_x` option records whether a secondary-entry level was touched; before trusting any 2X comparison, inspect whether that fill actually changes position-level P&L, volume-weighted entry, risk, and TP/SL lifecycle. Prior reports showed 2X ON/OFF equality in USD summaries; that equality is not proof that 2X is irrelevant and could indicate that the flag does not affect the relevant accounting path.

### E. Metrics and sample dependence

Existing artifacts show large raw historical results and high sensitivity to trailing distance. They are hypothesis-generating only. A 1M window nested within a 3M window is not independent validation. Any shortlist must be tested on non-overlapping chronological windows and then a fresh untouched holdout after freezing the code/config/selection rule. Include spread, commission, slippage, execution delays, trade count, max drawdown, expectancy in R, PF, MAE/MFE, ambiguity rate, and uncertainty; do not rank on win rate or raw Net R alone.

## Required Stage 0 tasks before a new run

1. Identify the exact runner/config/commit corresponding to the user's RR2/TRAIL4 forward run last week.
2. Lock its actual parameter meanings, including activation threshold, trailing distance, update cadence, target RR, point/pip conversion, and any execution-side constraints.
3. Select one frozen data source and manifest; audit coverage/gaps/timezone and hash.
4. Reproduce the baseline exactly. If the same trade population, event outcomes, and units cannot be reproduced, do not optimize.
5. Choose the correct estimand for each report (fixed signal population, actual fills counterfactual, or forward observed).
6. Only then run a staged exit-only matrix on the current implementation. Keep MA/EMA, ATR, session, spread, and time filters as separate hypothesis families, with baseline controls and explicit cost/stability checks.
7. Keep P-Gap, spike/entry/SL geometry, fill semantics, and pending-order rules frozen out of the optimization until separately resolved.

## Decision

**Do not launch a new optimization matrix yet.** Reuse and audit the existing matrix tools first. The most urgent issue is the conflicting pip-distance conventions and lack of a demonstrated one-to-one mapping between the current RR2/TRAIL4 forward runner and each historical replay. This is the appropriate next engineering gate; once passed, matrix automation can execute the staged experiment plan without inventing strategy rules.


## Additional audit — RR2/TRAIL4 matrix branch

The separate branch `research/rr2-trail4-trailing-matrix-20261013` contains `scripts/run_sp2l_v3_xauusd_trailing_matrix.py`. It describes a deterministic V3 trailing-management matrix that reuses one MT5 M1 dataset and the imported V3 config, keeps a newly calculated stop inactive until the next completed bar, and does not simulate spread, commission, slippage, or 2X. This is a better starting point for auditing exit-only sensitivity than the broader matrix that also changes P-Gap/spike/max-SL/TTL.

However, it is not yet evidence that the exact current forward RR2/TRAIL4 runner is matched:
- the associated V3 config on that branch declares `XAU_PIP_SIZE_PRICE = 0.1`, while the current environment's requested convention is 0.01 price units per point/pip;
- the V3 config shown in that branch defaults to TP_R=1 and TRAIL_PIPS=10, not the user's RR2/TRAIL4 target;
- the matrix is a historical counterfactual based on theoretical candidate entries, not replay of actual forward fills;
- it explicitly omits transaction costs and 2X.
Thus this matrix should be reused only after a source/config/unit comparison and a reproducible baseline run, not launched unchanged.

The branch also contains an older research record with a three-month 1,522-signal matrix and very large raw Net R / PF values. The report itself notes no spread/slippage/commission, M1 trailing simulation, and ambiguous same-bar outcomes. Treat these as exploratory outputs, not an established edge or an automatic recommendation for Trail 5.

**Required follow-up:** compare the exact current RR2/TRAIL4 branch's runner/config with this matrix script and the actual-forward-trade matrix. Resolve parameter units first; then add a baseline identity test (same candidate IDs, entry/SL/TP, and outcome under the baseline configuration) before generating any parameter sweep.
