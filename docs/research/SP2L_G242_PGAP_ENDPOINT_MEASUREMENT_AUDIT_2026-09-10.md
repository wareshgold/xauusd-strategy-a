# SP2L G242 — P-Gap endpoint measurement audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `BULLISH_ENDPOINT_GEOMETRY_STRONGLY_SUPPORTED__FULL_CANONICAL_FREEZE_BLOCKED`

## Objective

Audit the highest-value raw SP2L visual frames to determine whether the P-Gap shaded region is bounded by candle wick extrema or candle bodies. This is a source-only audit. No historical performance, optimization, or fixture results are used to select the interpretation.

## Source frames reviewed

Primary SP2L source video:

`/mnt/data/strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Key extracted frames reviewed:

- approximately 31:24–31:40: construction sequence where the author marks the earlier and later endpoint candles around the spike;
- approximately 35:50–36:00: positive/negative P-Gap panel;
- approximately 36:00–36:16: multiple positive examples with shaded P-Gap regions and `Valid BO = P-Gap`.

## Measurement audit

### 1. Construction sequence

The teaching sequence shows three relevant candles in order:

`endpoint A → large directional/spike candle → endpoint B`

The author separately circles/marks the first and third candles. This establishes the endpoint-candle relationship independently of the later shaded-region examples.

### 2. Positive example 1

The first accepted example contains a small earlier candle, a large bullish directional candle, and a later smaller candle. The shaded P-Gap region is vertically positioned between the upper extreme of the earlier endpoint candle and the lower extreme of the later endpoint candle.

The visible wicks are important: the shaded region reaches the level of the earlier candle's upper wick and the level of the later candle's lower wick rather than being confined to the candle bodies.

This is direct visual evidence favoring full-extrema / wick-to-wick endpoint geometry.

### 3. Positive examples 2 and 3

The additional accepted examples show the same construction: an earlier endpoint, a large directional candle, and a later endpoint, with the shaded P-Gap region occupying the separation between the relevant endpoint extremes.

Across the examples, the shaded region is visually consistent with:

`earlier High` → `later Low`

for bullish orientation.

The repeated geometry is materially stronger than a single-example visual estimate because the same relationship is reproduced across multiple accepted examples.

### 4. Negative example

The rejected example is a sharp directional movement without the corresponding endpoint separation. It is marked with a red X and therefore provides negative evidence against treating directional movement alone as P-Gap.

This remains consistent with the source statement `Valid BO = P-Gap` shown beside the accepted examples.

## Geometry comparison

| Candidate | Source-frame result | Decision |
|---|---|---|
| Full extrema / wick-to-wick | Matches the visible upper extreme of earlier endpoint to lower extreme of later endpoint across accepted examples | **Strongly supported** |
| Body-to-body only | Not required by the visible shaded-region boundaries; bodies do not explain the observed wick-aligned limits as well | **Not source-preferred** |
| Generic three-candle directional move without gap | Contradicted by rejected directional example | **Rejected** |
| Bullish strict endpoint relation `High[t-2] < Low[t]` | Consistent with the source geometry and same-author Gap-course wording | **Leading executable candidate** |
| Bullish inclusive `High[t-2] <= Low[t]` | No equality/touch example in the source | **UNKNOWN** |

## What is now resolved more strongly

The combined raw-source evidence supports the following research-level meaning:

> **For the bullish construction, the P-Gap separation is bounded by the upper extreme (High) of the earlier endpoint candle and the lower extreme (Low) of the later endpoint candle, with one intervening directional/spike candle.**

Therefore the source-correlated bullish geometric candidate can now be stated more precisely as:

`High[t-2] < Low[t]`

with the endpoint measurements interpreted as full candle extrema / wicks.

This is a substantially stronger conclusion than G241 because the shaded regions in the accepted examples visually align with wick extrema rather than merely showing an abstract separation.

## Remaining unresolved fields

The following must still remain UNKNOWN unless direct source evidence resolves them:

1. **Equality handling:** strict `<` versus inclusive `<=`.
2. **Minimum gap distance:** no numeric minimum is stated.
3. **Spike predicate:** the source clearly depicts a directional/spike candle, but no deterministic magnitude/shape threshold is supplied.
4. **Bearish mirror:** a bearish P-Gap is expected by directional symmetry, but the exact source-confirmed executable mirror has not yet been independently established.
5. **Event timing:** the exact candle-close/intrabar moment at which P-Gap becomes valid is not frozen.
6. **Breakout taxonomy:** `Valid BO = P-Gap` does not by itself import every separate Breakout Gap taxonomy condition.
7. **Shaded horizontal extent:** the vertical price boundaries are substantially clarified; exact horizontal/temporal extent remains unresolved.

## Important non-conclusions

This audit does **not** establish any of the following:

- P-Gap = generic FVG;
- P-Gap = Pressure Gap;
- P-Gap requires a particular three-candle body formula;
- a minimum pip/point threshold;
- a specific spike-size threshold;
- a market-entry substitute for the source's pending-limit mechanism.

## Gate decision

- **Source Resolution:** `PASS_PARTIAL` for bullish endpoint geometry.
- **Bullish wick/body semantics:** `STRONGLY_SUPPORTED = WICK_EXTREMA`.
- **Bullish endpoint relation:** `LEADING = High[t-2] < Low[t]`.
- **Full canonical P-Gap geometry:** **BLOCKED** until equality, spike predicate, timing, and bearish mirror are resolved or explicitly frozen as UNKNOWN by a formal B1 decision.
- **Synthetic Fixtures:** PASS; existing fixture hypotheses remain useful.
- **Historical DEV selection:** BLOCKED for unresolved fields.
- **Untouched Validation:** protected.
- **Fresh Holdout:** protected.
- **Production BUY/SELL:** BLOCKED.

## Next action

Proceed to a formal **B1 source-resolution decision** for P-Gap geometry, freezing only the source-confirmed bullish endpoint semantics and explicitly enumerating the unresolved fields. Before any historical optimization, independently resolve or document the bearish mirror and execution timing. No production predicate should be promoted from this audit alone.
