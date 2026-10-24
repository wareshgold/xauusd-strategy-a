# SP2L Research Path — P/L Accounting Extension

The historical 2026-09-14 to 2026-09-18 signal window now has a separate pip and broker-specific P/L accounting layer.

Next research step: propagate this accounting schema into future research reports and compare performance across fixed accounting lot sizes without changing Strategy A geometry or execution semantics.

Required guardrails:
- no canonical rule changes
- no production signal generation
- no live authorization
- preserve ambiguous outcomes as unresolved
- retain broker metadata as accounting inputs only
- keep pip convention explicit
- keep execution costs separate until sourced/verified

Current production/live status remains BLOCKED/DISABLED.
