# SP2L Data Plane Gate — 2026-09-15

## Status

`PREPARATION ONLY — NOT A SOURCE OR FREEZE GATE`

The data-plane work may proceed only as engineering preparation. It must not unblock source resolution or canonical geometry freeze.

## Gate ordering

`SOURCE → HUMAN ADJUDICATION → FROZEN GEOMETRY → DATA/ENGINE IMPLEMENTATION → VALIDATION`

Data acquisition does not move a blocked geometry dimension to a resolved state.

## Research path

Twelve Data remains the repository-documented initial research candidate. Raw M1 is the intended research base; M5 can be derived deterministically from M1 where required.

## MT5 path

MT5 terminal/broker data is the intended runtime/tester data plane. No Twelve Data-to-MT5 forwarding dependency is required.

## Separation requirement

Research and MT5 adapters must converge on the same normalized candle contract. The canonical Strategy A engine remains provider-neutral.

## Hold point

No live API acquisition, MT5 EA implementation, or performance comparison is required to complete this architecture gate. Those become appropriate only after the relevant upstream research gates authorize them.
