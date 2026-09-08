# SP2L Semantic Contract Freeze — 2026-09-08

## Purpose

This document freezes the source-aligned semantic meaning of Strategy A / SP2L without inventing unresolved executable OHLC geometry.

It is a **semantic contract**, not a production execution specification. The contract is allowed to contain unresolved geometry placeholders. Any implementation that requires one of those placeholders must stop or be explicitly labelled as a research hypothesis.

## Evidence hierarchy

1. Raw authoritative source material
2. Source visual evidence / extracted chart frames
3. Source ledger and semantic meaning map
4. This frozen semantic contract
5. Deterministic implementation
6. Historical performance research

Historical profitability must never be used to decide what the source means.

## Frozen semantic sequence

`Context / range → valid breakout with P-Gap → directional Spike → correction → pending-limit entry → structural invalidation → second leg continuation`

The source explicitly names the framework **SP2L = Spike → 2 Leg** and explicitly connects the second leg to an **AB = CD / equal-magnitude** relationship.

## Canonical semantic rules

### S1 — Context / range

A Spike is discussed in relation to a preceding range/context. The exact deterministic range definition is not frozen here.

Status: **SOURCE-CONFIRMED SEMANTIC; GEOMETRY UNRESOLVED**

### S2 — Valid breakout / P-Gap

A valid Spike requires the source-defined P-Gap associated with the breakout. A sharp directional movement without the required gap is not canonical SP2L.

Status: **SOURCE-CONFIRMED**

Hard boundary: P-Gap must not be implemented as a generic three-candle FVG unless first-party evidence later proves equivalence.

Unresolved:
- exact OHLC boundary;
- exact candle timing across the source's Spike variants;
- minimum gap/touch/equality convention.

### S3 — Spike

Spike is a strong/sharp directional market movement following the relevant context/breakout structure. The source presents multiple candle-level Spike constructions and treats the variants as belonging to the same Spike concept.

Status: **SOURCE-CONFIRMED SEMANTIC**

Hard boundary: no fixed candle count, body percentage, ATR threshold, displacement threshold, or generic swing algorithm is canonical unless separately source-confirmed.

### S4 — Correction

After the first directional movement, the market is expected to correct. The source describes the correction reference at candle level:
- bullish: correction reaches the Low of the previous/relevant candle;
- bearish: correction reaches the High of the previous/relevant candle.

Status: **SOURCE-CONFIRMED SEMANTIC**

The exact candle index for every Spike variant is not uniquely frozen.

### S5 — Entry

Entry is in the direction of the Spike and is placed during the correction as a **pending/manual limit order**. The source explicitly demonstrates pre-set Buy Limit / Sell Limit style placement and explains that the order can be prepared before activation.

Status: **SOURCE-CONFIRMED**

Hard boundaries:
- do not replace pending-limit entry with a market close-reclaim rule;
- do not define Entry as the P-Gap boundary;
- do not define Entry as classical harmonic point C;
- do not promote a 50% retracement rule to the base entry.

Unresolved:
- exact executable Entry price anchor;
- universal candle index across variants;
- cancellation/replacement semantics in all cases.

### S6 — Structural invalidation / SL

Stop/invalidation is structurally tied to the candle/structure from which the Spike originated. Bullish invalidation is below that origin structure; bearish invalidation is above it.

Status: **SOURCE-CONFIRMED SEMANTIC**

Unresolved:
- exact wick/body convention;
- exact origin candle identity across all variants;
- numeric buffer/offset;
- exact intrabar fill semantics.

### S7 — Leg 1

The first directional Spike movement supplies the first-leg magnitude used for the second-leg concept.

Status: **SOURCE-CONFIRMED SEMANTIC**

Current strongest research candidate for exact geometry is `Spike-origin → Spike-extreme`, but this is **not frozen**. Competing candidates remain possible until source evidence discriminates them.

### S8 — Leg 2 / AB = CD

The source explicitly teaches that after correction, the next leg is expected to have the same magnitude as the first leg and labels the relationship **AB = CD**.

Status: **SOURCE-CONFIRMED SEMANTIC**

Hard boundary: classical internet harmonic A/B/C/Fibonacci construction is not imported into Strategy A merely because the phrase AB=CD is used.

Unresolved:
- exact Leg-1 anchors;
- exact projection anchor after correction;
- tolerance for practical equality.

### S9 — Base target

The source teaches a base TP of **1:1** for this strategy. A larger TP2 is discussed as an optional/secondary management target rather than the frozen base target.

Status: **SOURCE-CONFIRMED**

### S10 — Direction symmetry

The semantic structure is mirrored:
- BUY: bullish Spike, correction toward relevant Low, invalidation below origin, second leg upward.
- SELL: bearish Spike, correction toward relevant High, invalidation above origin, second leg downward.

Status: **SOURCE-CONFIRMED SEMANTIC**

## Explicitly non-canonical imports

The following are not Strategy A rules unless future first-party evidence establishes them:

- generic FVG = P-Gap;
- liquidity sweep;
- BOS / MSS;
- displacement;
- generic retest;
- market close-reclaim as entry substitute;
- fixed Spike candle count;
- 65% body threshold;
- ATR/average-based Spike threshold;
- Fibonacci retracement requirement;
- classical harmonic A/B/C/D anchor mapping;
- arbitrary AB=CD tolerance;
- arbitrary tick/pip SL buffer;
- session filter chosen for backtest performance;
- any threshold selected because it improves historical results.

## Gate status

| Gate | Status |
|---|---|
| SOURCE RESOLUTION | **SEMANTIC CONTRACT FROZEN** |
| SYNTHETIC FIXTURES | **OPEN — semantic fixtures permitted** |
| FROZEN GEOMETRY | **BLOCKED** |
| DEV | **LOCKED** |
| UNTOUCHED VAL | **LOCKED** |
| ROBUSTNESS / STABILITY | **LOCKED** |
| FRESH HOLDOUT | **LOCKED** |
| PRODUCTION | **UNCHANGED / LOCKED** |

## Promotion rule

No executable rule may be promoted to canonical Strategy A solely because it passes synthetic tests or produces profitable historical results. A geometry rule becomes canonical only after first-party source evidence resolves it and the deterministic specification is frozen.

## Required next evidence to unblock geometry

At least one new first-party artifact should discriminate the remaining questions, such as:

- an annotated source chart with readable OHLC anchors;
- an official/open indicator or template exposing the geometry;
- a source worksheet/training document defining the exact candle relationship;
- a source example where competing geometric interpretations produce different entry/SL/Leg-1 prices and the instructor's chosen price is observable.

Until such evidence exists, research may compare hypotheses, but production and canonical backtesting remain locked.

## Provenance

Primary source artifact: uploaded SP2L source video, SHA-256 `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`.

Supporting source-resolution record: `docs/research/SP2L_SOURCE_ARTIFACT_FINAL_SEARCH_2026-09-08.md`.

This document supersedes no source evidence; it freezes the current semantic interpretation and explicitly records uncertainty.
