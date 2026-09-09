# Twelve Data XAU/USD Historical Acquisition Pilot

**Status:** ready to execute locally; intentionally bounded.

## Objective

Exercise the actual raw-data acquisition path on a small explicit UTC window before any full historical download. The pilot tests pagination, boundary de-duplication, OHLC validation, minute continuity, raw preservation, provenance, and checkpoint/resume mechanics.

## Default window

`2026-09-04 00:00:00 UTC` through `2026-09-05 00:00:00 UTC` (24 hours, inclusive).

This is deliberately small. It is not intended to establish full historical coverage or strategy performance.

## Command

```powershell
git pull --ff-only origin research/twelvedata-discovery-v1
python scripts/data/acquisition_pilot.py
```

Optional explicit window:

```powershell
python scripts/data/acquisition_pilot.py --start "2026-09-04 00:00:00" --end "2026-09-05 00:00:00"
```

The default request budget is 5. No more than the configured budget is attempted.

## Artifacts

The pilot writes under:

`data/raw/twelvedata/pilot/`

For a successful run it creates:

- raw CSV containing only `datetime,open,high,low,close`;
- JSON manifest containing request-level provenance, validation results, and the CSV SHA-256;
- a temporary checkpoint that is removed after successful completion.

Existing artifacts are protected by default. `--force` is required to intentionally replace a pilot artifact.

## Deterministic data handling

- All timestamps are treated as UTC.
- Candles are keyed by exact provider `datetime`.
- Boundary duplicates are removed deterministically by timestamp.
- Provider OHLC values are preserved as returned; no resampling or strategy transformation is applied.
- A gap means adjacent sorted timestamps differ from exactly 60 seconds.
- The pilot does not fill missing candles.
- The pilot does not infer market closure rules as data gaps.

## Exit semantics

Exit code `0` requires the requested range to be fully reached with zero internal 1-minute gaps and zero invalid OHLC rows. A non-zero exit means the artifact should not be treated as a clean pilot dataset without investigation.

## Provenance boundary

This pilot is evidence about the provider/data pipeline only. It must not be used to choose or modify Strategy A geometry, P-Gap, AB=CD anchors, entry rules, stop rules, or target rules.
