# DEV dataset audit — 2026-10-10

## Decision status

**PROVISIONAL — source parity is not exact.** This record captures a read-only comparison of the local DEV candidate against the independent MT5 reference. It does not certify Strategy A geometry, execution semantics, or tick-level parity. Neither source file was modified.

## Frozen comparison window

- Role: `DEVELOPMENT`
- Interval: `[2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z)`
- Candidate: `data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv`
- Independent reference: MT5 Common Files `sp2l_runtime_m1_20250925_20260925.csv`
- Candidate rows in interval: 28,815
- Reference rows in interval: 28,815
- Shared timestamps: 28,815
- Candidate-only timestamps: 0
- Reference-only timestamps: 0
- First available candle: `2026-08-21T01:00:00Z`
- Last available candle: `2026-09-18T23:57:00Z`

The requested interval begins at 00:00 UTC, but the first available bar in both files is 01:00 UTC. This record makes no claim that a 00:00 candle exists.

## Field comparison

| Field | Mismatches | Result |
|---|---:|---|
| Open | 0 | PASS |
| High | 0 | PASS |
| Low | 0 | PASS |
| Close | 0 | PASS |
| Tick volume | 0 | PASS |
| Real volume | 0 | PASS |
| Spread | 3 | REVIEW REQUIRED |

Spread mismatches:

| Timestamp (UTC) | Candidate | Reference |
|---|---:|---:|
| 2026-09-02T01:09:00Z | 23 | 24 |
| 2026-09-04T02:46:00Z | 16 | 17 |
| 2026-09-07T20:41:00Z | 13 | 14 |

The audit status is therefore **not exact parity**. Do not silently overwrite either source, normalize away these differences, or select a spread source based on backtest performance. Resolve spread provenance/semantics and freeze a common cost/execution contract before any 1v1 comparison that depends on spread.

## SHA-256 fingerprints

- Candidate raw-file SHA-256: `09FB33790E46539DF7EA072D0796A84F1136B242E32E28B365CCD2C604DD8CAE`
- Candidate normalized-row SHA-256: `35A9164A57F5E2C73EB744585FE8435DC269ABA0B4BD6C4C4901B0E665EA04A4`
- Reference normalized-row SHA-256: `39359F6FA709D328B709FB2A44103D5A73CEA7D9D79FD462F763EF24CE587582`

Normalized fingerprint procedure: select rows whose epoch is inside the half-open DEV interval; sort by epoch; serialize epoch followed by Open, High, Low, Close, Tick Volume, Spread, and Real Volume separated by `|`, with one newline per row; normalize price decimals with Python `Decimal.normalize()`/fixed-point formatting and serialize volume/spread fields as integers; SHA-256 the resulting UTF-8 bytes. The raw-file hash is separately calculated over the exact candidate file bytes.

## Guardrails and next gate

- Keep the candidate and independent reference unchanged.
- Do not use Fresh Holdout for candidate tuning. This audit does not report Holdout performance.
- M1 parity does not establish tick Bid/Ask or forming-candle path parity.
- Alireza's forming-M1 implementation must not be represented as exact replay from completed M1 OHLC.
- No 1v1 winner, canonical promotion, production eligibility, or BUY/SELL authority is granted by this audit.
- Before adapter implementation and real 1v1, acquire/review a research-only Tick Bid/Ask dataset for the DEV interval, or separately approve and label an approximation for both participants.
- The independent RR2/TRAIL4 forward runner is outside this workflow and must remain untouched.
