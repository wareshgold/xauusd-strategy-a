# Immutable Paired-Replay Evidence Intake Contract (2026-10-24)

## Status and authority

**Research-only intake specification. Not a replay result, not evidence that either strategy has an edge, and not authorization to trade.**

This contract defines what must be recorded before Strategy B and RR2/TRAIL4 artifacts can be joined for a paired historical replay. It does not define SP2L geometry, fill semantics, exit rules, or missing timestamps. Missing or conflicting values remain `UNKNOWN` / `AMBIGUOUS`; they must not be inferred from OHLC candles, expected strategy behavior, or headline metrics.

No MT5 connection, order action, runner start, or live-state modification is permitted during intake.

## Required immutable package

Each intake package must have a new unique directory or immutable archive name. Never replace an existing package. Preserve the original bytes as received and calculate SHA-256 over those exact bytes before parsing or normalization.

Minimum package members:

1. `intake_manifest.json` — metadata below, with every field present or explicitly `null` plus a reason.
2. `dataset_m1_original.*` — original shared historical M1 data used by both strategy replays.
3. `strategy_b_source_events_original.*` — original Strategy B source event/log export, if available.
4. `strategy_b_broker_deals_original.*` — broker-confirmed Strategy B deal-history export, if available.
5. `rr2_trail4_events_original.*` — byte-preserved RR2/TRAIL4 event JSONL snapshot, if available.
6. `rr2_trail4_broker_deals_original.*` — broker-confirmed RR2/TRAIL4 deal-history export, if available.
7. `source_inventory.json` — exact repository, branch, commit, path, and content hash for the code/config used.
8. `intake_audit.json` — generated read-only integrity and join diagnostics, written to a new path and never confused with original source files.

An absent file must be recorded as absent; do not create an empty placeholder that could be mistaken for a genuine export.

## Manifest schema

The following is an illustrative template, not a statement that these values are already known. Replace placeholders only from source evidence; keep unknowns explicit.

```json
{
  "contract": "sp2l-immutable-paired-replay-intake-v1",
  "intake_id": "REPLACE_WITH_UNIQUE_ID",
  "created_at_utc": null,
  "prepared_by": null,
  "purpose": "offline paired Strategy B vs RR2/TRAIL4 research",
  "status": "INCOMPLETE",
  "artifacts": [
    {
      "artifact_id": "shared_m1_dataset",
      "role": "shared_market_data",
      "path": "dataset_m1_original",
      "present": false,
      "byte_size": null,
      "sha256": null,
      "format": null,
      "row_count_raw": null,
      "row_count_parsed": null,
      "first_source_timestamp": null,
      "last_source_timestamp": null,
      "timestamp_field": null,
      "timestamp_basis": "UNKNOWN",
      "symbol_as_exported": null,
      "source_system": null,
      "exported_at_utc": null,
      "notes": "Set present=true only when the original bytes exist."
    }
  ],
  "replay_scope": {
    "symbol_strategy_b": "XAUUSD.ecn",
    "symbol_rr2_trail4": "XAUUSD.ecn",
    "timeframe": "M1",
    "week_window_start_utc_inclusive": null,
    "week_window_end_utc_exclusive": null,
    "month_window_start_utc_inclusive": null,
    "month_window_end_utc_exclusive": null,
    "window_selection_frozen_before_results": false,
    "same_market_rows_for_both_strategies": false
  },
  "broker_time_profile": {
    "broker_or_server_name": null,
    "server_timezone_or_offset_at_export": "UNKNOWN",
    "dst_rule_or_transition_evidence": "UNKNOWN",
    "source_timestamp_semantics": "UNKNOWN",
    "conversion_method": "UNKNOWN",
    "conversion_evidence_ref": null
  },
  "source_versions": [
    {
      "strategy": "strategy_b",
      "repository": null,
      "branch": null,
      "commit_sha": null,
      "source_paths_and_sha256": [],
      "config_paths_and_sha256": []
    },
    {
      "strategy": "rr2_trail4",
      "repository": "wareshgold/xauusd-strategy-a",
      "branch": null,
      "commit_sha": null,
      "source_paths_and_sha256": [],
      "config_paths_and_sha256": []
    }
  ],
  "privacy": {
    "account_numbers_removed": null,
    "credentials_and_tokens_removed": null,
    "personal_data_reviewed": null,
    "redaction_method_and_effect_on_integrity": null
  },
  "integrity_checks": {
    "sha256_verified": false,
    "duplicate_rows_checked": false,
    "ordering_checked": false,
    "timestamp_gaps_checked": false,
    "out_of_window_rows_reported": false,
    "all_source_bytes_preserved": false
  },
  "join_audit": {
    "join_keys_proposed_from_source_only": [],
    "broker_deal_ids_unique_within_export": null,
    "unmatched_source_events_count": null,
    "unmatched_deals_count": null,
    "conflicting_order_or_position_links_count": null,
    "missing_execution_time_count": null,
    "missing_execution_price_count": null,
    "missing_executed_volume_count": null,
    "status": "NOT_RUN"
  },
  "limitations": [],
  "approval": {
    "source_owner_reviewed": false,
    "review_reference": null,
    "canonical_rule_changes_authorized": false
  }
}
```

