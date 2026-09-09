# SP2L G44 — Real XAUUSD Sample Audit

Date: 2026-09-09
Gate: G44 — real-data sample quality audit
Status: PASS (structural data quality only)

## Dataset identity

- Provider: Twelve Data
- Instrument: XAU/USD
- Interval: 1min
- Rows: 5,000
- Input artifact: `data/raw/time_series.json` (local only; ignored by Git)
- Raw SHA-256: `3060db7473b5f43610b265f43c6c827052c89334420dbaf5163e7925f9d94979`
- Normalized SHA-256: `dbcf0b681b79e925cb320d7164dac0980e97eeb338ae1996ab4e852e35622f5f`

## Time handling

The downloaded JSON did not contain timezone metadata. Therefore timezone was not inferred from the file.

For this audit, `Australia/Sydney` was supplied explicitly as the source-timezone provenance parameter and timestamps were normalized to UTC using Python `zoneinfo`.

- First normalized timestamp: `2026-09-05T21:17:00+00:00`
- Last normalized timestamp: `2026-09-09T08:36:00+00:00`

The Windows environment required the IANA timezone package `tzdata`; the project now pins it in `requirements-research.txt`.

## Structural quality results

| Check | Result |
|---|---:|
| Row count | 5,000 |
| Duplicate timestamps | 0 |
| Non-monotonic pairs after normalization | 0 |
| Cadence mode | 60 seconds |
| Cadence anomalies | 0 |
| Missing bars | 0 |
| Invalid OHLC rows | 0 |
| Overall audit | PASS |

## Scope boundary

This PASS establishes only that this sample is structurally clean under the explicitly supplied timezone provenance.

It does **not** establish:

- Strategy A / SP2L geometry validity;
- P-Gap geometry;
- Entry/SL/Leg2 geometry;
- AB=CD anchor or tolerance;
- trigger semantics;
- profitability or statistical edge;
- suitability of this feed over another XAUUSD feed.

No BUY/SELL detector or Strategy A optimization is authorized by this audit.

## Reproducibility

The raw artifact remains local and is excluded from Git. Re-running the local audit against the same raw bytes with the same explicit timezone parameter must reproduce the raw and normalized fingerprints above.

## Gate decision

**G44: PASS for real-sample structural quality.**

Frozen Geometry remains blocked. The next work may proceed on strategy-neutral dataset reproducibility, acquisition provenance, feed comparison, and execution infrastructure, while canonical Strategy A detection remains locked behind source-geometry resolution.
