# SP2L Research Data Provenance Contract — 2026-09-17

## Purpose

Define the minimum provenance record required for any future historical dataset used in SP2L stability, untouched validation, robustness, or holdout research.

This is a data-audit contract. It does not define or modify Strategy A geometry.

## Required dataset identity

Every research dataset or snapshot must record:

- provider/data source;
- terminal or server identity when applicable;
- symbol identity;
- timeframe;
- requested start/end or snapshot-end definition;
- retrieval timestamp in UTC;
- requested bar count;
- actual first and last bar timestamps in UTC;
- actual bar count;
- timezone normalization rule;
- missing/discontinuous-bar findings;
- file/content SHA-256 when a materialized file is used;
- code/runner revision used to acquire or transform the data;
- configuration identifier for the downstream research run.

## Acquisition rule

Historical coverage expansion must use the same research configuration already frozen for the relevant comparison. Dataset expansion must not be used as an opportunity to optimize Strategy A parameters.

## Integrity rule

A dataset used for a published research result must be reproducible from its provenance record or accompanied by the materialized artifact and its cryptographic hash.

If the exact underlying bars cannot be verified, the result must be treated as unverifiable for that dataset rather than silently substituted with another source.

## Gap rule

Missing or discontinuous bars must be measured and reported. No synthetic candle may be inserted into the research dataset unless a separate fixture explicitly tests a transformation that is itself source-authorized and documented.

## Snapshot rule

For rolling/non-overlap stability research, each snapshot must preserve:

1. the exact snapshot-end rule;
2. the exact requested bar count/window rule;
3. the exact source and symbol;
4. the exact strategy configuration;
5. the exact code revision.

Changing any of these creates a different research condition and must not be silently mixed with prior results.

## Promotion boundary

Provenance completeness does not establish strategy validity. It only establishes traceability of the data used for a research result.

Source-resolution, Frozen Geometry, untouched validation, robustness/stability, and fresh-holdout gates remain independent.


## Versioned MT5 acquisition manifest

The research-only script `scripts/mt5_acquire_research_evidence_v1.py` emits the
versioned manifest schema identified by:

- `schema.id = sp2l.mt5-research-evidence`
- `schema.version = 1.0.0`

In this schema, `timestamp_discontinuities` records observed adjacent-row
timestamp intervals. Its `unclassified_gap` entries are positive intervals
longer than one minute; they do not assert that trading bars were missing.
`ordering_anomalies` records duplicate or reverse timestamps, while
`unclassified_gaps` is the corresponding filtered list. The
`chronological` flag describes strict timestamp ordering only; it does not
certify coverage completeness.

The audit statuses have distinct meanings:

- `AUDITED_PASS`: valid rows, strictly increasing timestamps, and no observed
  interval longer than one minute.
- `AUDITED_UNCLASSIFIED_COVERAGE`: valid rows and strictly increasing
  timestamps, but one or more positive intervals longer than one minute whose
  market-calendar meaning has not been established.
- `AUDITED_FAIL`: invalid rows, duplicate timestamps, or reverse timestamp
  order.

This schema is **not** the legacy template structure above. In particular,
legacy `observed.gap_count` / `observed.gap_ranges` fields are not aliases
for `discontinuity_count` / `timestamp_discontinuities`. Consumers must
select the schema by its explicit `schema.id` and `schema.version`; any
cross-schema conversion requires a separately specified and tested adapter.
No existing manifest is migrated or rewritten by this change.

### Requested minute-slot count is not expected market-bar coverage

For this manifest schema, `requested_bar_count` is a legacy field name whose
value is calculated as the inclusive number of calendar-minute slots between
the normalized requested start and end timestamps. It is request-window
arithmetic only. It is **not** an expected count of tradable M1 bars, does not
account for weekends, holidays, broker sessions, or market closures, and must
not be used to infer missing bars or coverage completeness. Compare
`actual_bar_count` with this value only as a descriptive difference; classify
coverage using observed timestamps and an independently established,
source-authorized market calendar, if one becomes available. The field is
retained for schema-v1 compatibility; consumers must not interpret its name
literally as an expected trading-bar count.


## Research acceptance gate for MT5 evidence manifest v1

The standalone validator `scripts/validate_mt5_research_manifest_v1.py`
implements a fail-closed acceptance check for the exact
`sp2l.mt5-research-evidence@1.0.0` schema. It requires the caller to supply
both the manifest and its raw CSV; it verifies the raw SHA-256, CSV columns,
row count, first/last timestamps, strict timestamp order, and recomputes
adjacent timestamp discontinuities from the raw rows before comparing them
with the manifest.

The validator emits one of three outcomes:

- `ACCEPTED`: the raw artifact and manifest pass the structural/integrity
  checks and the acquisition audit is `AUDITED_PASS`. This permits a
  research replay only; it does not prove that the requested interval is
  complete under the broker's historical trading sessions.
- `ACCEPTED_WITH_UNCLASSIFIED_COVERAGE`: raw artifact identity and internal
  consistency pass, but one or more observed positive timestamp intervals
  remain unclassified. This outcome is **not eligible for research replay**.
- `REJECTED`: unsupported schema, failed acquisition audit, missing or
  mismatched artifact, inconsistent counts/timestamps, invalid rows, or
  inconsistent discontinuity evidence.

The output always sets `confirmatory_validation_eligible=false` and
`production_eligible=false`. Those decisions require independent gates and
cannot be granted by a manifest-only validator. A return code of zero for an
unclassified acquisition status from the acquisition script is not an
acceptance decision; consumers must use this validator's explicit
`research_replay_eligible` field.

This validator is intentionally separate from the legacy M1 acquisition
scripts and the MT5 matrix `gap_intervals` quality gate. It does not adapt,
rewrite, or reinterpret those schemas. It also does not change any backtest
runner or make existing July–September datasets eligible.
