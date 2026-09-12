# G341 — AB=CD competing-model synthetic research

Date: 2026-09-12  
Branch: `research/sp2l-g341-abcd-competing-model-synthetic-2026-09-12`

## Purpose

Represent the unresolved executable AB=CD geometry as explicit competing deterministic research hypotheses, using synthetic fixtures only. This gate must not select a canonical A/B/C/D interpretation and must not use historical profitability to resolve source meaning.

## Source boundary inherited from G340

The source supports the semantic relationship **AB = CD / Leg 2 approximately equal to Leg 1**, a parent/deeper leg, a correction, and a pending-limit execution during the correction. The source does not yet provide an executable candle-level definition for the exact A/B/C/D OHLC fields, wick/body choice, AB=CD tolerance, or TP1/TP2 mapping.

Therefore this gate treats the following as research dimensions:

1. **A/B event selection** — source deep-leg origin, first breakout candle, or nearest-swing style candidate.
2. **Price field** — high, low, open, close, or body-derived field.
3. **C selection** — source correction reference versus the explicitly rejected `fill_as_C` hypothesis.
4. **Scale** — parent versus nested structural leg.
5. **D projection family** — deterministic translation of the signed AB price delta from C, used only as a representation of the source AB=CD semantic relation, not as a frozen production formula.

No tolerance is represented.

## Synthetic fixture design

`G341_SOURCE_SEMANTIC_FIXTURE` deliberately separates:

`range → deep origin → breakout → parent B → nested B → nearby swing → correction → pending → fill → Leg 2 end`

The fixture is adversarial by construction: different candidate selectors and price fields resolve to different A/B/C anchors and therefore different D projections.

This proves that an implementation could silently change Strategy A meaning if it hard-coded a convenient swing, fill, wick/body, or scale interpretation.

## Guardrails

- Every G341 model is explicitly `canonical: false`.
- `fill_as_C` is represented only to demonstrate divergence and is not promoted.
- Parent and nested scale remain distinct hypotheses.
- Wick/body semantics remain unresolved.
- No historical data is used.
- No parameter optimization is performed.
- No production namespace is modified.
- No AB=CD tolerance is invented.
- No TP1/TP2 numeric mapping is invented.

## Test expectations

The G341 test suite must demonstrate:

- all competing models remain non-canonical;
- competing anchors generate different D projections;
- fill remains distinct from the source correction reference;
- parent and nested scale produce divergent results;
- price-field choices produce divergent results;
- the projection is an explicit AB-delta translation with no tolerance parameter.

## Gate result

**G341 = PASS — COMPETING MODELS REPRESENTED, GEOMETRY UNRESOLVED**

This does **not** open FROZEN_GEOMETRY or DEV. The historical validation gates remain blocked.

## Next authorized step

Either:

1. acquire additional authoritative source material that explicitly resolves the executable anchors; or
2. continue synthetic discrimination of the unresolved model dimensions without selecting a canonical model.

Historical optimization, live signals, and production promotion remain unauthorized until the source geometry is frozen and all required validation gates are passed.
