# SP2L Synthetic Fixture Contract — 2026-09-14

## Purpose

This contract is the engineering gate after the source-resolution stop. It enables deterministic synthetic fixtures and validation without promoting unresolved Strategy A geometry into canonical logic.

## Allowed

- Deterministic synthetic OHLC candles.
- Explicit bullish/bearish fixture direction as fixture metadata only.
- Provenance references identifying why a fixture exists.
- Explicit status labels for unresolved executable geometry.
- Validation of OHLC invariants, candle ordering, unique indices, and provenance.
- Tests proving that fixtures cannot be mistaken for production trade decisions.

## Deliberately blocked

The following dimensions remain blocked pending a Tier-1/Tier-2 discriminator and manual source adjudication:

1. P-Gap exact candle pair/index and OHLC boundaries.
2. Entry price anchor.
3. Leg-2 start anchor.
4. Structural invalidation OHLC/wick/body boundary.
5. Pending-limit retain/replace threshold.
6. 1/2/3-candle trigger acceptance classifier.
7. AB=CD A/B/C/D anchors.
8. AB=CD equality tolerance.
9. 2X / TP1 / TP2 executable construction.
10. Deterministic bearish mirror.

## Non-goals

This contract does **not** define a P-Gap formula, Fibonacci rule, AB=CD tolerance, order-fill semantics, execution buffer, refresh threshold, target formula, or production BUY/SELL decision.

## Determinism requirements

- Candle indices are non-negative and unique.
- Candle order is explicit and deterministic.
- OHLC values satisfy `low <= open/close <= high`.
- Every fixture carries non-empty provenance.
- Every blocked executable geometry dimension is represented explicitly.
- Fixture objects are immutable (`frozen=True`).

## Source alignment

The contract follows the established source-resolution status: source semantics can be represented, but unresolved executable geometry must remain unresolved. Synthetic fixtures are therefore test scaffolding, not evidence that selects among competing geometry hypotheses.

## Gate status

`SYNTHETIC_FIXTURE_CONTRACT_READY`

This status means the fixture infrastructure is ready. It does **not** mean Strategy A geometry is frozen or production-ready.
