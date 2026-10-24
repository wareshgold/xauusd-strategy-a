# RR2/TRAIL4 event adapter field map (2026-10-24)

**Status: offline source inspection only. No runtime event sample was read. No live files were changed.**

This document maps fields observed in the checked-in RR2/TRAIL4 base runner to the proposed research ledger. It is an adapter plan, not a canonical execution specification. Source: branch `fix/rr2-trail4-pending-lifecycle-safe-20261011`, file `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`, blob SHA `185dc62d74c6e202e01c361c9550592d0c33470b`.

## Global event envelope

The logger emits `{"ts_utc": now_utc(), **event}` as one JSON object per line. `now_utc()` is `datetime.now(timezone.utc).isoformat()`; therefore the value is the runner's observation/write timestamp, not necessarily the broker event timestamp.

| Source field | Ledger disposition | Limitation |
|---|---|---|
| `ts_utc` | Preserve as `observed_at_utc` in adapter metadata; do not overwrite `event_time_original` | Logger timestamp, not broker deal time |
| `event` | Preserve verbatim as `source_event_ref`/source event name metadata; map to a normalized event only where semantics are evidenced | Event vocabulary is source-specific |
| JSONL line number | `source_row_ref`, e.g. a row number within the immutable copy | Stable only when paired with exact artifact SHA-256 |
| SHA-256 of original event-file bytes | `source_artifact_sha256` | Hash the immutable copy before parsing; never hash a rewritten serialization as the source |
| `event_id` / `source_sequence_id` | Leave null unless a source-backed identifier/order token exists | Current logger does not add either field globally |
| `source_commit`, config/data hashes | Manifest-level provenance | Do not infer from a filename or current branch |
| `event_time_original`, `event_timezone_basis`, `event_time_utc` | Keep broker/source time separate from observation time | A timestamp field or epoch integer alone does not establish its timezone mapping |

The JSONL writer does not add a schema version, event ID, artifact hash, or sequence ID. Those are adapter/manifest metadata, not fields to pretend were emitted by the runner.

## Event-specific field map

### `TELEGRAM_DEAL_LIFECYCLE`

Observed fields include `symbol`, `deal`, `order`, `position`, `signal_id`, `entry`, `reason`, `entry_price`, `theoretical_entry`, `theoretical_sl`, `theoretical_tp`, `entry_slippage`, `actual_r`, `exit_price`, `pips_result`, `profit`, `commission`, `swap`, `net`, `telegram`, and `canonical`.

- `deal` is a deal ticket/reference and is the strongest available event identifier in this row, but keep it in `deal_id`; do not fabricate a globally unique `event_id`.
- `entry` and `reason` are broker enum integer codes in this source context. Preserve raw codes and their source profile; map to entry/exit semantics only with the matching MT5 enum/source version.
- `entry_price` / `exit_price` have context-dependent meaning. On an entry-deal event, the lifecycle handler's local `exit_price` value may be populated from the current deal's price. Do not blindly map these fields to ledger `price` without checking the raw `entry` code and source logic.
- `profit`, `commission`, `swap`, `net` are reported deal-related amounts. Preserve original currency/accounting semantics and validate whether the event is entry or exit before aggregating; do not sum repeated position-level snapshots as realized P&L.
- The code uses `deal.time` to construct the human-facing Telegram message timestamp, but that timestamp is not included in the logged `TELEGRAM_DEAL_LIFECYCLE` object. Thus the JSONL event alone does not preserve the broker deal time.
- No source sequence token is emitted. Equal `ts_utc` values do not establish order.

Permitted normalized interpretation: a source-observed deal-lifecycle record, with the original row and artifact hash preserved. It may be mapped to `ENTRY_FILL` or `EXIT_FILL` only after the raw `entry` code is interpreted under the identified source profile and the deal ID, execution price, volume, and relevant broker evidence are present. This current event object does not include a dedicated raw deal volume field; obtain it from an immutable broker deal export/history artifact or leave volume unresolved. Do not infer it from current position volume.

### `PENDING_ORDER_LIFECYCLE`

Observed fields include `order`, `state`, `state_code`, `type`, `type_time`, `time_setup`, `time_done`, `magic`, `position_id`, `position_by_id`, `volume_initial`, `volume_current`, `price_open`, `price_current`, `sl`, `tp`, and `canonical`.

- Preserve `state` and `state_code` as raw source values. Normalize to submitted/rejected/cancelled/expired only when the source enum and state transition justify it.
- `time_setup` and `time_done` are raw broker-provided time fields. Preserve their raw integer values and the source timezone basis. Do not silently label them UTC.
- `volume_initial` and `volume_current` describe order state, not proof of an executed fill.
- `position_id` on an order record does not by itself prove a specific fill event or its price.

### `POSITION_LIFECYCLE`

Observed fields include `position`, `magic`, `type`, `volume`, `price_open`, `price_current`, `sl`, `tp`, and `profit`.

This is a broker-position snapshot, not a deal ledger. It may support state diagnostics but must not be translated directly into an `ENTRY_FILL` / `EXIT_FILL`. The `profit` field is snapshot state and is not necessarily realized P&L.

### `TRAIL_UPDATE` and diagnostic events

Keep an attempted stop update distinct from a broker-confirmed stop state. Preserve success/retcode and the raw row. A successful request result must not be promoted to `SL_UPDATE_CONFIRMED` unless source evidence establishes the broker accepted/applied the change. Query failures and reconciliation gaps are diagnostic evidence, not fills or exits.

## Deterministic adapter acceptance rules

1. Hash the original immutable JSONL bytes and retain the exact row number before any normalization.
2. Store `ts_utc` as observation time only. If broker event time is absent, `event_time_utc = null`; do not copy observation time into it.
3. Preserve raw source event name, enum codes, ticket IDs, and numeric fields in addition to any normalized representation.
4. Do not infer volume, deal time, or event ordering from a position snapshot, Telegram message, current market quote, or neighboring JSONL row.
5. Do not create an actual fill row from `POSITION_LIFECYCLE`, an order's theoretical price, an OHLC touch, or a trailing reference.
6. If a historical deal export supplies the missing deal time and volume, keep that export as a separately hashed source artifact and link its row/reference to the normalized record. Do not alter the original event file.
7. If the evidence cannot support a mapping, retain `UNKNOWN` / `AMBIGUOUS` / `NOT_DETERMINABLE` in the assessment and state the exact missing field.

## Gate status

This field map narrows the adapter design but does not make historical replay executable. An immutable, source-identified event snapshot and broker deal export are still needed to verify actual event rows, deal volume/time, timezone basis, and source ordering. The Strategy B comparison also requires its own actual-deal evidence. No performance comparison or profitability claim is authorized by this document.
