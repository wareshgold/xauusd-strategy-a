# SP2L Historical Session Resolution — Next Evidence Gate — 2026-09-17

## Objective

Resolve whether the current MT5 session calendar can be applied to historical XAUUSD.ecn M1 data, especially July 2026, without inference from observed gaps.

## Evidence currently available

1. Native MQL5 session metadata on the identified terminal reports Monday-Friday quote/trade sessions as `01:00:00` to `00:00:00`, with no Saturday/Sunday sessions.
2. Current symbol specification for `OtetGroup-MT5 / XAUUSD.ecn` has been captured separately.
3. The July 2026 audit using that current calendar fails: 257 expected timestamps are missing and 14 timestamp jumps are invalid under the current calendar.
4. Official broker holiday evidence states that XAUUSD had a special early close on 3 July 2026 at 20:00 (published in broker/server time), demonstrating that historical holiday/session exceptions exist.

## What remains unresolved

The evidence does not yet establish the complete historical session schedule for `OtetGroup-MT5 / XAUUSD.ecn` in July 2026, nor a complete UTC mapping for the broker-published holiday schedule.

Therefore:

- July remains `AUDITED_FAIL` under the current-calendar audit.
- Historical session applicability remains `UNRESOLVED`.
- No missing bars may be fabricated, shifted, interpolated, or silently removed.
- No SP2L geometry or execution rule may be changed to fit the observed data.

## Next deterministic evidence request

Obtain a broker/terminal historical session specification that is tied as closely as possible to:

`Otet Group Ltd. / OtetGroup-MT5 / XAUUSD.ecn / July 2026`

Acceptable evidence candidates, in descending preference:

1. Broker-provided historical symbol/session specification or archived trading-hours schedule for July 2026.
2. Terminal/broker report that explicitly records historical trading sessions for the exact symbol/server and date range.
3. Broker-published historical holiday calendar plus independently established server-time/UTC mapping, sufficient to reconstruct exceptions without guessing.
4. Other primary-source broker evidence with exact applicability to the symbol/server.

## Re-audit rule

Only after historical session applicability is resolved will the July dataset be re-audited. The re-audit must preserve exact timestamps and use only the resolved historical calendar. A passing audit requires exact expected active timestamps, uniqueness, chronology, and no invalid in-session jumps.

## Non-goals

This gate does not define or modify:

- P-Gap formula;
- spike geometry;
- AB=CD/F14 anchors or tolerance;
- entry semantics;
- stop-loss or take-profit semantics;
- fill/execution model;
- lifecycle rules;
- production BUY/SELL generation.

## Decision state

`SOURCE RESOLUTION / DATA PROVENANCE`

Historical session calendar: `UNRESOLVED`

July data audit under current calendar: `AUDITED_FAIL`

Canonical strategy: `BLOCKED`

Production: `NOT AUTHORIZED`
