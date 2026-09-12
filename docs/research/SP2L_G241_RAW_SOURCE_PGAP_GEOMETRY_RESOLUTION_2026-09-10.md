# SP2L G241 — Raw-source P-Gap geometry resolution

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `STRONGER_SOURCE_EVIDENCE__GEOMETRY_STILL_NOT_FULLY_FROZEN`

## Objective

Re-examine the raw SP2L video at the strongest P-Gap teaching sections to determine whether the source itself resolves the executable geometry of P-Gap. This pass is source-only: no historical performance, optimization, or fixture results are used to select the meaning.

## Raw source reviewed

Primary source video:

`/mnt/data/strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Relevant raw-video regions reviewed in this pass:

- approximately 31:00–32:10: construction/teaching sequence;
- approximately 35:50–36:16: positive and negative P-Gap examples;
- approximately 36:07: explicit `Valid BO = P-Gap` example panel.

## Direct visual observations

### 1. Teaching construction around 31:00–32:10

The strongest construction frame sequence repeatedly shows:

`earlier/small candle → large directional/spike candle → later/small candle → continuation`

At approximately 31:24–31:30, the author visually circles the earlier candle and the later/small candle, with the large directional candle between them. The intervening candle is the visually dominant spike.

The later frame around 31:50–32:00 labels the construction `P-GAP`.

This is strong direct evidence that the P-Gap construction is associated with the separation between the earlier and later endpoint candles, not simply with the spike candle in isolation.

### 2. Endpoint relationship

The reviewed teaching sequence is visually compatible with the same-author Gap-course relation:

`High[t-2] < Low[t]`

for the bullish orientation, where the intervening candle is the spike/directional candle.

This is stronger than a generic visual resemblance because the author specifically marks the first and third candles as the relevant endpoints while the middle candle is the spike.

However, the source frame does not provide sufficiently explicit verbal or numerical annotation to prove whether the intended endpoint uses wick extrema or candle bodies as a universal rule.

### 3. Positive/negative example panel

The approximately 35:50–36:16 panel contains a rejected directional example and multiple accepted examples. The rejected example is marked with a red X, while the accepted examples are associated with shaded P-Gap regions and the explicit text:

`Valid BO = P-Gap`

The accepted examples consistently show a directional/spike construction together with a visibly separated endpoint region. This provides qualitative negative evidence against interpreting every sharp directional move as P-Gap.

### 4. P-Gap is distinct from Common Gap

Earlier raw SP2L teaching material separately labels:

`P-GAP`

and

`GAP / Common`

Therefore P-Gap must not be collapsed into the generic/Common Gap label, even though the same-author generic Gap-course geometry is strongly compatible with the observed P-Gap endpoint construction.

### 5. Pressure Gap remains separate

The separate Gap course defines Pressure Gap as a taxonomy/context concept involving a trend that has persisted for roughly 10–30 candles before pressure stops and a trend bar appears. No reviewed SP2L evidence equates that taxonomy with the P-Gap label.

Therefore `P-Gap = Pressure Gap` remains unsupported and must not enter Strategy A.

## Geometry resolution matrix

| Question | Raw-source result | Decision |
|---|---|---|
| Are two endpoint candles involved? | Yes; author visibly marks earlier and later candles around the spike | **Strongly supported** |
| Is one intervening directional/spike candle present? | Yes in the reviewed construction | **Strongly supported** |
| Is a gap/separation required? | Accepted examples show separated/shaded P-Gap construction; rejected sharp move lacks qualifying separation | **Strongly supported qualitatively** |
| Is bullish endpoint relation compatible with `High[t-2] < Low[t]`? | Yes, strongly compatible | **Leading candidate** |
| Wick extrema or candle bodies? | Not explicitly resolved by source wording/visual precision | **UNKNOWN** |
| Strict `<` or inclusive `<=`? | No controlled equality/touch example | **UNKNOWN** |
| Minimum gap distance? | None explicitly stated | **UNKNOWN** |
| Numeric spike threshold? | None explicitly stated | **UNKNOWN** |
| Is spike a mandatory logical predicate? | Construction consistently depicts it, but no executable threshold/rule is stated | **UNKNOWN / candidate conjunction** |
| Is Breakout Gap taxonomy mandatory? | P-Gap is associated with valid breakout, but the separate taxonomy conditions are not explicitly imported | **UNKNOWN** |
| Is P-Gap Pressure Gap? | No authoritative evidence | **REJECTED as interpretation** |
| Exact bearish mirror? | Not resolved in reviewed material | **UNKNOWN** |
| Exact shaded-zone boundaries? | Visually suggest endpoint separation but are not numerically defined | **UNKNOWN** |
| Exact event timing? | Not explicitly frozen | **UNKNOWN** |

## Source-resolution conclusion

G241 materially strengthens the source case for the following research-level interpretation:

> **Bullish P-Gap is strongly correlated with the separation between the earlier endpoint candle and the later endpoint candle surrounding an intervening directional/spike candle; `High[t-2] < Low[t]` is the leading source-correlated geometric candidate.**

But this pass does **not** justify a full canonical freeze because the source still does not explicitly resolve wick/body semantics, equality handling, minimum distance, numeric spike criteria, exact region boundaries, or all timing/mirror details.

The project therefore remains deliberately conservative:

`P-GAP_GEOMETRY = NOT_FULLY_FROZEN`

`LEADING_BULLISH_CANDIDATE = High[t-2] < Low[t]`

`PRODUCTION_PREDICATE = BLOCKED`

## Gate decision

- **Source Resolution:** improved substantially; still partially blocked.
- **Synthetic Fixtures:** PASS.
- **Frozen Geometry:** **BLOCKED**.
- **DEV historical optimization:** **BLOCKED** for P-Gap geometry selection.
- **Untouched Validation:** protected.
- **Fresh Holdout:** protected.
- **Production BUY/SELL:** blocked.

## Next decision point

The next formal step should not introduce additional arbitrary thresholds. Instead, either:

1. locate an even more explicit source segment where the author defines the exact P-Gap boundary/measurement; or
2. record a formal B1 source-resolution decision that freezes only what the source truly supports and leaves the remaining fields as explicit `UNKNOWN` values.

No production Strategy A code is authorized from this record alone.
