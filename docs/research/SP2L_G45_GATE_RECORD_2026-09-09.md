# SP2L G45 Gate Record

## Gate
G45 — Reproducible Dataset / Acquisition Provenance

## Result
**PASS — contract and sample identity established.**

## Evidence
- G44 real XAU/USD 1min sample passed structural quality audit.
- Raw fingerprint: `3060db7473b5f43610b265f43c6c827052c89334420dbaf5163e7925f9d94979`.
- Normalized fingerprint: `dbcf0b681b79e925cb320d7164dac0980e97eeb338ae1996ab4e852e35622f5f`.
- Explicit source timezone: `Australia/Sydney`.
- `tzdata==2026.3` is required for reproducible Windows timezone handling.
- Raw data remains local-only and is excluded from Git.

## Boundary
This gate does not resolve Strategy A geometry and does not authorize historical BUY/SELL detection, optimization, or profitability claims.

## Next permitted work
- repeatable acquisition artifacts;
- feed comparison with independent provenance;
- larger historical coverage acquisition;
- strategy-neutral execution/backtest infrastructure.

Frozen Geometry remains blocked.
