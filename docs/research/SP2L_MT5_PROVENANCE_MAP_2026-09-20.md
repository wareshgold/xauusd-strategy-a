# SP2L MT5 Data Provenance Map — 2026-09-20

## Purpose

Per-dataset provenance for every MT5 acquisition and session-availability
artifact in this repository. Draws from the manifests under
`data/mt5-acquisition/*.manifest.json` and
`data/mt5-session-availability/*.manifest.json`, consistent with the
[data provenance contract](docs/research/SP2L_DATA_PROVENANCE_CONTRACT_2026-09-17.md).

**Reading guide** — one row answers: source, symbol, timeframe, date range,
timestamp basis, known limitations, and allowed usage.

**Timestamp basis.** All `*_utc` fields are UTC as normalized from the MT5
terminal. The MT5 candle timestamp basis itself is **not assumed UTC** by the
research process; session-calendar provenance was audited separately
(session-calendar id
`xauusd-ecn-session-current-observation-2026-09-17`, historical applicability
**UNVERIFIED**). Every timestamp-dependent result carries this as a tracked
assumption, not a fact.

**Allowed-usage tiers.** D = DIAGNOSTIC (data-characteristics only) ·
E = EVIDENCE (data characteristics under contract) · R = RESEARCH ONLY
(replica/baseline input, never canonical until gates pass).

---

## A. Monthly acquisition datasets

| Dataset (id → artifact CSV) | Range (UTC) | Bars | Gaps | SHA-256 | Audit | Allowed use |
|---|---|---|---|---|---|---|
| `xauusd-ecn-m1-2026-07` → `xauusd-ecn-m1-2026-07.csv` | 2026-07-01→07-31 | 31,483 | 257 | `482991df85c7…8e34e` | AUDITED_FAIL | D/E infill-safe? NO — heavy gaps |
| `xauusd-ecn-m1-2026-08` → `xauusd-ecn-m1-2026-08.csv` | 2026-08-01→08-31 | 28,957 | 23 | `8d9f4d9a82ff…4a87` | AUDITED_FAIL | D/E |
| `xauusd-ecn-m1-2026-09` → `xauusd-ecn-m1-2026-09.csv` | 2026-09-01→09-17 | 17,069 | 871 | `3b7212dc43f8…cc2b` | AUDITED_FAIL | D/E — gap-heavy, uneven |
| `xauusd_ecn_m1_2026-08-21_2026-09-18` → `xauusd_ecn_m1_2026-08-21_2026-09-18.csv` | 2026-08-21→09-18 | 28,815 | 20 | `9df9a0ca0333…5aa4` | research_only | R — **primary 4-week research feed** |

Notes:
- Provider is `MetaTrader5 terminal API`; terminal `Otet Group MT5 Terminal`; server `OtetGroup-MT5`; symbol `XAUUSD.ecn`; timeframe M1 — uniform across all.
- Gaps cluster at (Fri 23:57–Mon 01:00) and daily (23:58–01:00) — matches the session calendar, so they are session-boundary jumps, not data errors. `invalid_row_count: 0` on the 08-21→09-18 set; unique and chronological timestamps confirmed.
- AUDITED_FAIL means missing-bar audit ran and reported gaps — provenance is intact, but the dataset is not gap-free; treat as supply-driven availability evidence, not continuous price.

## B. Session-aware & smoke test datasets

| Dataset | Range (UTC) | Bars | Gaps | SHA-256 | Audit | Allowed use |
|---|---|---|---|---|---|---|
| `xauusd-ecn-m1-session-aware-test-2026-09-17-v2` | 09-16 22:00→09-17 02:00 | 181 | 0 | `9be20f3533c9…e228e` | AUDITED_PASS | D — session-boundary probe, tight window |
| `xauusd-ecn-m1-session-aware-test-2026-09-17` | same | 181 | 0 | `9be20f3533c9…e228e` | AUDITED_FAIL | D — superseded by -v2, same bytes |
| `xauusd-ecn-m1-smoke-2026-09-17` | 09-16 00:00→01:00 | 1 (of 61 req) | 0 | `f07d0264f3cc…b471` | AUDITED_PASS | D — connectivity smoke only; not a price series |
| `xauusd-ecn-m1-smoke-strict-2026-09-17` | same | 1 | 0 | `f07d0264f3cc…b471` | AUDITED_FAIL | D — strict-mode check; not a price series |

