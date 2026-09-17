# SP2L Holiday / Special-Session Cross-Audit — 2026-09-17

## Purpose

Separate ordinary raw M1 availability boundaries from broker-published holiday or special-session events. This document is research evidence only. It does not define session rules, UTC conversion rules, execution rules, or SP2L geometry.

## Source hierarchy

1. Otet official financial-holiday calendar for broker-specific schedule claims.
2. Raw XAUUSD.ecn M1 availability artifacts produced by the MT5 acquisition/matrix tooling.
3. Current MT5 timestamp-basis diagnostic only as evidence of the observed current server basis; it must not be retroactively applied as a historical DST rule.

## Broker-published 2026 holiday evidence located

- 2026-06-19: Otet's holiday page lists XAUUSD as `Close at 20:00`. The page states that schedule times are MT5 server time. Source: https://otetmarkets.com/may-2026/
- 2026-09-07: Otet's current financial-holidays page lists XAUUSD as `Close at 21:30`. The page states that schedule times are MT5 server time. Source: https://otetmarkets.com/financial-holidays/
- 2026-04-03: Otet's April 2026 holiday page lists XAUUSD as `Closed`. Source: https://otetmarkets.com/april-2026/

## Raw MT5 evidence currently available in project

### 2026-06-19

The June-to-July raw availability matrix reports the 2026-06-15 to 2026-06-22 window with `actual_last_utc = 2026-06-19T20:00:00Z`. Its gap artifact contains the ordinary daily boundaries `23:59Z -> 01:00Z` for June 15-18, but no intra-Friday gap is present after the reported 20:00 UTC last bar.

### 2026-07-03

The June-to-July raw availability matrix reports the 2026-06-29 to 2026-07-06 window with `actual_last_utc = 2026-07-03T20:00:00Z`. Its gap artifact contains ordinary daily boundaries `23:59Z -> 01:00Z` for June 29-July 2, with no intra-Friday gap after the reported 20:00 UTC last bar.

### 2026-09-07

The contiguous July-September raw availability matrix contains an anomaly:
`2026-09-07T21:36:00Z -> 2026-09-08T01:00:00Z`, 203 missing M1 bars.

## Critical unresolved timestamp issue

The official Otet holiday pages explicitly express holiday times in MT5 server time. The raw availability artifacts are expressed in UTC. The current timestamp-basis diagnostic observed the account server at UTC+3 on 2026-09-17, while also explicitly warning that no historical DST rule should be inferred from that observation.

Therefore the official holiday times cannot currently be converted into historical UTC timestamps without introducing an unproven historical offset/DST rule.

Moreover, direct visual comparison of the published server-time values with the raw UTC last-bar timestamps must NOT be treated as a match. For example:

- 2026-06-19: published `20:00 MT5 server` vs raw `20:00 UTC`.
- 2026-09-07: published `21:30 MT5 server` vs raw anomaly beginning at `21:36 UTC`.

These are different time bases. Their numerical equality does not establish alignment.

## Current classification

| Event | Official broker evidence | Raw M1 evidence | Classification |
|---|---|---|---|
| 2026-06-19 | XAUUSD close 20:00 MT5 server | last raw bar 20:00 UTC | `UNRESOLVED_TIME_BASIS` |
| 2026-07-03 | holiday/special schedule requires official July source confirmation | last raw bar 20:00 UTC | `UNRESOLVED_TIME_BASIS` |
| 2026-09-07 | XAUUSD close 21:30 MT5 server | anomaly 21:36 UTC -> 01:00 UTC | `UNRESOLVED_TIME_BASIS` |
| ordinary Jun-Jul daily boundaries | no holiday required | repeated 23:59 UTC -> 01:00 UTC | `ORDINARY_RAW_BOUNDARY` (availability only) |

## Explicit non-conclusions

- No holiday event is being used as a canonical UTC session boundary.
- No historical UTC offset or DST rule is inferred.
- No `20:00 UTC` or `21:36 UTC` value is re-labeled as a broker server-time close.
- War/geopolitical events are not classified as market closures without an official trading-schedule source.
- No SP2L geometry, signal, trade, or execution logic is introduced.

## Next evidence gate

Resolve historical timestamp basis around the broker-published holiday dates. The required evidence is a source that establishes the relevant historical MT5-server-to-UTC relationship for those dates, or a terminal/API artifact that exposes historical session schedule values in an unambiguous time basis. Only after that can the June 19 / July 3 / September 7 events be classified as holiday early-close or closure in UTC.
