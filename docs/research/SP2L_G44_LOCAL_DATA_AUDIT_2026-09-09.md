# SP2L G44 — Local Data Audit

Date: 2026-09-09

## Objective

Create a reproducible local audit for raw Twelve Data-shaped XAU/USD OHLC JSON. The audit is strategy-neutral and must not detect, optimize, or validate Strategy A setups.

## Real sample

Input: `time_series.json` supplied for G44.

Observed source metadata:
- Symbol: XAU/USD
- Interval: 1min
- OHLC fields present
- Sample contains 5,000 values
- Provider payload is newest-first and is normalized locally to ascending UTC for analysis

The uploaded sample was independently inspected before this local-tool contract was added. The audit contract now makes those checks reproducible from a local file rather than relying on manual inspection.

## Local command

```bash
python -m research.engine.local_data_audit path/to/time_series.json --output-dir reports
```

The command writes `reports/quality_audit.json` and prints a concise PASS/WARN/BLOCKED summary.

## Deterministic checks

1. JSON parsing and required `meta.symbol` / `meta.interval`.
2. Explicit timezone requirement for naive timestamps; no guessed timezone.
3. UTC normalization.
4. Duplicate timestamp detection.
5. Chronological ordering after normalization.
6. OHLC integrity: `low <= open <= high` and `low <= close <= high`.
7. Expected cadence derived from the declared interval.
8. Cadence anomalies and implied missing-bar count are reported; bars are never fabricated.
9. Raw input SHA-256.
10. Normalized candle SHA-256.

## Status semantics

- `PASS`: no blocking integrity issue and no cadence anomaly.
- `WARN`: integrity is usable but cadence anomalies/missing bars are present.
- `BLOCKED`: duplicate timestamps, non-monotonic timestamps, invalid OHLC, malformed rows, or other blocking parse/integrity failure.

## Important boundary

This tool does not contain Strategy A geometry, P-Gap logic, entry/SL inference, AB=CD anchors, triggers, TP projection, or BUY/SELL generation. A clean data audit is not evidence of Strategy A profitability or source-geometry resolution.

## Reproducibility

The local audit is intended to become the single reusable mechanism for local sample checks and later CI execution. The raw sample remains immutable evidence; normalized data is a derived artifact identified by its own SHA-256 fingerprint.

## Gate disposition

G44 local audit tooling: **PASS** as infrastructure.

G44 Strategy A validation: **NOT AUTHORIZED**.

Frozen Geometry remains blocked pending authoritative source resolution of B1–B6.
