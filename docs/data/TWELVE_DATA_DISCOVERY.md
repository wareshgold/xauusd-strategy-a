# Twelve Data XAU/USD Discovery

**Status:** research-only discovery tool
**Version:** `twelvedata-discovery-v1`

## Purpose

This tool establishes whether the local environment can access Twelve Data for `XAU/USD` M1 data and records a small, reproducible discovery result before any large historical download.

It is deliberately separate from the future historical ingestion pipeline.

## Secret handling

The script reads:

```text
TWELVE_DATA_API_KEY
```

from the process environment. The value is never printed, written to a file, committed to Git, or included in a report.

Do **not** put the API key in source code, `.env` files that are committed, manifests, fixtures, notebooks, or command history.

## Run locally

From the repository root:

```powershell
python scripts/data/check_twelvedata.py
```

Optional sample size:

```powershell
python scripts/data/check_twelvedata.py --sample-size 10
```

The default run makes two small requests:

1. `/earliest_timestamp` for `XAU/USD`, `1min`, UTC.
2. `/time_series` for a small UTC M1 sample.

## What it checks

The report includes:

- API key availability without revealing its value;
- HTTP/API success;
- provider symbol and asset metadata;
- earliest available timestamp when returned by the endpoint;
- UTC sample timestamps;
- sample row count;
- chronological ordering after local diagnostic normalization;
- non-1-minute intervals inside the sample;
- basic OHLC consistency (`low <= open/close <= high`).

## Important limitations

A successful discovery result does **not** establish that the historical dataset is suitable for backtesting.

It does not yet prove:

- complete historical coverage;
- absence of gaps across long periods;
- absence of duplicate timestamps;
- feed continuity around market closures;
- broker/feed equivalence;
- correct handling of DST/session boundaries;
- API-credit feasibility for the full research period;
- reproducibility of a historical snapshot.

Those are explicit follow-up data-quality gates.

## Project policy

For SP2L research, the historical dataset must have documented provenance, retrieval parameters, timezone, coverage, row counts, quality checks, and a content checksum. Raw source data should remain local or in appropriate external storage; GitHub should contain the code, manifests, schemas, fixtures, and research records needed to reproduce the dataset.
