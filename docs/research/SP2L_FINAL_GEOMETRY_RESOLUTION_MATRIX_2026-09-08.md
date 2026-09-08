# SP2L Final Geometry Resolution Matrix — 2026-09-08

## Purpose

This pass evaluates whether the remaining Strategy A geometry can be frozen independently, without allowing an unresolved P-Gap interpretation or profitable backtest to determine source meaning.

Authoritative order remains:

1. raw source video/transcript;
2. source visual evidence;
3. source ledger / meaning map;
4. deterministic specification;
5. implementation;
6. historical performance.

The public TradingView indicator is secondary corroboration only. Its protected implementation cannot establish canonical source geometry.

## Resolution matrix

| Component | Source semantic | Strongest candidate | Exact deterministic geometry | Gate |
|---|---|---|---|---|
| Spike | strong directional movement after range/breakout | source-defined directional sequence | exact candle taxonomy still open across variants | PARTIAL |
| Breakout | close beyond prior level + follow-through / key bar | source-described breakout sequence | exact prior-level construction still open | PARTIAL |
| P-Gap | breakout-associated gap/non-overlap; valid BO = P-Gap | wick-range non-overlap is strongest candidate | exact boundaries, timing, equality, minimum gap unresolved | BLOCKER |
| Entry direction | trade in direction of Spike | BUY after bullish / SELL after bearish correction | deterministic | SOURCE-CONFIRMED |
| Entry reference side | bullish correction reaches prior Low; bearish reaches prior High | immediate/relevant previous candle extreme | exact relevant-candle identity across all variants unresolved | PARTIAL |
| Entry execution | pending/manual pre-set limit during correction | pending limit at source-defined correction level | exact executable price/buffer unresolved | PARTIAL |
| SL semantic | invalidation beyond spike-origin candle | BUY below origin low / SELL above origin high | wick/body, strictness, buffer, tick semantics unresolved | PARTIAL |
| Leg 1 | first-leg / Spike magnitude | Spike-origin → Spike-extreme | exact OHLC anchor unresolved | PARTIAL |
| Leg 2 | second leg approximately/equally matches Leg 1; AB=CD named | equal magnitude to resolved Leg 1 | exact correction anchor and tolerance unresolved | PARTIAL |
| TP | source example favors TP1 / 1:1 | base 1R | exact module relation to 2X/TP2 requires separate resolution | PARTIAL |

## What can be frozen now

The following are safe semantic contracts and may be treated as source-confirmed meaning, but they are not sufficient to unlock Frozen Geometry:

### Entry semantic contract

`Spike direction → correction → relevant prior candle extreme → pending-limit execution in Spike direction`

BUY uses the relevant prior Low; SELL uses the relevant prior High.

Do not silently convert this to:

- market close-reclaim;
- P-Gap boundary entry;
- FVG midpoint;
- classical harmonic C;
- fixed 50% retracement.

### Structural invalidation semantic contract

`Invalidation is structurally beyond the candle from which the Spike originated.`

No numeric price offset is implied by this contract.

### Equal-leg semantic contract

`Source-defined second leg targets a magnitude approximately/equally matching the source-defined first leg.`

The source's candle-level treatment must not be replaced by imported classical A/B/C/D Fibonacci geometry.

## What cannot be frozen yet

### P-Gap

The source visuals distinguish a valid breakout-associated P-Gap from rejected/non-valid constructions, but do not expose enough precision to choose uniquely among:

- previous High → next Low wick-range gap;
- body-top → body-bottom gap;
- other wick/body boundary combinations;
- equality/touch handling;
- minimum gap size;
- exact candle timing.

The three accepted-looking visual variants also show that P-Gap timing is relational to the breakout/sequence, not safely representable as a universal fixed candle index.

### Entry candle identity

The source wording strongly supports the previous-candle Low/High concept. The video also describes the first low/high in the correction sequence. These observations are compatible but do not prove a single universal candle index across all Spike variants.

Therefore `previous candle` remains the semantic reference, while `relevant candle index` remains unresolved.

### SL executable price

The origin-candle semantic is strong. Exact wick/body selection, at-touch vs strictly beyond, spread/tick handling, and any buffer are unresolved.

### Leg 1 and AB=CD

The source explicitly contrasts its candle-level approach with classical internet A/B/C/Fibonacci treatment. Therefore no classical harmonic anchors may be imported. The strongest candidate is Spike-origin → Spike-extreme, but exact OHLC anchors and AB=CD tolerance remain unresolved.

## Synthetic discriminator status

The following discriminator families are now required before a full geometry freeze:

- `PGAP-B01..B08`: wick/body boundary, equality, timing, and gap-vs-breakout separation;
- `ENTRY-B01..B06`: immediate previous candle vs first correction candle vs source-defined relevant candle;
- `SL-B01..B04`: origin wick/body and strict invalidation semantics;
- `LEG-B01..B06`: origin/extreme wick/body and competing origin candidates;
- `ABCD-B01..B04`: exact equality, near-equality, and no-invented tolerance.

A discriminator is valid only if competing interpretations produce different outputs. If outputs are identical, the fixture does not resolve the ambiguity.

## External TradingView evidence boundary

The public TradingView description corroborates several semantic concepts: Spike, gap/FVG filtering, previous Low/High entry structure, SL behind the Spike-origin candle, and TP1/TP2 concepts. Because the script is protected and third-party, these claims remain corroboration and hypothesis-generation material, not canonical source definitions.

In particular:

`TradingView FVG terminology != proof that source P-Gap is generic FVG.`

## Gate decision

**SOURCE RESOLUTION:** materially advanced.

**SEMANTIC LOCK:** partial; Entry direction/execution semantics, structural SL semantics, and equal-leg semantic are stable.

**FROZEN GEOMETRY:** **BLOCKED**.

Primary blocker: exact P-Gap geometry/timing.

Secondary blockers: exact Entry candle identity/price, exact SL executable price, exact Leg-1 OHLC anchors, AB=CD tolerance, and target-module relation.

**DEV:** locked.

**UNTOUCHED VAL:** locked.

**ROBUSTNESS/STABILITY:** locked.

**FRESH HOLDOUT:** untouched.

**PRODUCTION:** unchanged.

## Next multi-stage resolution batch

1. Finish P-Gap boundary/timing discrimination from the highest-information source frames.
2. Resolve Entry candle identity using the same accepted Spike variants and bearish mirror.
3. Resolve SL price convention independently of P-Gap.
4. Re-test Leg-1 origin candidates after Entry/SL anchors are fixed.
5. Resolve AB=CD equality/tolerance only from source evidence; do not optimize it.
6. Only after all geometry is source-frozen, generate the canonical deterministic specification and unlock DEV validation.
