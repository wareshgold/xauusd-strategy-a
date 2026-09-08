# SP2L Entry / SL Semantic Lock — 2026-09-08

## Purpose

This checkpoint tightens the source meaning of the SP2L entry and stop semantics without inventing an executable price formula. It remains research-only.

## Primary-source evidence

### Entry

The official SP2L description states:

- bullish: wait for the corrective candle to reach the **low of the previous candle**;
- bearish: wait for the corrective candle to reach the **high of the previous candle**;
- entry is then taken in the direction of the spike.

The source video additionally describes placing the order manually or as a **pre-set limit** during that correction and explicitly shows a Buy Limit order in the entry diagram.

### Semantic lock

The following meaning is now sufficiently source-supported:

`Spike → correction → correction reaches prior-candle extreme → pending-limit execution in spike direction`

For research purposes:

- BUY correction reference = relevant prior-candle Low;
- SELL correction reference = relevant prior-candle High;
- execution mechanism = pending limit during correction, not a market close-reclaim substitute.

### Remaining entry uncertainty

The source does not provide a universal machine-readable definition for which candle is the "previous/relevant" candle across every spike construction, nor does it explicitly specify tick/buffer treatment around the level.

Therefore the following are **not frozen**:

- arbitrary buffer;
- body-vs-wick substitution;
- 50% retracement;
- classical harmonic C;
- close-reclaim execution;
- any tolerance chosen from backtest performance.

## Stop-loss

The official source states that SL is placed **behind the candle from which the spike originated**. The video diagram independently shows the SL on the opposite side of the spike-origin structure.

### Semantic lock

`SL reference = spike-origin candle`

This is stronger than a generic "recent swing" or "previous structure" rule and should be preserved as the source meaning.

### Remaining SL uncertainty

The exact executable price remains unresolved:

- wick extreme vs body boundary;
- exact side/offset;
- tick/buffer treatment;
- whether the origin candle identity changes across the source's multiple spike constructions.

No numeric buffer or fixed-point stop is authorized.

## Leg-1 boundary

Entry/SL semantics can be tightened without resolving the exact Leg-1 measurement. The source confirms that the second leg is intended to be approximately/effectively equal to the first leg and explicitly names AB=CD, while also contrasting the source's candle-level method with classical internet A/B/C/Fibonacci treatment.

Therefore:

- equal-leg relationship = source-confirmed concept;
- exact Leg-1 origin endpoint = unresolved;
- classical harmonic A/B/C anchors = forbidden import unless directly source-confirmed.

## Deterministic research contract

A research implementation may represent the source semantics as:

```text
BUY:
  correction reaches relevant prior Low
  -> pending Buy Limit is active during correction
  -> SL references the candle from which the spike originated

SELL:
  correction reaches relevant prior High
  -> pending Sell Limit is active during correction
  -> SL references the candle from which the spike originated
```

This contract intentionally leaves the unresolved geometric fields explicit rather than filling them with heuristics.

## Gate status

- SOURCE RESOLUTION: **advanced / semantic entry+SL meaning tightened**
- SYNTHETIC FIXTURES: **required for remaining price-anchor ambiguity**
- FROZEN GEOMETRY: **BLOCKED** by P-Gap formula, exact entry-price convention, exact SL price convention, and Leg-1 origin
- DEV: locked for canonical Strategy A
- VAL / HOLDOUT: locked
- PRODUCTION: unchanged

## Next highest-value source-resolution target

Resolve P-Gap boundary/timing first. In parallel, use discriminating fixtures to test whether the source's prior-candle entry level and origin-candle SL can be represented without hidden wick/body/buffer assumptions.
