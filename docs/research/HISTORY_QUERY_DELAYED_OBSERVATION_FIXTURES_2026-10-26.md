# History Query / Delayed-Observation Fixture Contract — 2026-10-26

## Source-aligned boundary

The pinned research source `scripts/sp2l_tracked_deal_history.py` distinguishes a valid empty iterable from a failed history query: an empty result can be processed as an empty observation, while `None`, a raised exception, or an unavailable query function raises `DealHistoryQueryError`. The Strategy A wrapper catches that error, records a diagnostic, saves state, and defers lifecycle delivery for that poll.

The source also re-queries tracked order IDs and linked position IDs on subsequent polling cycles. Therefore, a deal absent from one successful query must not be rewritten as a permanent absence: a later query may expose it. This fixture models only the observation contract; it does not establish why or when a broker may publish history.

## Fixture semantics

- `QUERY_FAILED_DEFER`: at least one requested query failed. Do not aggregate a partial snapshot into a lifecycle conclusion.
- `EMPTY_OBSERVED`: all supplied query responses succeeded and contained zero rows. This describes only those queries at that poll; it is not proof of complete account history, no fill, or a closed/nonexistent position.
- `OBSERVATIONS_FOUND`: one or more supplied rows were observed. This does not prove full fill, all partial deals, or complete history.
- `UNRESOLVED`: query identity/response shape is invalid or no query observations were supplied.

A later poll may change from `EMPTY_OBSERVED` to `OBSERVATIONS_FOUND`; the earlier poll remains an accurate record of what it observed at that time. No timeout, retry count, history-completeness watermark, broker clock assumption, or synthetic closure is defined here.

## Tests and limits

Synthetic tests cover `None`, exceptions, empty iterables, supplied rows, malformed responses, no queries, and delayed appearance on a later poll. The tests do not connect to MT5, change runner behavior, or prove real broker history latency.

Replay remains blocked on actual source/data binding, event timing and ordering, partial-fill accounting, cost semantics, trailing outcomes, and other previously documented execution blockers.