Notes:
- The two `session-aware-test` artifacts share byte-identical content; `-v2` is the passing audit, use it.
- The smoke artifacts return only 1 bar of a requested 61 — they validate the acquisition path, not market data.

## C. Session-availability & forensic datasets (`data/mt5-session-availability/`)

| Dataset | Range (UTC) | Bars | Audit status | Allowed use |
|---|---|---|---|---|
| `xauusd_ecn_m1_availability_2026-09-07_2026-09-14` | 09-07→09-14 | 6,753 | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — availability evidence |
| `xauusd_ecn_m1_availability_contiguous_2026-07-06_2026-09-14` | 07-06→09-14 | — | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — contiguity evidence |
| `xauusd_ecn_m1_availability_june_to_july_2026` | 06→07 2026 | — | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — availability evidence |
| `xauusd_ecn_m1_availability_matrix_2026Q1_Q3` | Q1–Q3 2026 | — | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — availability matrix |
| `xauusd_ecn_m1_availability_seasonal_dst_2026_may_oct` | May→Oct 2026 | — | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — DST-season evidence |
| `xauusd_ecn_m1_forensic_2026-06-19` | 06-19 01:00→06-22 04:00 | 1,322 | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — forensic probe |
| `xauusd_ecn_m1_forensic_2026-07-03` | 07-03 01:00→07-06 04:00 | 1,322 | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — forensic probe |
| `xauusd_ecn_m1_forensic_2026-09-07` | 09-07 01:00→09-08 04:00 | 1,418 | ACQUIRED_WITHOUT_GAP_INTERPRETATION | D — forensic probe |

Notes:
- Audit status `ACQUIRED_WITHOUT_GAP_INTERPRETATION` means bars were pulled without a gap-classification pass; do not attribute gap semantics to these.
- These support the session-calendar research (MT5 timestamp/session basis), they are **not** strategy inputs.

## D. Non-MT5 comparison feed (research-only)

| Dataset | Source | Note |
|---|---|---|
| `data/historical/xauusd-1min.json` / `xauusd-5min.json` | TwelveData XAU/USD | Research comparison feed only. M1 is intended raw source of truth; M5 derivable locally. |
| `artifacts/mt5_xauusd_m1_10000.json` / `_fixed_10000.json` | OTET MT5 export | Prior 10k-candle replays (49 signals / 46 decisive). Comparison baseline. |

## E. Standing constraints

1. **No synthetic candles** may be inserted into any research dataset except as a separately authorized, documented fixture.
2. **No gap filling** to manufacture a continuous series — gaps are reported as measured.
3. Provenance completeness ≠ strategy validity. It only establishes traceability ([contract](docs/research/SP2L_DATA_PROVENANCE_CONTRACT_2026-09-17.md)).
4. Datasets may power **replica / stability / holdout** work only under the frozen research configuration; expanding coverage is not an opportunity to tune parameters.
5. The Fresh Holdout boundary **`2026-09-19 00:00 UTC`** is untouched (artifact `SP2L_fresh_holdout_2026-09-19.json` = `HOLDOUT_DATA_UNAVAILABLE`).

## F. Related

- [Research Artifact Index (this set)](docs/research/SP2L_RESEARCH_ARTIFACT_INDEX_2026-09-20.md)
- [Data Provenance Contract](docs/research/SP2L_DATA_PROVENANCE_CONTRACT_2026-09-17.md)
- MT5 session metadata evidence: `docs/research/SP2L_MT5_SESSION_METADATA_EVIDENCE_2026-09-17.md`
- Session calendar runbook: `research/mt5/README_SESSION_CALENDAR.md`