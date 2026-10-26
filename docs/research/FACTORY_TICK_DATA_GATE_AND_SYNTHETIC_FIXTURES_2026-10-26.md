# Factory Tick Data Gate and Synthetic Fixture Contract — 2026-10-26

## Purpose and status

This document records a research-only decision for the XAUUSD.ecn tick dataset and defines the next deterministic synthetic-fixture gate. It does not make SP2L geometry canonical, authorize live trading, or claim a backtest result.

**Status:** conditional data acceptance for engineering fixtures and replay-adapter development; strategy replay remains blocked until execution semantics are frozen and verified.

## Dataset identity

- File: xauusd-ecn-ticks-20260821_20260919.csv.gz
- SHA-256: 412a535b8d5f0413f329e5fde8a1f851591ee83c95fc25af38b287d6170a1347
- Size: 111,124,585 bytes
- Rows: 10,817,858
- Declared UTC interval: [2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z)
- Observed first/last ticks: 2026-08-21T01:00:05.864Z / 2026-09-18T23:57:56.609Z
- Source: MT5 terminal API, server OtetGroup-MT5, symbol XAUUSD.ecn
- Independent read-only audit: SHA/row count matched; zero backward timestamp steps; zero invalid numeric/time rows; zero missing/nonpositive Bid/Ask rows; zero crossed quotes.

The dataset is not stored in this repository. This record documents user-provided audit output and does not independently re-read the local artifact.

## Duplicate timestamp disposition

The audit found:

- 12,389 adjacent equal-timestamp steps
- 7,429 timestamp groups containing duplicates
- 19,818 rows inside those groups
- 6,895 duplicate groups with differing Bid/Ask quotes
- 534 duplicate groups with identical Bid/Ask quotes
- Maximum group size: 15 rows

**Required handling:** preserve original file row order and assign a monotonically increasing source-row index. Do not sort by timestamp, deduplicate, collapse to first/last quote, or infer sub-millisecond order. The row order is a reproducible processing order, not proof of true sub-millisecond event chronology.

If execution outcomes depend on the order of different quotes sharing a timestamp, report that outcome as order-sensitive/ambiguous and quantify sensitivity. A candidate must not choose whichever order improves results.

## Gap review and 2026-09-07 treatment

The audit found 20 positive adjacent-tick gaps over 60 seconds. Four approximately 48-hour gaps align with weekends; most approximately one-hour gaps align with the daily session boundary seen in this feed.

The 2026-09-07 gap is:

- Last observed tick before gap: 2026-09-07T21:36:11.547Z
- First observed tick after gap: 2026-09-08T01:00:07.172Z
- Duration: 12,235.625 seconds (about 3 h 24 min)

For this research pass, **treat 2026-09-07 as a provisional scheduled-holiday/shortened-session closure assumption**, consistent with the US Labor Day calendar context. This is an explicit research-calendar assumption requested for the current gate, not verified historical evidence from OtetGroup for this exact symbol and date.

Consequences:

1. Do not count this gap alone as proof of a missing-feed defect for the current engineering-fixture gate.
2. Keep the assumption visible in all data manifests and reports.
3. Do not silently interpolate ticks or synthesize prices across the gap.
4. If a future result materially depends on positions or triggers spanning the gap, mark it session-calendar-sensitive until the broker's historical schedule is independently verified.
5. Other gap classifications remain diagnostic; a gap threshold alone is not a canonical market-hours rule.

## Synthetic fixture contract

Fixtures must be deterministic and must not depend on live MT5, broker connectivity, or account state.

1. **Source order:** equal timestamps with different quotes retain input row order and stable source-row IDs.
2. **Duplicate sensitivity:** a constructed case where two same-timestamp quotes lead to different hypothetical outcomes must be flagged order-sensitive; the harness must not silently pick a preferred ordering.
3. **Trailing source bar:** only the configured completed M1 bar may be used; a forming bar must not be read as completed. The exact RR2/TRAIL4 rule must be asserted against the selected source revision before executable tests encode it.
4. **SL/TP collision:** if the tick sequence explicitly orders touches, use that sequence; if only OHLC or same-timestamp evidence cannot resolve ordering, emit an ambiguity rather than inventing intrabar order.
5. **Stop/freeze constraints:** a rejected/invalid SL modification must not be recorded as a successful modification.
6. **Pending-limit lifecycle:** test placement, expiry, cancellation, and market-crossing cases only after exact source behavior and broker constraints are transcribed into a frozen adapter contract.
7. **Repeatability:** identical fixture bytes, contract fingerprint, and engine revision must yield identical event-ledger bytes and summary metrics.

## Gate decision

- **Data integrity:** preliminary pass for the audited file identity and quoted numeric checks.
- **Chronological order:** nondecreasing timestamps; duplicate ordering remains an explicit risk.
- **Coverage:** conditional for engineering and fixtures; the 2026-09-07 gap is provisionally classified as a holiday/shortened-session closure assumption, not broker-confirmed fact.
- **Strategy replay:** blocked until the exact RR2/TRAIL4 source revision, entry/exit behavior, fill semantics, trailing units, and broker constraints are frozen in a source-linked adapter contract.
- **Canonical SP2L geometry:** unresolved items remain unresolved; no rule is promoted by this document.
- **Production/live decisions:** out of scope and not authorized.

## Next implementation step

Implement the synthetic fixtures and their tests on this research branch, with each expected result tied to source-confirmed behavior. Any unresolved behavior must have a fixture that expects an explicit UNRESOLVED/AMBIGUOUS result rather than a guessed fill or trade outcome.
