# Session Calendar Snapshot Schema v1

**Status:** FROZEN RESEARCH SCHEMA / NOT A CALENDAR

## Purpose

Define the machine-readable shape of a current MQL5 session-schedule observation so later historical resolution is deterministic and auditable.

## Required metadata

- `terminal`
- `company`
- `server`
- `symbol`
- capture timestamp/provenance when available

## Session record

Each observed session preserves:

- `kind`: `QUOTE` or `TRADE`
- `day`: terminal weekday
- `session_index`: terminal-provided index
- `from`: raw terminal representation
- `to`: raw terminal representation
- `from_epoch`: raw terminal epoch
- `to_epoch`: raw terminal epoch
- source line/reference

## Validation

The validator must reject malformed session records and non-contiguous session indices within each `(kind, day)` group.

## Interpretation boundary

A valid snapshot means only that the captured terminal output is structurally valid. It does **not** establish:

- historical schedule validity;
- UTC equivalence of session fields;
- DST history;
- holidays/special sessions;
- historical broker schedule changes;
- missing-bar semantics;
- SP2L rules.

Any derived UTC comparison must retain the raw server-time representation and document its conversion evidence separately.
