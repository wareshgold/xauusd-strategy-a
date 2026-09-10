# SP2L G244 — B1 P-Gap source-resolution decision

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Decision class:** `B1_PGAP_SOURCE_RESOLUTION`  
**Status:** `PARTIAL_FREEZE__PRODUCTION_BLOCKED`

## 1. Purpose

This record converts the completed raw-source audits into a formal Strategy-A source-resolution boundary. It freezes only semantics supported by authoritative source evidence and explicitly preserves unresolved geometry as UNKNOWN.

No historical performance, optimization result, or implementation convenience is used to decide source meaning.

## 2. Evidence basis

Primary SP2L source video:

`/mnt/data/strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Same-author Gap course:

`/mnt/data/gap پورصمدی دوره جامع.mp4`

Supporting raw-source audit records:

- G234 — P-Gap endpoint mapping source pass
- G235 — cross-example positive P-Gap review
- G236 — rejected-example negative evidence
- G237 — B1 decision preparation
- G238 — synthetic fixture specification
- G239 — numeric research fixtures
- G240 — source-vs-fixture disambiguation
- G241 — raw-source P-Gap geometry resolution
- G242 — P-Gap endpoint measurement audit
- G243 — bearish mirror and event-timing audit

## 3. Frozen source meaning

### 3.1 P-Gap is a first-class validity condition

The source explicitly associates valid breakout/spike examples with P-Gap and rejects at least one sharp directional example that lacks the corresponding gap condition.

Therefore directional movement alone is insufficient to declare a valid P-Gap-qualified breakout.

### 3.2 Bullish endpoint semantics

The strongest repeated visual evidence shows the P-Gap vertical separation bounded by the full wick extrema of two endpoint candles surrounding the intervening directional/spike candle.

The source-correlated bullish endpoint construction is therefore frozen at the research semantic level as:

`earlier endpoint High` versus `later endpoint Low`

with the endpoint measurements interpreted as full candle extrema / wicks.

The leading executable relation is:

`High[t-2] < Low[t]`

This relation is **source-correlated and geometry-frozen only for the bullish endpoint orientation**. It is not authorization to implement a complete P-Gap production predicate.

## 4. Explicitly unresolved fields

The following remain UNKNOWN and are intentionally not guessed:

| Field | Status | Reason |
|---|---|---|
| Bullish equality | `UNKNOWN` | No source example establishes whether exact contact counts as a gap. |
| Bearish endpoint formula | `UNKNOWN / CANDIDATE` | Broader SP2L directionality is confirmed, but the reviewed raw material does not provide an independently measurable bearish P-Gap construction of equivalent strength. |
| Bearish equality | `UNKNOWN` | No direct source evidence. |
| Minimum gap distance | `UNKNOWN` | No numeric minimum is source-confirmed. |
| Spike magnitude/shape predicate | `UNKNOWN` | Source depicts a spike/directional candle but supplies no deterministic threshold/formula. |
| Event timing | `UNKNOWN` | Source does not freeze intrabar vs close-of-candle confirmation. |
| Horizontal/time extent of shaded P-Gap | `UNKNOWN` | Vertical price boundaries are clarified; exact temporal rectangle extent is not. |
| Breakout taxonomy requirements | `UNKNOWN` | `Valid BO = P-Gap` does not import all separate Breakout Gap taxonomy conditions. |

## 5. Candidate but non-canonical interpretations

The following are retained for research comparison only:

- bearish mathematical mirror: `Low[t-2] > High[t]`;
- equality-inclusive variants: `<=` / `>=`;
- any numeric minimum gap threshold;
- any deterministic spike-size or candle-shape threshold;
- any inferred close-based or intrabar timing rule;
- any equation equating P-Gap with FVG, generic three-candle imbalance, Pressure Gap, or Common Gap.

No candidate may be promoted solely because it improves backtest performance.

## 6. Implementation boundary

### Allowed now

- Preserve the frozen bullish endpoint semantics in the research/source ledger.
- Maintain synthetic fixtures that explicitly compare candidate interpretations.
- Test implementation infrastructure against fixtures without treating a candidate as canonical Strategy A.
- Continue source investigation for unresolved fields.

### Forbidden now

- Production P-Gap predicate using unresolved fields.
- Production BUY/SELL generation based on the candidate alone.
- Silent bearish mirroring by mathematical symmetry.
- Silent equality choice.
- Invented minimum-gap threshold.
- Invented spike threshold.
- Invented event timing.
- Replacing the source pending-limit mechanism with market-entry logic.
- Using historical profitability to decide which source interpretation is correct.

## 7. Gate status

- **SOURCE RESOLUTION:** `PASS_PARTIAL`
- **B1 P-Gap:** `PARTIAL_FREEZE`
- **SYNTHETIC FIXTURES:** `PASS`
- **FROZEN GEOMETRY:** `BLOCKED_FOR_FULL_STRATEGY`
- **DEV:** `BLOCKED`
- **UNTOUCHED VALIDATION:** `PROTECTED`
- **ROBUSTNESS/STABILITY:** `BLOCKED`
- **FRESH HOLDOUT:** `PROTECTED`
- **PRODUCTION:** `BLOCKED`

## 8. Required next work

1. Preserve this B1 decision as the authoritative boundary for P-Gap source meaning.
2. Continue source resolution for the unresolved bearish mirror and timing fields, but do not manufacture answers from symmetry or implementation convention.
3. Resolve the remaining independent Strategy-A geometry components (correction, pending-limit anchor/fill semantics, structural invalidation, AB=CD anchors/tolerance, and target semantics) before any full Strategy-A freeze.
4. Once all required geometry is source-resolved, build the complete deterministic specification and only then enter historical development validation.

## 9. Final decision

**B1 = PARTIALLY FROZEN.**

The bullish P-Gap endpoint semantics are sufficiently supported to freeze as source meaning: full wick extrema, with leading relation `High[t-2] < Low[t]`. All other unresolved fields remain explicitly UNKNOWN/CANDIDATE. This record does not authorize production trading logic.
