# SP2L Spike → Entry Cross-Check

Date: 2026-09-08
Branch: `research/source-resolution-entry-level-v2`

## Purpose

Cross-check the newly inspected full-video spike section (approximately 29:00–35:30) against the later entry/AB=CD section (approximately 36:00–41:50) and authoritative published source material.

This is a research evidence record. It does **not** freeze unresolved geometry and does not authorize production changes.

## Source-confirmed core

The authoritative SP2L strategy page describes the core sequence as a strong/sharp move (Spike), correction, and continuation/2nd Leg. It explicitly states that a valid spike is associated with a P-Gap and describes the corrective entry condition in candle-relative terms: for a bullish setup the correction reaches/touches the prior candle's low; for a bearish setup the correction reaches/touches the prior candle's high.

The full source video independently shows:

- `SP2L Strategy / Spike - 2Leg`;
- `Valid BO = P-Gap`;
- repeated `AB=CD` annotation;
- a multi-wave impulse/correction/continuation drawing;
- `Limit`, `BO`, and `Buy Limit` annotations;
- `SL` below the lower structural area;
- a separate `2X` module.

These observations strengthen the following deterministic semantic chain:

`Spike → P-Gap-valid breakout → correction → candle-relative limit-entry condition → second-leg continuation`

The exact executable price formula remains unresolved because the source material inspected at available raster resolution does not uniquely identify all OHLC anchors or prove that the entry level is identical to geometric C of AB=CD.

## Four-spike teaching section

The 29:00–35:30 inspection found four visually distinct spike examples. They are retained as source examples rather than named/parameterized as four canonical algorithms.

### Example-level findings

1. The examples consistently emphasize directional/impulsive movement rather than a generic single-candle reversal pattern.
2. P-Gap markings are repeatedly associated with valid breakout/spike examples.
3. Invalid/marked-out examples are present, supporting the idea that not every sharp movement qualifies.
4. Horizontal candle/price levels are used in the teaching drawings and later connect to Buy/Sell/Limit discussion.
5. The available 640×360 raster does not expose enough coordinate detail to establish a unique P-Gap boundary formula or exact A/B/C/D OHLC anchors.

## Cross-check against later entry section

The 36:00–41:50 sequence adds direct execution semantics:

- `AB=CD` is explicitly written;
- `Limit` is written beside a horizontal reference level;
- `BO` is added;
- `Buy Limit` is explicitly written on the illustrated level;
- `SL` is explicitly placed below the lower structural area;
- `2X` is separately annotated.

This supports pending-limit entry as canonical semantics, but does **not** justify replacing it with a market close-reclaim trigger.

## External corroboration — non-canonical

A third-party TradingFinder description independently reports that its SP2L implementation uses a spike structure, treats the spike as AB, and determines entry from breakout of the last spike candle boundary. This is useful triangulation because it aligns with the source-video candle-relative entry teaching, but it is **not authoritative source evidence** and must not be used to freeze Strategy A geometry by itself.

The same third-party material reports a three-candle spike pattern and a 65% body/range condition. Those numerical conditions are explicitly classified here as **NON-CANONICAL / UNVERIFIED** and are not promoted into Strategy A.

## Geometry decision matrix

| Element | Current status | Reason |
|---|---|---|
| Spike → correction → 2nd Leg | SOURCE-CONFIRMED | Video + authoritative published description |
| P-Gap required for valid breakout | SOURCE-CONFIRMED SEMANTIC | Video explicitly says `Valid BO = P-Gap` |
| Correction reaches prior candle low/high | SOURCE-CONFIRMED SEMANTIC | Authoritative published description |
| Pending Limit semantics | SOURCE-CONFIRMED | Video explicitly shows `Limit` / `Buy Limit` |
| SL below/behind spike origin structure | SOURCE-CONFIRMED | Video + published description |
| Spike = exact three-candle formula | UNRESOLVED | Third-party claim only; source video not sufficient to freeze |
| P-Gap exact candle formula | UNRESOLVED | No unique OHLC boundary exposed |
| A/B exact anchors | UNRESOLVED | Visual endpoints remain ambiguous |
| C exact AB=CD anchor | UNRESOLVED | Entry/reference level not explicitly labeled as C |
| AB=CD tolerance | UNRESOLVED | No source numeric tolerance |
| 2X = core TP | UNRESOLVED / SEPARATE MODULE | Source presents it separately |

## Guardrails

- Do not import the third-party 65% body/range threshold.
- Do not import a generic three-candle P-Gap formula.
- Do not infer C from the Buy Limit price merely because they appear visually associated.
- Do not replace pending-limit semantics with close-reclaim execution.
- Do not use backtest performance to choose among unresolved geometry candidates.

## Gate impact

Source Resolution has materially advanced, but canonical geometry is still blocked by P-Gap executable geometry and exact A/B/C anchors.

DEV/VAL/Fresh Holdout/Production remain unchanged.
