# SP2L Real-Chart Order Reconstruction — 2026-09-08

**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Production impact:** none

## Objective

Use the real XAUUSD execution/history segment in the uploaded primary source to determine whether actual Entry / SL / TP prices can resolve the remaining SP2L candle geometry.

## Source segment inspected

The execution/history segment around **61:50–64:30** was inspected frame-by-frame, including the MT4/MT5-like order-history table and the annotated XAUUSD chart.

The visible execution records include four relevant XAUUSD sell entries:

| Entry | SL | TP | Observed close | Observed profit | Risk distance |
|---:|---:|---:|---:|---:|---:|
| 3229.08 | 3237.73 | 3213.37 | 3223.36 | 118.40 | 8.65 |
| 3223.84 | 3235.50 | 3213.37 | 3223.36 | 10.60 | 11.66 |
| 3228.88 | 3235.50 | 3213.37 | 3223.36 | 112.80 | 6.62 |
| 3232.41 | 3237.80 | 0.00 | 3223.36 | 364.40 | 5.39 |

These values are transcribed from the visible source table. They are source observations, not inferred strategy rules.

## What the records establish

### 1. Multiple entries can coexist within one bearish sequence

The four records have different entry prices and different stop distances while sharing the same broad execution episode. This is consistent with the source's explanation that additional entries / 2X-style management can occur at different levels.

**Status:** source-supported execution behavior.

### 2. Stop is structural, but not numerically resolved by the table alone

The SL values differ (3235.50, 3237.73, 3237.80), so the stop cannot safely be modeled as a universal fixed-distance formula. The table alone does not identify which exact candle High/Low is the canonical structural anchor.

**Status:** structural invalidation = source-confirmed; exact SL anchor = unresolved.

### 3. TP cannot be inferred as `Entry ± 1R` from these real trades

For example, Entry 3229.08 with SL 3237.73 has risk 8.65, while the visible TP 3213.37 is 15.71 price units away. That is not 1R. Other rows likewise do not share one fixed `Entry ± 1R` geometry.

This does **not** invalidate the official/source statement that TP1 / a base 1:1 target is used for the strategy. It means the displayed real-chart execution segment cannot be used to freeze a universal target formula. The episode may contain multiple trades / management states, and one row has no TP.

**Status:** target module remains unresolved for canonical executable geometry.

### 4. Real-chart annotations are not A/B/C/D labels

The chart annotations visible in this segment are primarily numeric / management annotations such as `1`, `2`, `2X`, `E`, and `0.0`. They cannot be reliably interpreted as harmonic A/B/C/D points.

This is consistent with the transcript's explicit distinction between classical internet A/B/C/Fibonacci treatment and the source's candle-level AB=CD explanation.

**Status:** classical harmonic anchors remain rejected as an automatic interpretation.

## What the records do NOT establish

The real execution table does not provide enough information to uniquely determine:

- the exact two-candle boundaries of P-Gap;
- whether P-Gap is wick-based or body-based;
- whether the displayed Entry price equals the previous candle Low/High in the source chart;
- whether Entry is a geometric C point;
- the exact Leg-1 origin candle;
- the exact structural SL candle/price anchor;
- the AB=CD tolerance;
- the intrabar ordering between limit fill and invalidation;
- whether the common TP 3213.37 is a canonical 1R target, a structural level, or a management target for that episode.

## Important numerical observation

The four visible entries should **not** be converted into a fitted rule. In particular, the relationship between Entry, SL, and TP varies materially enough that reverse-engineering a formula from these few trades would be parameter mining / source overreach.

The correct use of these records is therefore as **negative/constraint evidence**:

> Real execution confirms that the system uses concrete pending entries and structural stops, but the visible execution table does not uniquely identify their candle anchors.

## Gate decision

**Real-chart execution evidence:** useful  
**Entry price anchor:** unresolved  
**SL anchor:** unresolved  
**P-Gap formula:** unresolved  
**Target formula:** unresolved  
**Classical A/B/C/D interpretation:** rejected  
**Production change:** none

## Next research action

The highest-value remaining source-resolution task is no longer to infer geometry from the order table alone. It is to align the **entry/SL price levels with the exact candle sequence immediately before each order placement** and determine whether the visible price scale provides a trustworthy mapping. If that mapping remains ambiguous at source resolution, the ambiguity must be preserved and the geometry gate must remain blocked.
