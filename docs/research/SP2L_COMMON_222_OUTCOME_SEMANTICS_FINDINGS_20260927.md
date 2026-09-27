# SP2L Common 222 Outcome Semantics Findings — 2026-09-27

## Status

Research-only forensic checkpoint. No canonical rule, geometry, fill semantics, or execution semantics are promoted.

## Observed run

The common-signal outcome forensic was run against:

- baseline: `SP2L_MT5_SOURCE_BASELINE_V2_20260927T085954Z.json`
- reference: `SP2L_STRATEGY_A_V2_MT5_20260927T101344Z.json`
- population reconciliation: `SP2L_V2_222_VS_227_POPULATION_RECONCILIATION_20260927.json`

Observed output:

- common signals: 222
- outcome semantic differences: 204
- reference no-trade: 18
- reported baseline R over common rows: +27R
- reported reference R over common rows: +50R
- reported common-row delta: +23R

## Important audit warning

The current forensic implementation is not yet sufficient for a final parity conclusion.

The reference runner's persisted trade schema does not establish a field named `activation_time` in the documented `trades_detail` contract. Therefore the reported 165 `FILL_TIME` differences cannot yet be interpreted as real fill differences.

There is also an aggregate consistency check that must be resolved before interpreting the +23R common-row delta. The complete reference report is +50R, while the collision forensic separately matched +1R for the five baseline-only rows against their reference occupants. The expected arithmetic relationship between common and collision populations therefore needs an explicit reconciliation of trade fingerprints and membership.

## Next forensic requirement

Harden the common-outcome comparator before drawing conclusions:

1. inspect the exact persisted reference trade fields;
2. define the reference fill/activation timestamp from an actually persisted field;
3. verify one-to-one fingerprint membership for all reference trades;
4. partition reference trades into common-fingerprint and collision-occupant populations;
5. reconcile their R sums to the reference report total;
6. only then classify genuine fill/exit/R differences.

Until these checks pass, the +23R figure is a diagnostic observation, not an explanation of the +22R total performance gap.

Search token: SP2L_COMMON_222_OUTCOME_SEMANTICS_FINDINGS_20260927