For a real package, `artifacts` must contain one record for every supplied file, including both broker-deal exports and each event snapshot. The shortened example above shows the required field style; it is not a fixed list of only one artifact.

## Evidence and join rules

### 1. Byte integrity before parsing

- Hash every original file with SHA-256 before parsing, newline normalization, timezone conversion, sorting, filtering, or redaction.
- Record byte size, parser/version, encoding, row counts, and parse errors separately.
- If privacy redaction is necessary, retain the unmodified source securely outside the research repository and hash both original and redacted copies. Record the transformation and do not describe the redacted file as byte-identical to the original.
- Do not upload credentials, access tokens, account passwords, or unnecessary personal/account identifiers to GitHub.

### 2. Market-data integrity

- Preserve all source rows first. Report duplicate timestamps, non-monotonic ordering, gaps, invalid rows, and rows outside each requested window; never silently drop or synthesize them.
- Record the timestamp exactly as exported and the evidence supporting any UTC mapping. The suffix `Z` or a rendered UTC label alone does not prove the broker's historical server-time mapping.
- Freeze explicit inclusive start / exclusive end boundaries before viewing strategy results.
- Both strategies must consume the same immutable market-data bytes and the same row-selection manifest.

### 3. Actual deals versus diagnostics

- A market-order request, `order_send` response, order ticket, position snapshot, Telegram message, trailing update, or OHLC-derived outcome is not by itself a broker-confirmed fill.
- An actual deal row requires source-supported broker deal identity, original execution time/time basis, symbol, side/entry code, execution price, executed volume, and available financial fields. Preserve source field names and raw values alongside normalized values.
- Do not substitute runner `ts_utc` observation/write time for broker execution time.
- Do not infer executed volume from requested volume; do not infer execution price from candle open/high/low/close; do not infer missing deal IDs from nearby timestamps.
- Preserve order/deal/position identifiers exactly as exported. Any join using more than one identifier must report the evidence for that linkage.

### 4. Join accounting — no silent losses

For each source stream, report counts for:
- all raw rows;
- parsed rows and rejected rows;
- unique and duplicate deal IDs;
- events with no candidate deal;
- deals with no candidate source event;
- one-to-many and many-to-one matches;
- conflicting order/position links;
- missing or invalid execution time, price, or volume.

A match is `CONFIRMED` only when source identifiers and field semantics support it. Timestamp proximity alone may produce a separately labeled candidate, never a confirmed join. Do not discard unmatched rows; keep them in the audit with explicit reason codes. If two plausible joins conflict, status is `AMBIGUOUS`.

### 5. Replay eligibility

Use these separate statuses:

- `BLOCKED_MISSING_ARTIFACT`: a required immutable input is absent.
- `BLOCKED_HASH_OR_PARSE_FAILURE`: source integrity cannot be established.
- `BLOCKED_TIMESTAMP_MAPPING`: historical time basis is unresolved.
- `BLOCKED_FILL_EVIDENCE`: actual fill time/price/volume cannot be supported for the claimed replay fidelity.
- `BLOCKED_SOURCE_SEMANTICS`: the strategy's signal or execution behavior cannot be reproduced from source evidence.
- `DIAGNOSTIC_PROXY_ONLY`: a deliberately limited proxy can run, but it must not be called an exact source replica.
- `ELIGIBLE_FOR_OFFLINE_REPLAY_REVIEW`: package integrity and source reviews passed; this is not a pass on profitability or production readiness.

Do not collapse multiple blockers into a single green check. A package may have several simultaneous blockers.

## Deterministic synthetic join fixtures required before adapter use

The adapter's tests must include, at minimum:

1. One source event and one matching broker deal with exact stable IDs.
2. A source event with no broker deal.
3. A broker deal with no source event.
4. Duplicate broker deal ID.
5. Two events claiming the same deal ID.
6. Conflicting order ID versus position ID linkage.
7. Same timestamp but different deal IDs, proving timestamp-only joins do not match.
8. Missing broker execution timestamp.
9. Missing execution price.
10. Missing executed volume despite a requested volume.
11. Runner observation timestamp different from broker execution timestamp.
12. A malformed row that is retained in rejected-row diagnostics.
13. Out-of-window event retained and counted rather than silently dropped.
14. Repeated identical input produces byte-identical normalized output and audit, excluding explicitly declared nondeterministic metadata.

Every fixture must assert both the accepted result and the rejection/ambiguity reason. Synthetic fixtures validate deterministic implementation only; they do not establish historical facts.

## Completion gate

The intake is ready for adapter review only when:

- original bytes and hashes are preserved;
- source/config versions are pinned to exact commits and file hashes;
- shared market-data integrity and time mapping are documented;
- broker-deal exports and runner/event snapshots are present where required;
- unmatched and conflicting rows are accounted for;
- the synthetic fixture suite passes;
- unresolved limitations remain visible in the output.

Even then, the first replay is research-only. No performance claim, source-rule promotion, or production action follows automatically from a passing intake.
