# SP2L G220 — Gap Course Source Pass

Date: 2026-09-10
Status: RESEARCH-ONLY / SOURCE RESOLUTION SUPPORT

## Objective

Assess whether the uploaded PourSamadi comprehensive trading-course video provides source evidence that can disambiguate the meaning of **Gap** terminology relevant to SP2L, especially the distinction between generic gaps and the SP2L **P-Gap**.

This pass does **not** freeze P-Gap geometry and does not modify production logic.

## Asset provenance

Uploaded asset:
`gap پورصمدی دوره جامع.mp4`

Measured local properties:
- duration: approximately 1955.77 s (32:35.77)
- video: 854x480
- frame rate: 30 fps
- frame count: 58,673
- SHA-256: `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`

Frame convention for this asset: nominal zero-based frame ~= round(t * 30).

## Direct visual observations

### 1. Course section explicitly titled PriceAction (Gaps)

The video opens with a slide titled `PriceAction (Gaps)`. This is strong evidence that the asset is specifically about gap concepts rather than a generic unrelated trading lesson.

### 2. Early chart walkthroughs distinguish gap-related price behavior

During the first approximately ten minutes, the instructor repeatedly annotates chart examples and progressively marks gap regions, including examples around market-open movement and subsequent price behavior.

### 3. Explicit market-open gap section

Around 09:00, the chart is explicitly titled in Persian:
`شکاف های بزرگ در شروع بازار`
(large gaps at the start/open of the market).

The instructor marks the large opening discontinuity and discusses it as a gap phenomenon. This is useful evidence that a market-open gap is a distinct context/type in the course material.

### 4. Gap labels/annotations are source evidence, not executable geometry

Several frames contain handwritten `GAP` annotations and additional notation. Some handwritten notation is not sufficiently legible at the source resolution to be transcribed safely. No numeric rule is promoted from visual handwriting alone.

## Relevance to SP2L P-Gap

This asset is valuable because it establishes that PourSamadi treats **Gap** as a differentiated price-action concept and discusses at least a market-open/large-gap class explicitly.

However, this pass has **not yet established** that the course's generic Gap definition is identical to SP2L's P-Gap definition. In particular, the following remain unresolved:

- exact P-Gap participating candles;
- exact OHLC/range boundaries;
- whether wick or body is authoritative;
- overlap/non-overlap requirements;
- directional/bullish/bearish mirror formula;
- whether a market-open gap is P-Gap, merely one gap type, or a separate category;
- any minimum-size threshold;
- exact relationship between the course Gap taxonomy and the SP2L `Valid BO = P-Gap` rule.

## Source-first conclusion

**Decision: USEFUL SOURCE-CORROBORATION — FURTHER TARGETED PASS REQUIRED.**

The uploaded course should be treated as a high-value secondary source from the same creator for terminology disambiguation. It must not be used to invent or overwrite SP2L P-Gap geometry unless an explicit statement or unambiguous source example links the course definition to the SP2L P-Gap.

## Next targeted pass

Search this video specifically for:
1. an explicit definition of `P-Gap` / `PGAP`;
2. any spoken or written comparison of multiple Gap types;
3. examples where the instructor labels the same gap as P-Gap;
4. any candle-by-candle explanation of the gap boundaries;
5. any statement connecting Gap terminology to breakout validity.

If such evidence is found, create a separate evidence record and cross-reference the SP2L raw-video frames around 30:00–36:16 where `P-GAP` and `Valid BO = P-Gap` are explicitly shown.

## Gate impact

- Source Resolution: **still BLOCKED at executable P-Gap geometry**
- Frozen Geometry: **still BLOCKED**
- Research/production separation: **preserved**
- No production rule changed
- No backtest result used to interpret source meaning
