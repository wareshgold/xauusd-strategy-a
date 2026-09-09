# Twelve Data XAU/USD Historical Coverage Probe

**Branch:** `research/twelvedata-discovery-v1`

**Status:** discovery tooling added; no claim of complete historical coverage.

## Purpose

Establish the behaviour of the Twelve Data `time_series` endpoint for XAU/USD M1 before any bulk historical acquisition. The probe is intentionally low-credit and is not a backtest downloader.

## Current known evidence

The preceding discovery check successfully established:

- symbol: `XAU/USD`
- interval: `1min`
- timezone: `UTC`
- sample OHLC validation: 0 invalid rows
- sample interval validation: 0 non-1-minute intervals
- provider-reported earliest timestamp: `2020-04-06 06:40:00` UTC

The earliest timestamp is an endpoint response and must not yet be interpreted as proof that every minute from that date to the present is available.

## Probe

Run:

```powershell
python scripts/data/historical_coverage.py
```

The script performs two deliberately limited requests:

1. An explicit old-date probe to observe how the provider responds to a historical date outside the known range.
2. One `outputsize=5000` M1 page to inspect the returned page boundaries, continuity, and OHLC validity.

The API key is read from `TWELVE_DATA_API_KEY`; the value is never printed or written to repository files.

## What this does NOT establish

This probe does not establish:

- complete 2020-present M1 coverage;
- absence of gaps outside the returned page;
- exact maximum pagination depth;
- exact historical credit cost for the eventual dataset;
- broker/feed equivalence;
- suitability as the final source of truth.

Those questions require a separate, resumable acquisition experiment with explicit credit accounting and provenance.

## Next gate

If the probe passes, the next task is to design a **credit-bounded historical acquisition experiment**. It should measure request cost, page overlap/continuity, duplicate handling, and checkpoint/resume semantics before attempting full historical extraction.
