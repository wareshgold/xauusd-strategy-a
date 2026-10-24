# Exact broker-deal join audit (research-only)

Script: `scripts/audit_sp2l_exact_deal_join_readonly.py`

Tests: `tests/test_audit_sp2l_exact_deal_join_readonly.py`

## Purpose

This utility audits two already-preserved JSONL snapshots: normalized source events and normalized broker-deal rows. It does not parse platform-specific logs, define a strategy adapter, establish source authenticity, or simulate trades. Its only automatic join key is exact `deal_id` equality.

The script never uses timestamp proximity as a join key, never infers a fill from OHLC, never substitutes requested volume for executed volume, and refuses to overwrite an existing report path.

## Input contract

Each nonblank line must be a JSON object. Unparseable lines and non-object JSON values are reported in `rejected_rows` rather than silently discarded.

Source-event rows should provide:
- `event_id`: stable unique source-event identifier;
- `deal_id`: broker deal identifier explicitly present in the source evidence;
- optional `order_id` and `position_id`;
- any observation timestamp under its original field name (not used for joining).

Broker-deal rows should provide:
- `deal_id`: stable broker deal identifier;
- `execution_time_original`: original broker execution time string, with time basis documented separately by the intake package;
- `execution_price`: positive numeric executed price;
- `executed_volume`: positive numeric executed volume;
- optional `order_id` and `position_id`.

These names are the normalized audit input contract, not claims that the raw source systems already export these exact names. Raw source fields must be preserved in the immutable package and any normalization must be separately documented and reviewable. Missing IDs must not be manufactured to make this tool run.

## Example invocation

Run only against stable, offline snapshots, not a live file currently being written. Choose a new output filename for every run:

```powershell
python scripts/audit_sp2l_exact_deal_join_readonly.py `
  --events .\evidence\normalized-source-events.jsonl `
  --deals .\evidence\normalized-broker-deals.jsonl `
  --output .\reports\deal-join-audit-run-001.json
```

The report records input SHA-256 hashes and byte sizes, parsed/rejected row counts, duplicate IDs, multi-event claims, exact-ID match status, missing execution fields, and unmatched rows in both directions. Report order follows source line order; JSON keys are sorted when writing the file.

## Status semantics

- `CONFIRMED_IDENTITY_FIELDS_COMPLETE`: exact deal ID match, no detected order/position conflict, unique event/deal identifiers, and required execution time/price/volume fields present. This is not independent proof that the source is authentic or the timestamp is correctly mapped.
- `IDENTITY_MATCH_INCOMPLETE`: exact unique deal ID exists, but execution timestamp, price, or volume is missing/invalid.
- `AMBIGUOUS`: duplicate IDs, multiple source events claiming the same deal, or conflicting link fields.
- `UNMATCHED`: no exact counterpart or required source identity missing.

All statuses are research diagnostics. A downstream replay must not silently promote any status into a canonical trade event. Manual provenance and timezone review remain required.
