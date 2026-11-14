# MA Research — Decision Timestamp Capture Specification

Status: **RESEARCH DESIGN ONLY — NOT IMPLEMENTED IN THE LIVE RUNNER**

Branch: `research/ma-filter-forward-week-20261114`

## 1. Purpose

Define the minimum evidence required to align an MA observation with the information actually available when a Runner candidate is detected. This document does not define or change Strategy A entry, exit, fill, stop-loss, take-profit, or execution rules.

## 2. Historical evidence disposition

The currently audited V3.1 event records expose `trigger_time`, but do not expose a per-event detection/poll timestamp or order-send timestamp. The runtime source stamps `trigger_time` from the triggering M1 bar's broker/server epoch. The entry scan can inspect historical bars and return the first qualifying trigger, including the final array element.

Therefore:

- `trigger_time` is the triggering bar's open time; it is **not** a proven decision timestamp.
- File modification time, JSONL row order, and later broker deal time are not acceptable substitutes for the missing decision timestamp.
- Historical MA alignment to the exact Runner information set is **UNRESOLVED**.
- Existing historical rows must not be backfilled with guessed timestamps.

## 3. Required event fields for a future research population

Capture these fields at the observation boundary, before any order request is constructed:

| Field | Meaning | Requirement |
|---|---|---|
| `event_schema_version` | Version of this research event schema | Required |
| `candidate_id` | Stable ID shared by candidate, attempt, and result records | Required |
| `poll_sequence` | Monotonically increasing poll counter within one process session | Required |
| `process_session_id` | Unique ID for one process start | Required |
| `decision_observed_at_utc` | Host UTC wall-clock timestamp at the moment the candidate is observed | Required |
| `decision_monotonic_ns` | Monotonic-clock reading at the same observation boundary | Required |
| `trigger_time_server_epoch` | Existing trigger bar open time, explicitly retaining its broker/server epoch meaning | Required when known |
| `current_m1_bar_open_server_epoch` | Open time of the current M1 bar visible at observation | Required when known |
| `last_completed_m1_bar_open_server_epoch` | Open time of the most recent fully completed M1 bar at observation | Required when known |
| `last_completed_m1_bar_close_server_epoch` | Close boundary for that completed bar, using the source's verified time convention | Required when known |
| `server_utc_offset_seconds` | Verified server-to-UTC offset applicable at observation | Required when known; otherwise null |
| `bar_snapshot_sha256` | Hash of the exact ordered M1 bar slice used for the observation | Required for reproducibility |
| `bar_snapshot_range` | First/last bar times and count included in the hashed slice | Required |

The same `candidate_id`, `process_session_id`, and `poll_sequence` must be carried into corresponding candidate, order-attempt, and order-result records. Record order alone is not a correlation mechanism.

## 4. Timestamp and clock rules

1. Store UTC wall-clock time as an ISO-8601 value with an explicit `Z` suffix.
2. Store monotonic time separately; never convert monotonic time into UTC.
3. Preserve broker/server epoch fields separately from UTC fields. Do not silently relabel one as the other.
4. Record the server offset only when it has been independently verified for that observation period. Do not assume a fixed offset across daylight-saving transitions.
5. Capture the completed-bar boundary from the actual M1 snapshot used at observation, not by deriving it from `trigger_time`.
6. If any required timestamp or bar-boundary field is absent or inconsistent, mark that observation `UNRESOLVED`; do not silently fall back to fill time or trigger time.

## 5. MA alignment contract for the research analyzer

For a future captured observation, MA inputs may only use M1 bars that were fully completed and available at `decision_observed_at_utc`. The analyzer must verify the recorded bar snapshot and the recorded completed-bar boundary before assigning a filter state.

The existing selected gap policy remains in force: every M1 delta greater than 60 seconds starts a new segment; SMA/EMA remain unavailable until a full contiguous period exists; EMA is seeded from the SMA of that segment. This is a research data-validity policy, not a canonical Strategy A rule.

Do not infer hypothetical outcomes for candidates rejected by an MA filter from the outcomes of trades that the Runner actually placed.

## 6. Synthetic fixture requirements before implementation

A separate research-only capture component and analyzer must have fixtures proving:

- UTC wall-clock and monotonic timestamps are both captured at the observation boundary.
- Trigger-bar time remains distinct from observation time.
- A historical trigger discovered during a later poll does not get mislabelled as a contemporaneous decision.
- Current/incomplete M1 bar is distinguished from the last completed M1 bar.
- Candidate, order-attempt, and order-result records retain the same correlation identifiers.
- Missing/unknown server offset remains null and does not cause a guessed conversion.
- Daylight-saving/offset changes do not rewrite previously recorded timestamps.
- Missing or contradictory bar boundaries produce `UNRESOLVED`.
- The exact bar slice hash changes when any included bar changes.
- No MT5 order, position, SL, TP, or account mutation is performed by the research capture test harness.

## 7. Scope and safety boundary

- No edits to the live V3.1 Runner, its imported runtime, production configuration, or Telegram routing.
- No calls to `order_send` or any trade-management API from the research capture component.
- No production BUY/SELL decisions.
- No canonical MA period/type/filter selection.
- No replay/backtest authorization: execution/fill/commission/spread/intrabar semantics remain separately gated.
- Implementation, if later approved, belongs in an isolated research-only copy or standalone observer and must be validated before any data is admitted to Discovery.

## 8. Current disposition

**Historical decision-time alignment: UNRESOLVED.**

**Future timestamp capture: SPECIFIED; standalone research record builder and synthetic fixtures added. Not integrated with any Runner or MT5 process.**

The original 31-test MA validation run passed before the latest strict-validation hardening. Two additional regression fixtures now cover malformed UTC timestamps and an intervening bar that contradicts the declared last-completed-bar boundary. The expanded local suite must be rerun before those latest changes are considered validated.

See [MA_DECISION_OBSERVER_INTEGRATION_REVIEW.md](MA_DECISION_OBSERVER_INTEGRATION_REVIEW.md) for the isolated observer architecture, evidence modes, safety controls, and acceptance gates.

Historical alignment remains unresolved. Any future shadow observer records its own observations and must not be presented as exact telemetry from the production Runner.
