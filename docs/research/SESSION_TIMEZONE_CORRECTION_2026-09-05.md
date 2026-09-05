# Session Timezone Correction — 2026-09-05

## Decision

The Poorsamadi time-window research must NOT use `Europe/Istanbul` as the trading-session timezone.

The canonical historical dataset timestamps are UTC. This is established by the downloader, whose default `XAUUSD_TIMEZONE` is `UTC`, and whose requested timezone is stored in dataset metadata.

The user's intended trading window is defined by the actual market sessions:

- London session: evaluated in `Europe/London`.
- New York session: evaluated in `America/New_York`.
- Trading is permitted only from the defined London start through the end of the defined New York session.
- Iran/local time is display/context only and is NOT the canonical session-definition timezone.
- UTC remains the canonical timestamp representation for stored historical data.

## Research correction

Previous exploratory partitions using `Europe/Istanbul` are retained as historical diagnostics only. They must not be promoted into trading rules or fresh-holdout hypotheses.

The next time/session research version must:

1. Convert each candle timestamp from canonical UTC into the relevant IANA market timezone when evaluating session membership.
2. Define London and New York boundaries explicitly and account for DST through the IANA timezone database rather than fixed UTC offsets.
3. Restrict the research universe to the intended London-through-New-York trading window.
4. Re-run DEV/VAL diagnostics before any fresh-holdout test.
5. Keep the fresh holdout locked until the corrected hypothesis is pre-registered.

## Non-goals

This checkpoint does not change production Strategy A rules, signal generation, entry logic, risk logic, or broker execution.

## Status

Research-only correction. No production rule is promoted by this document.
