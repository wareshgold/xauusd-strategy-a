# G385 — XAUUSD Data Contract

**Status:** RESEARCH INFRASTRUCTURE ONLY

This contract defines what a dataset must satisfy before canonical historical DEV can begin. It does not define Strategy A geometry.

## Required record

Each raw candle must preserve:

- symbol (`XAUUSD` or the provider's explicitly documented equivalent);
- timestamp with unambiguous timezone/offset;
- open, high, low, close;
- source/provider identifier;
- timeframe;
- ingestion/refresh timestamp;
- dataset version or immutable provenance identifier.

## Canonical research representation

- Raw provider data must remain immutable.
- Derived M5 candles should be generated deterministically from the selected raw timeframe where the provider/session convention permits.
- Candle boundaries and timezone must be explicit and reproducible.
- Missing/duplicate/out-of-order candles must be detected and reported, not silently repaired.
- Provider-specific price construction must be recorded.

## Reproducibility

A DEV result must identify:

1. provider/source;
2. instrument identifier;
3. raw-data snapshot/version;
4. date range;
5. timeframe;
6. timezone/session convention;
7. transformation code/version;
8. strategy specification/version;
9. execution/fill model version;
10. costs/slippage assumptions, if any.

## Feed comparison

If more than one XAUUSD feed is used, compare at minimum:

- timestamp alignment;
- OHLC differences;
- missing/extra candles;
- high/low excursions;
- spread or executable-price differences when available.

Differences must be documented rather than silently merged.

## Gate

**Canonical DEV is NOT authorized by this document.** It requires the frozen executable Strategy A geometry first. A data pipeline can be built and quality-checked in parallel, but no historical profitability result may be labeled canonical while geometry remains blocked.
