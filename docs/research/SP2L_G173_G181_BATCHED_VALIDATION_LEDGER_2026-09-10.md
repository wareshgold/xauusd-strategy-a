# SP2L G173-G181 — Batched Validation Ledger

## Purpose

Create one deterministic ledger boundary tying source provenance, dataset identity, specification version, fixture evidence, DEV evidence, and validation evidence together.

## Gates

- G173: source version is recorded.
- G174: dataset fingerprint is recorded.
- G175: specification version is recorded.
- G176: fixture evidence fingerprint is recorded.
- G177: DEV result fingerprint is recorded.
- G178: validation result fingerprint is recorded.
- G179: missing required evidence reports UNKNOWN.
- G180: touched holdout blocks.
- G181: complete untouched ledger may PASS.

## Production boundary

A ledger PASS is evidence integrity only. It does not freeze Strategy A geometry and does not authorize live BUY/SELL decisions. All unresolved source geometry remains fail-closed.
