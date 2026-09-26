# SP2L Forward Continuity — Historical Evidence Gap — 2026-09-26

## Status

**UNRESOLVED — historical continuous polling is not provable from the preserved artifacts.**

This checkpoint records an evidence boundary only. It does not change Strategy A geometry, P-Gap semantics, fill semantics, execution rules, or canonical status.

## Historical intervals under investigation

The three previously flagged forward-test intervals were:

- 2026-09-24 10:00–10:15 UTC
- 2026-09-24 11:45–12:05 UTC
- 2026-09-24 12:35–12:55 UTC

The preserved `artifacts/forward-test/SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl` contains no matching timestamped events for those windows.

The preserved frozen runner log also does not cover those intervals: its observed timestamp range ends at approximately 2026-09-24 01:50 UTC.

## Forensic telemetry coverage

`artifacts/forensic/runtime/SP2L_FORWARD_FORENSIC_TELEMETRY_20260926T055934Z.jsonl` contains 452 parsed `ts_utc` values spanning:

- FIRST: 2026-09-26 05:59:34 UTC
- LAST: 2026-09-26 06:14:36 UTC

Therefore this telemetry capture does not provide direct evidence for the three historical 2026-09-24 intervals.

## API parity evidence

A separate same-terminal forensic comparison was completed using:

- `mt5.copy_rates_range()`
- `mt5.copy_rates_from()`

for XAUUSD.ecn M1 over three observed windows on 2026-09-24. All three windows had exact equality of timestamp sequence and OHLC between the two acquisition APIs.

This establishes API parity for those observed windows only. It does **not** prove continuous forward polling, eliminate runner lifecycle gaps, or prove that the historical forward intervals were continuously observed.

## Interpretation rule

Absence of preserved events is **not** classified as a proven polling outage.

The three intervals remain:

**UNRESOLVED — continuous polling not proven from preserved evidence.**

No claim of missed signal, missed data, or runner downtime is promoted from these artifacts.

## Required future evidence

A future forensic capture intended to prove forward continuity must preserve, at minimum, timestamped records for:

1. every polling iteration / heartbeat;
2. raw MT5 acquisition result metadata;
3. raw MT5 candle timestamp and OHLC;
4. detector result for each poll;
5. polling/data errors;
6. process start and stop lifecycle events;
7. a wall-clock timestamp alongside the raw MT5 timestamp.

The capture must span the complete interval under investigation.

## Canonical-rule boundary

This checkpoint does **not** authorize any change to:

- P-Gap formula or candle-role mapping;
- trigger acceptance semantics;
- trigger candle indexing;
- entry-price anchor;
- fill semantics;
- SL boundary;
- F13 order lifecycle;
- AB=CD anchors or tolerance;
- cancellation/expiry rules.

Those remain governed by source resolution.

## Reproducibility

Evidence reviewed for this checkpoint includes:

- `artifacts/forward-test/SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl`
- `artifacts/forensic/2026-09-26/runner_stdout_FROZEN_20260924_0632.log`
- `artifacts/forensic/runtime/SP2L_FORWARD_FORENSIC_TELEMETRY_20260926T055934Z.jsonl`
- `artifacts/forensic/2026-09-26/FORENSIC_API_PARITY_20260926T103635Z.json`

Conclusion: the historical continuity question remains explicitly unresolved rather than inferred from missing evidence.
