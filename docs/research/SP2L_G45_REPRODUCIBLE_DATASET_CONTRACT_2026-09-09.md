# SP2L G45 — Reproducible Dataset Contract

Date: 2026-09-09
Gate: G45
Status: CONTRACT DEFINED; real-data sample provenance captured

## Objective

Establish a deterministic, auditable artifact contract for historical XAU/USD research data before any Strategy A historical detector or optimization is introduced.

## Required identity

Every acquired dataset must preserve:

- provider and instrument;
- interval/timeframe;
- requested UTC bounds;
- retrieval timestamp;
- explicit source timezone provenance when timestamps are naive;
- source/provider metadata;
- raw response bytes or canonical raw serialization;
- normalized canonical OHLC records;
- raw SHA-256 fingerprint;
- normalized SHA-256 fingerprint;
- quality-audit result.

## G44 sample registered

The first real sample audited under G44 is:

- Provider: Twelve Data
- Symbol: XAU/USD
- Interval: 1min
- Rows: 5,000
- Explicit source timezone: Australia/Sydney
- Normalized range: 2026-09-05T21:17:00+00:00 through 2026-09-09T08:36:00+00:00
- Raw SHA-256: `3060db7473b5f43610b265f43c6c827052c89334420dbaf5163e7925f9d94979`
- Normalized SHA-256: `dbcf0b681b79e925cb320d7164dac0980e97eeb338ae1996ab4e852e35622f5f`
- Structural quality: PASS

The raw JSON remains local and is intentionally not committed to Git.

## Reproduction rule

A dataset is reproducible only when the same raw artifact, normalization contract, explicit timezone provenance, and canonical serialization reproduce the same raw and normalized fingerprints.

A changed provider response, source timezone, normalization rule, or canonical serialization creates a new dataset identity and must not silently overwrite an existing identity.

## Feed separation

Different XAU/USD feeds must be stored and fingerprinted independently. Timestamp alignment, missing bars, price deviations, and candle-construction differences may be measured, but feed selection must not be made because one feed produces better Strategy A backtest performance.

## Strategy boundary

G45 is strategy-neutral. No P-Gap, Entry, Stop, Trigger, AB=CD, Leg2, TP, or BUY/SELL rule is introduced by this contract.

Frozen Geometry remains blocked until source-resolution blockers are independently resolved.
