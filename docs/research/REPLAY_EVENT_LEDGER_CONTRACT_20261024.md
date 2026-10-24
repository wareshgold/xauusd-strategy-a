# Research-only event ledger contract — Strategy B vs RR2/TRAIL4 (2026-10-24)

**Status: proposed evidence schema; not an execution specification and not canonical Strategy A rules.**

## Purpose and safety

This contract describes how to preserve lifecycle evidence for offline comparison. It does not simulate broker behavior, turn candle touches into fills, infer missing events, or authorize a strategy decision. Strategy B and RR2/TRAIL4 must remain separate source profiles. Do not connect to MT5, modify a runner/config/state/event log, or run a live test as part of this work.

## Event vocabulary

Allowed normalized labels for research records:

- `SIGNAL_CANDIDATE`: a strategy implementation reported a candidate; not an order and not a fill.
- `ORDER_SUBMITTED`, `ORDER_REJECTED`, `ORDER_CANCELLED`, `ORDER_EXPIRED`: only when an identifiable source event supports that label. These are not assumed to exist in every implementation.
- `ENTRY_FILL`: an evidenced actual fill, or a clearly labeled proxy event. Proxy and actual events must never be conflated.
- `SL_UPDATE_SUBMITTED`, `SL_UPDATE_CONFIRMED`, `SL_UPDATE_REJECTED`: distinguish request from confirmation; do not assume every proposed update reached the broker.
- `EXIT_FILL`: evidenced closing fill / deal, not merely an OHLC touch.
- `DATA_END`: replay input boundary, not an exit.
- `OPEN_AT_END`: derived lifecycle assessment when entry is evidenced but no closing event is evidenced before the data boundary.
- `UNKNOWN` / `AMBIGUOUS`: assessment values for insufficient or conflicting evidence, not broker event types.

This vocabulary is an audit normalization layer. A label may be absent if its source system does not emit that event. Never manufacture a missing source event to make a lifecycle look complete.

## Required record envelope

Each event row should preserve these fields where available; unavailable values stay null:

| Field | Requirement |
|---|---|
| `schema_version` | Contract version, currently `1.0-proposal`. |
| `run_id`, `event_id`, `candidate_id`, `trade_id` | Stable identifiers; trade ID may remain null until a source-backed association exists. |
| `strategy_id`, `profile_id` | Explicitly identify the implementation and its event adapter; do not use a universal execution profile. |
| `source_commit`, `config_sha256`, `dataset_sha256` | Immutable source/config/data identity where applicable. |
| `event_type` | Normalized vocabulary above. Preserve original source event name separately. |
| `source_event_ref`, `source_artifact_sha256`, `source_row_ref` | Traceable provenance. A synthetic fixture must identify itself as synthetic. |
| `event_time_original`, `event_timezone_basis`, `event_time_utc` | Preserve original timestamp and the evidence for its timezone mapping. UTC must be null/unknown if the mapping is not supported. |
| `source_sequence_id` | Exact source ordering token when available. Do not manufacture a tie-breaker. |
| `price`, `volume`, `side`, `order_id`, `position_id`, `deal_id` | Nullable source values; never fill from theoretical references without labeling them as derived/proxy. |
| `evidence_class` | For example `source_observed`, `synthetic_fixture`, or `ohlc_proxy`. |
| `notes`, `warnings[]` | Missing evidence, assumptions, contradictions, timestamp uncertainty. |

The ledger/run manifest must also retain the exact replay code commit, adapter/profile version, schema version, window boundaries and convention, symbol metadata, environment/command, and original input hash. Hash original bytes before parsing.

## Profiles are intentionally separate

### Strategy B live bot

The inspected source audit describes a forming-M1-candle poll loop followed by a market deal. Its event adapter may record a candidate/trigger, an actual market-order submission, and an evidenced deal/fill when source/broker records exist. A candidate or trigger is not itself a fill. Preserve the source's event names and references alongside normalized labels. If an actual deal cannot be evidenced, entry status remains `UNKNOWN`; an OHLC estimate must be labeled as a proxy.

