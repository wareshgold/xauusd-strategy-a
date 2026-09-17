# MT5 Session Calendar Evidence Intake v1

**Status:** READY FOR TERMINAL EVIDENCE / NOT YET POPULATED  
**Scope:** XAUUSD Strategy A / SP2L historical session-calendar resolution  
**Canonical symbol:** `XAUUSD.ecn`  
**Canonical bar timestamp basis:** UTC  
**Telegram display timezone:** `Asia/Tehran`

## 1. Objective

Create a reproducible evidence record for the terminal-side XAUUSD.ecn quote/trade session schedule before any historical missing-bar interval is classified as a session closure.

This document is an evidence container specification. It does not define a historical calendar and must not be treated as one.

## 2. Required terminal evidence

The following fields must be captured from the MQL5 session diagnostic without manual editing of the observed values:

- terminal name;
- company;
- account server;
- symbol;
- quote sessions for every weekday returned by the terminal;
- trade sessions for every weekday returned by the terminal;
- session index;
- `from` and `to` values exactly as reported;
- corresponding raw epoch values when available;
- diagnostic execution timestamp/provenance.

## 3. Normalization rules

1. Preserve the raw terminal output verbatim as source evidence.
2. Do not reinterpret session `from`/`to` values as UTC merely because bar timestamps are UTC.
3. Treat terminal session schedule values as broker/server-time schedule evidence, consistent with the MQL5 session model.
4. Preserve cross-midnight relationships; do not force `to > from` on the same nominal weekday.
5. Any UTC normalization used for an audit must be a derived representation with an explicit documented offset/evidence source.
6. Never modify canonical MT5 bar timestamps.
7. Never infer historical DST behavior from a single current schedule snapshot.
8. Never infer holiday/special sessions from the regular weekly schedule.

## 4. Historical-resolution gate

A current terminal snapshot alone is insufficient to freeze the historical calendar.

Before `MT5_SESSION_CALENDAR_CONTRACT_V2` can be considered, the evidence set must address:

- regular weekly quote schedule;
- regular weekly trade schedule;
- cross-midnight sessions;
- research-period DST/seasonal boundaries where applicable;
- holidays/special sessions affecting the research period;
- broker schedule changes, if any;
- reproducible expected-M1 availability mapping;
- independent comparison against the acquired artifact.

## 5. Gap classification during resolution

Until the above gate is satisfied, all unexplained missing intervals remain:

`UNRESOLVED_GAP`

Observable gap facts may be recorded, but labels such as `SESSION_CLOSED`, `HOLIDAY`, `DST`, or `DATA_FEED_GAP` require supporting evidence.

## 6. Evidence record template

```text
EVIDENCE_ID=
CAPTURED_AT_UTC=
TERMINAL=
COMPANY=
SERVER=
SYMBOL=XAUUSD.ecn

QUOTE_SESSIONS_RAW=
TRADE_SESSIONS_RAW=

HISTORICAL_COVERAGE=
DST_EVIDENCE=
HOLIDAY_SPECIAL_SESSION_EVIDENCE=
SCHEDULE_CHANGE_EVIDENCE=

SOURCE_PROVENANCE=
ARTIFACT_REFERENCES=

STATUS=UNRESOLVED
```

## 7. Promotion rule

This evidence record may support a future calendar contract only when the raw terminal evidence and all required historical qualifiers are preserved. Performance improvement, backtest fit, or visual alignment alone cannot promote an inferred calendar into a canonical rule.
