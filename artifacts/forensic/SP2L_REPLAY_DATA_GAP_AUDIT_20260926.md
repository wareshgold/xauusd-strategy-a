# SP2L Replay Audit — 2026-09-26

## Finding

The existing XAUUSD replay artifact contains **26 detected candidates**, but it is not yet a valid uninterrupted seven-day evidence set.

Requested interval: 2026-09-16 00:00 UTC through 2026-09-23 00:00 UTC.

Returned bars: 10,081.

Filtered bars: 6,895.

There are four data gaps:

1. 2026-09-16 23:59 -> 2026-09-17 01:00: 60 minutes
2. 2026-09-17 23:58 -> 2026-09-18 01:00: 61 minutes
3. 2026-09-18 23:57 -> 2026-09-21 01:00: 2,942 minutes
4. 2026-09-21 23:58 -> 2026-09-22 01:00: 61 minutes

The large weekend gap is expected for a market-closed interval. The three approximately one-hour daily gaps are also consistent with broker/session discontinuities, but their exact semantic interpretation is not being promoted without source confirmation.

## Consequence

The 26-signal result (16 WIN / 10 LOSS, +6R, PF 1.60) remains a **research replay result**.

It must not be described as a continuous seven-day sample, and it must not be used to modify canonical geometry.

## Important candidate-level observation

The artifact's first candidate is:

- raw epoch: 1789528800
- rendered time: 2026-09-16 03:20 UTC
- direction: BUY
- entry: 4284.28
- SL: 4283.06
- TP: 4285.50

The artifact explicitly says its timestamp mapping remains unresolved. Therefore this timestamp is retained as an exact raw-source identifier, not treated as confirmed UTC wall-clock truth.

## Next forensic requirement

For Monday open-market evidence, preserve both:

- raw MT5 epoch;
- independently captured wall-clock UTC.

Then reconcile candidates using exact raw identifiers first. No timezone shift should be inferred merely because a shifted timestamp makes records match.

## Status

- Data integrity within returned replay: PASS
- Continuous market-data coverage: NOT PROVEN
- Historical timestamp semantics: UNRESOLVED
- Candidate geometry: research-only
- Canonical promotion: BLOCKED