### Strategy A RR2/TRAIL4 research baseline

The inspected config labels its order mode `PENDING_LIMIT_RESEARCH`, with a 30-minute pending TTL. Its adapter must preserve separately evidenced pending-order submission, rejection/cancellation/expiry, fill, SL-update request/confirmation/rejection, and exit/deal events when present. The configured research mode does not prove that a theoretical entry reference was filled. Do not transfer Strategy B market-deal semantics into this profile or infer canonical Strategy A rules from the runner.

### Adapter rule

A profile documents source-confirmed event vocabulary and source references; it does **not** define a universal state machine. Sequence constraints must be backed by that profile's source evidence. Unknown profile semantics stay unresolved and are recorded as such.

## Ordering and lifecycle assessment

1. Preserve source ordering IDs when available. Use timestamps to compare events only when both timestamps and their timezone mappings are evidenced.
2. If two events have equal timestamps and no source sequence ID, their order is `AMBIGUOUS`; do not sort them by file order or event-type preference.
3. A submitted SL update is not a confirmed SL update. If the update and exit cannot be ordered from evidence, do not claim the new stop caused the exit.
4. A rejection can support `NOT_FILLED` only when the evidence establishes that rejection is terminal for the relevant order and no earlier/partial fill is possible in that source context. Otherwise retain `UNKNOWN`.
5. Repeated candidates are separate candidate observations unless a source-backed identity/deduplication key proves they refer to the same candidate. Never assume they create duplicate fills or that they are duplicates.
6. `DATA_END` is not an exit. If entry is evidenced and no exit is evidenced before the data boundary, assess `OPEN_AT_END`; if entry itself is not evidenced, keep the lifecycle `UNKNOWN`.
7. An `EXIT_FILL` requires exit evidence. A candle touching SL/TP or a trailing reference alone is not an exit fill.
8. Missing intervals or conflicting events remain `UNKNOWN` / `AMBIGUOUS` / `NOT_DETERMINABLE`, not silently resolved.

## Deterministic synthetic acceptance matrix

The paired test file `tests/test_replay_event_ledger_contract_fixtures.py` must cover:

- candidate is not fill; a later SL/TP touch cannot create an entry or exit fill;
- an explicit, source-referenced terminal rejection can support `NOT_FILLED`, but missing fill evidence cannot;
- repeated candidate observations do not establish repeated fills or duplicate suppression;
- SL-update request vs exit ordering is resolved only by evidenced time/sequence; tied times without sequence remain ambiguous;
- an evidenced entry with no exit before `DATA_END` is `OPEN_AT_END`, and `DATA_END` is never `EXIT_FILL`;
- Strategy B market-deal and RR2/TRAIL4 pending-limit profiles remain distinct;
- every fixture ID is unique and fixture records retain provenance/time-basis fields.

Tests must use synthetic data only and must not import MT5, broker APIs, forward runners, or signal-generation code. Passing tests checks the contract fixtures only; it does not establish source fidelity, historical replay parity, statistical edge, or profitability.

## Current gate

**Comparison remains BLOCKED.** Historical timestamp mapping, actual fill/exit evidence, intrabar trailing ordering, overlap, and common historical costs are still unresolved. This contract is research instrumentation only; no paired backtest should be presented as execution-accurate until those gates are independently resolved.


## Structural validation gate

The proposed envelope is now checked by [the read-only schema validator](./EVENT_LEDGER_SCHEMA_VALIDATOR_20261024.md) and its synthetic tests. The validator checks key presence, nullable-field handling, identifier uniqueness, hash shape, event vocabulary, JSONL syntax, and timestamp conversion evidence. It deliberately does not prove the event is true or the timestamp mapping is correct. Passing this gate is structural validation only.
