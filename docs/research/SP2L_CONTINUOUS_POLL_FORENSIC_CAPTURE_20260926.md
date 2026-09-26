# SP2L Continuous Poll Forensic Capture Checkpoint

Date: 2026-09-26

## Scope

This checkpoint records a read-only analysis of one real continuous MT5 polling forensic capture:

`artifacts/forensic/runtime/SP2L_CONTINUOUS_POLL_FORENSIC_20260926T105027Z.jsonl`

This is research/forensics evidence only. It does not change Strategy A geometry, P-Gap semantics, detector behavior, order execution, Telegram behavior, or canonical rules.

## Capture interval

- First record: `2026-09-26T10:50:27.847365+00:00`
- Last record: `2026-09-26T10:55:27.851237+00:00`
- Duration: approximately 5 minutes
- Total records: 152
- `FORENSIC_START`: 1
- `POLL`: 150
- `FORENSIC_STOP`: 1

## Poll cadence evidence

Across the 150 POLL records:

- Minimum timestamp gap: 2.000822 seconds
- Maximum timestamp gap: 2.211167 seconds
- Mean timestamp gap: 2.0043200604 seconds
- Gaps greater than 3 seconds: 0
- Gaps greater than 5 seconds: 0

Interpretation for this capture:

**Cadence continuity = PASS for the observed capture interval.**

The observed polling cadence is consistent with the runner's configured 2-second polling interval, with no observed timestamp gap above 3 seconds.

## MT5 acquisition evidence

All 150 POLL records reported:

- `status = DATA_OK`
- `returned_count = 10`
- `mt5_last_error = (1, "Success")`

Therefore:

- DATA_ERROR count: 0
- Empty-data poll count: 0
- Missing `poll_duration_seconds` count: 0

Interpretation for this capture:

**MT5 acquisition continuity = PASS for the observed capture interval.**

Every recorded poll returned 10 bars and reported MT5 success.

## Boundary of inference

This checkpoint proves only what is evidenced by this specific preserved capture interval.

It does **not** establish continuous polling during the historical 2026-09-24 windows:

1. 2026-09-24 10:00–10:15 UTC
2. 2026-09-24 11:45–12:05 UTC
3. 2026-09-24 12:35–12:55 UTC

The historical continuity status for those three windows remains:

**UNRESOLVED — continuous polling is not proven from preserved evidence.**

The absence of matching historical events is not treated as proof of a polling outage.

Likewise, the separate MT5 API parity result for the historical windows establishes parity between the two tested MT5 acquisition methods, but does not prove forward-loop continuity.

## Classification

| Evidence layer | Status | Meaning |
|---|---|---|
| This 2026-09-26 capture cadence | PASS | No observed polling gap >3s in this capture |
| This 2026-09-26 MT5 acquisition | PASS | 150/150 DATA_OK, 10/10 bars per poll |
| Historical 2026-09-24 polling continuity | UNRESOLVED | No preserved continuous capture spans those windows |
| Historical MT5 API parity | PASS | Previously tested acquisition methods matched in the observed windows |

## Safety boundary

No canonical Strategy A rule is inferred from this capture.

No P-Gap formula, candle-role mapping, trigger semantics, fill semantics, stop-loss rule, AB=CD tolerance, order lifecycle, or production BUY/SELL behavior is promoted or modified.

No live-trading action is part of this checkpoint.

## Reproducibility

The calculations in this checkpoint were performed directly against the preserved JSONL artifact named above. The artifact's raw records remain the evidence source; this document records the derived statistics and the limits of inference.

