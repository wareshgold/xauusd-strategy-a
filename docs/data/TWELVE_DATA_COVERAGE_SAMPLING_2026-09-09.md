# Twelve Data XAU/USD M1 Coverage Sampling

Status: **sampling probe only** — not proof of complete historical coverage.

The probe samples explicit UTC windows across the available history to detect whether the provider returns data in those periods and whether the returned windows are internally continuous and OHLC-valid.

## Results

| Requested UTC window | Rows | Returned range | Gaps | Invalid OHLC | Credits used |
|---|---:|---|---:|---:|---:|
| 2020-04-06 06:40:00 → 2020-04-06 12:00:00 | 321 | 2020-04-06 06:40:00 → 2020-04-06 12:00:00 | 0 | 0 | 1 |
| 2022-01-04 00:00:00 → 2022-01-04 06:00:00 | 361 | 2022-01-04 00:00:00 → 2022-01-04 06:00:00 | 0 | 0 | 2 |
| 2024-01-04 00:00:00 → 2024-01-04 06:00:00 | 361 | 2024-01-04 00:00:00 → 2024-01-04 06:00:00 | 0 | 0 | 3 |
| 2025-01-06 00:00:00 → 2025-01-06 06:00:00 | 361 | 2025-01-06 00:00:00 → 2025-01-06 06:00:00 | 0 | 0 | 4 |
| 2026-09-04 00:00:00 → 2026-09-04 06:00:00 | 361 | 2026-09-04 00:00:00 → 2026-09-04 06:00:00 | 0 | 0 | 5 |

## Interpretation

- Successful samples establish availability only for the sampled windows.
- A zero-gap result applies only inside each returned sample; it does not establish global continuity.
- The earliest timestamp must be treated as a provider boundary, not as evidence that every minute after it exists.
- Full historical acquisition remains a separate resumable process with manifests, checkpoints, de-duplication, and SHA-256 provenance.
- Strategy rules are intentionally absent from this probe.
