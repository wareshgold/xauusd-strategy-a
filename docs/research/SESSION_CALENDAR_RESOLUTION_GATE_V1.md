# Session Calendar Resolution Gate v1

**Status:** ACTIVE RESEARCH GATE  
**Scope:** XAUUSD.ecn / M1 / SP2L research acquisition and audit

## Objective

Resolve historical session availability without modifying canonical MT5 bar timestamps.

## Evidence hierarchy

1. Official MetaQuotes/MQL5 session API semantics.
2. Actual terminal-side `XAUUSD.ecn` session schedule observation.
3. Reproducible historical terminal observations at representative boundaries.
4. Dataset gap audit as supporting evidence only.
5. Price-pattern inference is not authoritative for calendar reconstruction.

## Required evidence before Calendar v2 can be frozen

- current quote and trade schedules for every weekday;
- explicit treatment of cross-midnight sessions;
- historical observations spanning at least one ordinary weekday boundary and one weekly boundary;
- evidence for any observed broker schedule/DST transition in the research interval;
- special/holiday sessions identified where applicable;
- reproducible mapping from schedule semantics to expected M1 availability;
- independent audit showing that classified session closures explain the relevant gaps without unexplained timestamp shifts.

## Classification policy

Until all required evidence is satisfied:

- missing M1 bar = `UNRESOLVED_GAP`;
- timestamp jump = `UNRESOLVED_GAP`;
- current-day truncation = `CURRENT_DAY_TRUNCATION` only when directly established as retrieval truncation;
- no gap may be converted into a canonical session closure from price data alone.

## Time handling

- MT5 canonical bar timestamps remain UTC under `MT5_TIMESTAMP_CONTRACT_V1`.
- Session schedule values observed from MQL5 are broker/server-time semantics and must be normalized for comparison without changing bar timestamps.
- Telegram signal display remains `Asia/Tehran` under `TELEGRAM_SIGNAL_TIME_CONTRACT_V1`.
- No broker/server offset is allowed to be applied to MT5 bar timestamps.

## Historical resolution procedure

1. Capture terminal schedule snapshot with provenance.
2. Capture raw epoch observations around representative historical boundaries.
3. Normalize session intervals to a comparison timeline while retaining source representation.
4. Compare expected availability with the immutable acquired dataset.
5. Classify each gap as explained, special-session, retrieval-truncation, or unresolved.
6. Preserve all unresolved cases explicitly.
7. Freeze Calendar v2 only if source evidence and audit agree.

## Non-goals

This gate does not define SP2L geometry, P-Gap, AB=CD anchors/tolerance, trigger semantics, execution/fill semantics, or production BUY/SELL decisions.
