# SP2L Leg-1 / AB=CD / 2X Resolution Gate — 2026-09-22

## Audit result

The archived implementation history contains a deterministic `LegProjection.ts`, but its formula is implementation-derived and cannot be promoted to source geometry.

The legacy projection uses:

- Leg 1 start = `spikeStartIndex`
- Leg 1 end = `spikeEndIndex`
- Leg 1 size = absolute difference between `last.close` and `first.open`
- projection origin = `correction.extremePrice`
- TP1 = projection origin ± Leg 1 size

This is **not source-confirmed** because the source does not uniquely establish those OHLC anchors.

## Source-confirmed layer

1. **AB=CD concept:** confirmed as a magnitude relationship: Leg 2 is expected to be approximately equal to Leg 1.
2. **2X concept:** confirmed as a second-position/reward-management concept.
3. The source contains half-target / second-position examples, but they do not establish one universal numeric 2X formula.
4. Exact A/B/C/D anchors remain unresolved.
5. Exact TP1/TP2 formulas remain unresolved.
6. AB=CD numerical tolerance remains unresolved.

## Explicit non-promotions

Do not canonicalize:

- `Leg1Size = spikeEnd.close - spikeStart.open`
- `projectionFrom = correctionExtreme`
- `C = Entry`
- `C = fill`
- `TP1 = C ± Leg1Size`
- any fixed Fibonacci extension
- any numerical AB=CD tolerance
- any universal 2X R-multiple

## Gate decision

No new canonical geometry can be justified from the currently archived evidence.

**Frozen Geometry: BLOCKED**

The next useful source discriminator is a teaching example where the first-leg endpoints, correction reference, and target/2X levels are simultaneously identifiable. Until that exists, implementation formulas remain research-only.

No production code was changed.
