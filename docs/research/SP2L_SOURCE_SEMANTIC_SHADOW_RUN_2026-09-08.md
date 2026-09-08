# SP2L Source-Semantic Shadow Run — Impact Assessment

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Mode:** RESEARCH ONLY / NO PRODUCTION CHANGE

## 1. Objective

Measure the immediate effect of source alignment against the existing Strategy A baseline without inventing unresolved P-Gap or AB=CD geometry.

The comparison is intentionally conservative: a baseline trade may be classified as **SOURCE-BLOCKED** when a required canonical geometric fact is unresolved. SOURCE-BLOCKED does **not** mean the source says the trade is invalid. It means the repository cannot yet reproduce the source rule deterministically.

## 2. Existing baseline reference

The current baseline implementation uses heuristic Spike detection, a generic research pipeline, correction detection, a close-reclaim entry trigger, candidate Leg-2 projection, and context/quality filters. The baseline runner explicitly calls these components and produces 1M and 5M reports.

Reference implementation:
`src/domain/strategy-a/SpikeDetector.ts`  
`src/domain/strategy-a/CorrectionDetector.ts`  
`src/domain/strategy-a/EntryTrigger.ts`  
`src/domain/strategy-a/LegProjection.ts`  
`scripts/run-baseline-backtest.ts`

The current entry trigger is explicitly `CORRECTION_EXTREME_RECLAIM` and uses a later candle close as the entry price. This is not source-canonical.

## 3. Baseline snapshot

| Timeframe | Candles | Baseline trades | Win rate | Avg/Expectancy R | Profit factor | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| 1M | 10,000 | 338 | 28.40% | +0.121R | 1.169 | 101.45R |
| 5M | 10,000 | 241 | 32.37% | -0.105R | 0.844 | 36.70R |

Dataset provenance in the existing reports is Twelve Data (`twelvedata`). The 1M report covers 2026-08-20 13:05 through 2026-08-27 11:44; the 5M report covers 2026-07-23 18:25 through 2026-08-27 11:40.

These numbers are a baseline reference only. They are not a validated Strategy A result.

## 4. Source-semantic shadow classification

A canonical SP2L candidate currently requires source-confirmed evidence for:

1. Spike/breakout semantics;
2. P-Gap;
3. correction sequence;
4. pending-limit entry;
5. structural invalidation;
6. source-confirmed Leg-1 / AB=CD geometry;
7. executable target semantics.

The recovered source resolves the semantic chain but does not yet resolve the executable geometry for P-Gap or A/B/C/D. Therefore the shadow engine must not convert a baseline candidate into a canonical BUY/SELL trade solely from its existing coordinates.

### Current classification rule

For research accounting only:

- `SOURCE-SEMANTIC-COMPATIBLE`: the baseline event is compatible with concepts explicitly supported by the source, but no canonical trade is emitted.
- `SOURCE-BLOCKED-GEOMETRY`: a canonical decision would require unresolved P-Gap/A-B-C-D/fill/target geometry.
- `SOURCE-CONTRADICTED`: the baseline decision relies on a behavior explicitly inconsistent with the source, such as using a market close-reclaim as the canonical entry instead of a pending limit.

No baseline result is relabeled as a source-valid trade merely because it was profitable.

## 5. Immediate impact on the existing output

### Entry logic

Every baseline candidate whose actual decision depends on `CORRECTION_EXTREME_RECLAIM` cannot be promoted unchanged. The source explicitly demonstrates a pre-placed Buy Limit during correction; therefore the baseline close-reclaim entry is **SOURCE-CONTRADICTED AS CANONICAL ENTRY SEMANTICS**.

This can change:

- whether an order is ever filled;
- fill timestamp;
- fill price;
- risk distance;
- R multiple;
- subsequent target/stop outcome.

The old trade result must therefore not be reused after entry semantics are corrected.

### P-Gap

The generic three-candle imbalance cannot be promoted to P-Gap. A baseline candidate that depends on that generic detector is therefore **SOURCE-BLOCKED-GEOMETRY**, not source-invalid.

### Leg 1 / AB=CD

The source confirms the AB=CD concept, but the executable A/B/C/D anchors and tolerance are unresolved. Any baseline Leg-2 projection based on heuristic spike start/end or correction extreme is therefore not reusable as canonical target geometry.

### Target

The source supports a 1:1 target concept, while the source material also distinguishes TP1/TP2 and 2X. The baseline projection cannot be assumed to be the same as the source target module.

## 6. Quantitative interpretation of the baseline numbers

The baseline currently reports 338 trades on 1M and 241 trades on 5M. These counts must be treated as **upper-bound research populations for the current heuristic implementation**, not expected canonical trade counts.

Because the source-aligned entry is pending-limit based and P-Gap/A-B-C-D geometry remains unresolved, the final canonical trade population can only be measured after those geometries are frozen and replayed with the exact same dataset.

A particularly important warning is the baseline R distribution: the existing report contains trades with very small risk distances and correspondingly large R outcomes. For example, the 5M report contains a trade with approximately 0.214 price-unit risk and +8.59R. This makes mean R sensitive to outliers and reinforces the requirement to report median R and excursion distributions in the next executable research run.

## 7. What this run proves

1. Source alignment materially changes the meaning of an accepted setup.
2. The current close-reclaim entry cannot be retained as canonical.
3. The current generic P-Gap detector cannot be promoted.
4. The current Leg-2 projection cannot be promoted until A/B/C/D geometry is source-resolved.
5. Therefore the baseline's profitability cannot yet be attributed to the source-defined SP2L strategy.
6. The correct next measurement is a replay with frozen source geometry, not parameter optimization.

## 8. Gate status

**SOURCE RESOLUTION:** IN PROGRESS  
**SYNTHETIC FIXTURES:** COMPLETE FOR CURRENT COMPETING GEOMETRIES  
**FROZEN GEOMETRY:** BLOCKED  
**DEV:** NOT STARTED FOR CANONICAL GEOMETRY  
**VALIDATION:** LOCKED  
**PRODUCTION:** UNCHANGED

## 9. Next executable comparison

Once P-Gap and A/B/C/D geometry are source-resolved, run the same dataset through:

`BASELINE` → existing heuristic implementation  
`SOURCE-FROZEN` → exact canonical implementation  

and produce, at minimum:

- candidate count;
- filled-order count;
- unfilled pending orders;
- wins/losses;
- expectancy and median R;
- profit factor;
- drawdown;
- consecutive losses;
- long/short split;
- session/time-of-day breakdown only if source-confirmed;
- MAE/MFE;
- trade clustering;
- exact list of baseline trades removed, retained, or changed by source alignment.

No optimization is permitted during this comparison.
