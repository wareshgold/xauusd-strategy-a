# SP2L 125R Golden Fixture Checkpoint — 2026-09-16

## Purpose

Freeze the persisted 125R forensic observation as a research-only golden fixture so accidental changes to its observed values or source-level classification are detected by the SP2L harness.

## Reference evidence

The forensic reconstruction records the persisted observation at `2026-08-20 20:54:00` with:

- direction: SELL
- entry: `4521.5838`
- stopLoss: `4521.61331`
- TP1: `4517.8892399999995`
- risk distance: `0.02951`
- R multiple: `125.19688241535353`
- source-level geometry status: `UNRESOLVED`

The forensic reconstruction explicitly states that the observation is implementation-forensic evidence and does not establish canonical geometry.

## Engineering change

Added:

- `research/harness/sp2l_125r_golden_fixture_v1.ts`
- `tests/sp2l-125r-golden-fixture.test.ts`

The fixture is frozen with `Object.freeze` and preserves the exact persisted numeric values plus the non-canonical source classification.

The test verifies:

1. exact value preservation;
2. absence of trading-decision fields;
3. preservation of unresolved source-level classification.

The harness TypeScript configuration and CI workflow now include this fixture/test.

## Safety boundary

This fixture does **not**:

- promote any geometry to canonical status;
- define entry, stop, trigger, P-Gap, 2X, or AB=CD rules;
- generate BUY/SELL decisions;
- alter the 125R observation;
- unlock validation, robustness, holdout, or production.

## Current gate state

- Frozen Geometry: `BLOCKED`
- Untouched Validation: `LOCKED`
- Robustness/Stability: `LOCKED`
- Fresh Holdout: `LOCKED`
- Production: `OFF`

CI is configured to execute the new integrity test. No CI result is asserted here unless independently observed.
