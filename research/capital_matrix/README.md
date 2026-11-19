# SP2L Capital Management Matrix (research only)

This package defines the reproducible experiment population and the first risk-sizing primitives for the capital-management study.

## Agreed primary matrix

Initial capital: **USD 1,000**. Risk fractions: **0.25%, 0.50%, 0.75%, 1.00%**. Each sizing mode is evaluated independently:

- `COMPOUND`: risk budget = current equity × risk fraction.
- `FIXED_BASE`: risk budget = initial capital × risk fraction.

| Family | Variants | Sizing modes | Runs |
|---|---:|---:|---:|
| Fixed TP | 5 targets: 1R, 1.5R, 2R, 3R, 4R | 2 × 4 risk levels | 40 |
| Two independent positions | 5 TP pairs: 1R/2R, 1R/3R, 1R/4R, 1.5R/3R, 2R/4R | 2 × 4 risk levels | 40 |
| Exact V3.1 runner reference | Historical 0.01 lot, exact declared profile | None | 1 |
| Risk-normalized V3.1 runner | Same exit profile, four risk levels | 2 × 4 risk levels | 8 |
| **Total** | | | **89** |

Dual-position configurations allocate half of the *aggregate* risk budget to each independent position. The two legs do not each receive the full risk budget. A separate fixed 0.01 + 0.01 diagnostic is intentionally not part of the 89 primary runs and must be labelled infeasible whenever it breaches the aggregate risk budget.

The exact runner reference remains a fixed-volume historical benchmark. It must not be silently relabelled as a risk-normalized run.

## Risk sizing contract

Lot size is calculated from actual broker contract metadata:

`risk per lot = (stop distance / tick size) × tick value per lot`

Volume is rounded **down** to the broker volume step. If the result is below minimum volume, the leg is explicitly marked infeasible; the code never rounds up to force a trade. Broker metadata must come from the actual instrument/account specification and be recorded with the run evidence. Example values in tests are synthetic fixtures, not XAUUSD broker claims.

## Current implementation boundary

Implemented:
- deterministic enumeration and stable IDs for all 89 primary configurations;
- compound and fixed-base risk budgets;
- contract-aware volume sizing with downward step rounding;
- equal aggregate-risk split for the two independent legs;
- explicit infeasibility below broker minimum volume;
- exact fixed-0.01-lot runner reference representation;
- unit tests for the above invariants.

Not yet implemented:
- trade execution/replay engine;
- precise V3.1 trailing event semantics and same-bar path handling;
- spread, commission, swap and slippage calibration;
- chronological development/validation/Fresh Holdout pipeline;
- metrics, robustness, Monte Carlo and sortable ranking output.

These are deliberate gates. Do not publish performance results or rank configurations until those components are implemented, tested, and supplied with the byte-bound historical dataset and the common frozen entry population.

## Required input evidence before replay

1. Preserved three-month M1 CSV.GZ with the audited SHA-256 from the V3.1 population specification.
2. Frozen V3.1 entry CSV and manifest generated from that exact source.
3. Tick data sufficient to resolve intrabar trailing/SL/TP ordering and calibrate costs, or an explicit lower-evidence OHLC policy.
4. Broker contract metadata: tick size/value, volume min/max/step, account currency, commission schedule, swap, spread and execution assumptions.
5. SHA-256 values for every input, source file, config and output.

M1 source currently documented in the repository spans 2026-08-10 through 2026-11-09, has 89,866 bars and 66 timestamp gaps. It is not a complete interval. The source CSV.GZ itself is not stored in this repository. Gap-exposed trades must remain ambiguous; never interpolate missing candles or let signal/entry searches bridge gaps.

## Safety

Research-only. No MetaTrader5 import or connection, no order API, no runner/dashboard changes, no canonical decisions, and no automatic promotion. The live forward runner is outside this package.
