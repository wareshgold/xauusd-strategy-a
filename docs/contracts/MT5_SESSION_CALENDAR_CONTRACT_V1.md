# MT5 Session Calendar Contract v1

**Status:** FROZEN CONTRACT BOUNDARY / CALENDAR DATA UNRESOLVED  
**Scope:** XAUUSD Strategy A / SP2L research acquisition and dataset-audit layer  
**Canonical symbol:** `XAUUSD.ecn`  
**Canonical timeframe:** M1  
**Observed server:** `OtetGroup-MT5`

## 1. Purpose

This document freezes the project's rules for how session/calendar evidence is handled. It deliberately does **not** freeze a historical XAUUSD.ecn session schedule yet.

The objective is to prevent missing-bar observations from being silently converted into trading-session assumptions.

Source meaning outranks empirical convenience or backtest performance.

## 2. Source-confirmed session model

Official MQL5 documentation states that the terminal stores a per-symbol schedule of quoting and trading sessions. It also states that session opening/closing hours are translated by the terminal from the exchange local timezone into broker/server time.

The MQL5 APIs `SymbolInfoSessionQuote` and `SymbolInfoSessionTrade` expose these intraday session windows by symbol and weekday. The returned `from`/`to` values are intraday schedule values; their date component is normally ignored, but the documentation warns that an end time may carry an extra day when a session crosses midnight.

Sources:

- https://www.mql5.com/en/book/automation/symbols/symbols_sessions
- https://www.mql5.com/en/docs/marketinformation/symbolinfosessionquote
- https://www.mql5.com/en/docs/marketinformation/symbolinfosessiontrade

## 3. Frozen interpretation boundary

The following are now frozen as project policy:

1. **Timestamp semantics and session semantics are separate contracts.**
2. A missing M1 timestamp is **not** automatically a session closure.
3. A timestamp jump is **not** automatically a session boundary.
4. Current-day truncation is **not** historical calendar evidence.
5. No session schedule may be inferred solely from the four-week CSV's missing timestamps.
6. No broker/server offset may be invented to make a gap pattern fit an expected session.
7. Any historical session calendar used by validation must have an explicit evidence record and provenance.
8. Session boundaries must preserve cross-midnight behavior rather than assuming `end > start` on the same nominal day.

## 4. What remains unresolved

The following remain **UNRESOLVED** and are not canonical Strategy A rules:

- the historically correct XAUUSD.ecn quoting schedule for the full research period;
- the historically correct XAUUSD.ecn trading schedule for the full research period;
- whether the broker changed session schedules during the research period;
- DST/seasonal changes in the broker/server session schedule;
- holiday/special-session exceptions;
- whether every observed historical gap in the acquired M1 artifact is explained by session availability;
- whether any data-feed or terminal-history gaps are mixed with true session closures.

## 5. Canonical gap classification policy

Until historical calendar resolution is complete, every missing interval must be classified as:

`UNRESOLVED_GAP`

unless independently proven otherwise.

The audit layer may additionally record observable facts such as:

- previous returned timestamp;
- next returned timestamp;
- gap duration;
- retrieval timestamp;
- acquisition method;
- terminal/server;
- symbol/timeframe;
- whether the interval includes the current retrieval horizon.

It must not label the gap `SESSION_CLOSED`, `HOLIDAY`, `DST`, or `DATA_FEED_GAP` without supporting evidence.

## 6. Required source-resolution path

Before the historical calendar can be frozen, the project must obtain and preserve:

1. the actual terminal-side session schedule for `XAUUSD.ecn`;
2. evidence covering all relevant weekdays;
3. evidence covering the research period's seasonal/DST boundaries where applicable;
4. evidence for any observed special/holiday sessions;
5. a reproducible mapping from session schedule to expected M1 bar availability;
6. an independent audit showing that observed gaps are explained consistently.

The preferred authoritative terminal-side evidence is the MQL5 session API / terminal specification, not an inferred schedule from price data.

## 7. Acquisition requirements

Canonical acquisition artifacts must preserve:

- provider;
- terminal name/path where available;
- server;
- symbol;
- timeframe;
- requested interval;
- retrieval timestamp;
- acquisition method;
- timestamp contract version;
- session-calendar contract version;
- audit status;
- artifact hash where applicable.

No acquisition script may silently fill, interpolate, shift, or delete missing bars to satisfy a calendar assumption.

## 8. Relation to the frozen timestamp contract

`MT5_TIMESTAMP_CONTRACT_V1` remains authoritative for timestamp interpretation:

`MT5 bar timestamp basis = UTC; no manual timestamp shift.`

Session schedule values may be represented in broker/server-time terms when sourced from terminal session APIs, but that does **not** authorize changing the canonical UTC bar timestamps.

Conceptually:

```text
raw MT5 bar timestamp
        -> UTC canonical timestamp

terminal session schedule
        -> independent session evidence
        -> expected availability model

Do not merge these into one timezone-correction rule.
```

## 9. Evidence status

### Source-confirmed

- Per-symbol quote/trade session schedules exist in the terminal model.
- Quote and trade sessions are distinct concepts.
- Session times are represented relative to broker/server time in the terminal's session schedule model.
- Session APIs expose weekday/session-index windows.
- Cross-midnight sessions require preserving the date/day relationship.

### Environment evidence already available

The current four-week acquisition audit demonstrates that returned timestamps are chronological and unique, but the audit is `AUDITED_FAIL` because expected active-bar counts were based on a calendar that was explicitly marked `CURRENT_OBSERVATION_NOT_HISTORICALLY_VERIFIED`.

That audit result is therefore **not** evidence of a particular historical session calendar.

### Not yet proven

- historical XAUUSD.ecn calendar;
- historical DST behavior;
- historical holiday exceptions;
- completeness of every returned/missing interval.

## 10. Frozen decision

**FROZEN:** The project will not infer or canonicalize a historical session calendar from missing-bar patterns alone.

**UNRESOLVED:** The actual historical XAUUSD.ecn session calendar remains an explicit research dependency.

A future `MT5_SESSION_CALENDAR_CONTRACT_V2` may freeze the historical calendar only after source-backed terminal evidence and reproducible validation are available.
