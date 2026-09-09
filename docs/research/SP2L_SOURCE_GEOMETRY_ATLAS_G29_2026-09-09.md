# SP2L Source Geometry Atlas — G29 — 2026-09-09

## Purpose

This atlas records repeated source examples at the visual-geometry level without converting visual similarity into an executable formula. It is a source-resolution artifact, not a production strategy specification.

## Evidence policy

- Direct source video frames and the recovered source transcript have priority.
- A chart annotation is evidence of the teacher's demonstrated intent, but not automatically proof of an OHLC coordinate formula.
- If multiple coordinate interpretations remain consistent with the source, the coordinate remains UNRESOLVED.
- Historical profitability is not an admissible tie-breaker.

## Atlas A — P-Gap / valid breakout

### A1 — ~34:10
Observed visual: several spike constructions are shown; one construction is explicitly rejected with a red X, while another is annotated with BO, key bar and a circled low.

Source-level conclusion: the teacher distinguishes acceptable spike/breakout constructions from a rejected construction and uses P-Gap in this teaching sequence.

Geometry conclusion: candle indexing and the exact OHLC boundary are not uniquely specified by the frame.

Status: **SEMANTIC CONFIRMED / GEOMETRY UNRESOLVED**.

### A2 — ~35:35
Observed visual: multiple constructions are circled/annotated under an explicit P-GAP heading. The examples are not identical in candle count/shape.

Source-level conclusion: P-Gap is a first-class concept covering more than one visual construction.

Geometry conclusion: the source does not justify replacing the concept with a generic three-candle imbalance/FVG formula.

Status: **GENERIC-FVG INTERPRETATION REJECTED / EXACT FORMULA UNRESOLVED**.

### A3 — ~36:46
Observed visual: explicit text `Valid BO = P-Gap` appears together with `AB=CD`.

Source-level conclusion: valid breakout is explicitly associated with P-Gap.

Geometry conclusion: this frame establishes the semantic relation, not a unique OHLC equation.

Status: **SEMANTIC CONFIRMED / GEOMETRY UNRESOLVED**.

## Atlas B — Entry

### B1 — ~38:54
Observed visual: bullish sequence with higher-low annotations; a handwritten `Limit`/`(سفارش) Limit` is placed beside a horizontal order line.

Source-level conclusion: the correction phase is associated with a pending Limit order.

Geometry conclusion: the horizontal line is visibly associated with the structural sequence, but the frame alone does not uniquely identify wick/body/pivot as the universal coordinate.

Status: **PENDING-LIMIT CONFIRMED / ANCHOR UNRESOLVED**.

### B2 — ~39:30
Observed visual: `Buy Lim` is written next to a horizontal order line crossing the demonstrated bullish structure.

Source-level conclusion: the order is pending and is placed before/within the correction rather than being replaced by a market close-reclaim rule.

Geometry conclusion: the line is not proven to equal the original spike low and is not proven to equal the start of Leg 2.

Status: **ENTRY MECHANISM CONFIRMED / EXACT ANCHOR UNRESOLVED**.

### B3 — ~39:45
Observed visual: explicit `Buy Limit` and separate `SL` annotations; SL is materially below Entry in the bullish example.

Source-level conclusion: Entry and invalidation are distinct levels and the stop is structural.

Geometry conclusion: exact wick/body/pivot coordinate and any buffer remain unresolved.

Status: **STRUCTURAL RELATION CONFIRMED / OHLC ANCHOR UNRESOLVED**.

## Atlas C — Trigger / order management

### C1 — ~53:16 onward
Recovered transcript states that one-, two-, and three-candle formations can lead to placement of the Limit entry trigger; the example is described as taking about three minutes to trigger.

Source-level conclusion: a trigger family exists and is not restricted to one candle.

Geometry conclusion: exact acceptance condition, timing convention, and whether all variants share one deterministic OHLC test remain unresolved.

Status: **TRIGGER FAMILY CONFIRMED / ACCEPTANCE UNRESOLVED**.

### C2 — ~39:26–40:16
Source narration describes deleting/replacing a pending order when a new candle materially changes the distance to the stop.

Source-level conclusion: pending-order management can respond to a material structural/risk-distance change.

Geometry conclusion: the exact threshold and event timing are not source-confirmed.

Status: **QUALITATIVE UPDATE RULE CONFIRMED / THRESHOLD UNRESOLVED**.

## Atlas D — Leg 1 / Leg 2 / AB=CD / TP

### D1 — ~36:15–37:57
Source teaching explicitly introduces AB=CD and describes the next leg as expected to have the same magnitude as the first leg.

Source-level conclusion: AB=CD is a magnitude relationship between the two legs.

Geometry conclusion: A/B/C/D anchors and tolerance are not uniquely defined; no wick/body/pivot model is promoted.

Status: **MAGNITUDE RELATIONSHIP CONFIRMED / ANCHORS + TOLERANCE UNRESOLVED**.

### D2 — ~53:43
Recovered transcript describes a pullback to the beginning of Leg 2 and explicitly distinguishes Leg 1 from Leg 2.

Source-level conclusion: Entry and Leg-2 start are separate concepts.

Geometry conclusion: this does not prove that the entry line equals Leg-2 start.

Status: **SEMANTIC DISTINCTION CONFIRMED**.

### D3 — ~42:26–42:37
Source discussion distinguishes TP1 and TP2 and states that TP1 is generally used, while TP2 is a larger objective that should be evaluated by backtest.

Source-level conclusion: TP1 is the preferred demonstrated exit; TP2 is a research candidate.

Geometry conclusion: executable TP1 projection remains unresolved until the Leg1/Leg2 coordinate model is source-frozen.

Status: **TP PREFERENCE CONFIRMED / PROJECTION UNRESOLVED**.

## Atlas E — Bearish mirror

### E1 — ~55:00 onward
Direct bearish chart examples show upper `SL`, separate `E`/Entry annotations, and subsequent downward continuation/Leg-2 markings.

Source-level conclusion: bearish execution mirrors the bullish structural model: Lower Highs → directional continuation → Sell Limit → structural invalidation above.

Geometry conclusion: the exact bearish candle-level entry/stop coordinate is not sufficiently explicit to freeze wick/body/pivot behavior.

Status: **STRUCTURAL MIRROR STRONGLY SUPPORTED / OHLC GEOMETRY UNRESOLVED**.

## Cross-example findings

1. Entry is consistently presented as a **pending Limit order** rather than a market reclaim.
2. Entry is associated with a relevant structural Low/High in the demonstrated sequence.
3. Entry is not safely reducible to the original Spike extreme in every example.
4. Entry is not safely reducible to Leg-2 start.
5. SL is structurally distinct from Entry.
6. P-Gap is source-specific and must not be silently replaced by generic FVG/imbalance logic.
7. AB=CD establishes a two-leg magnitude relationship but not an executable coordinate formula.
8. One-, two-, and three-candle trigger examples exist; exact acceptance is unresolved.
9. Pending order replacement is qualitative in the source; the numeric/algorithmic threshold is unresolved.
10. Bearish structural symmetry is supported, but exact OHLC geometry remains incomplete.

## Additional source-resolution findings from recovered transcript

11. The source explicitly says the chart should be read candle-by-candle and describes OHLC components as important observables. This strengthens the requirement that any production rule must be candle-indexed and OHLC-deterministic once frozen.
12. The source explicitly describes the correction for the bullish example as moving below the first Low, while the visual entry line is later associated with the evolving structural sequence. This supports a correction/structure relationship but does not uniquely define the order-line coordinate.
13. The source explicitly states that two P-Gap constructions can be treated as one strategy branch despite different ordering of breakout, higher lows and gap formation. Therefore a production detector must support multiple source-confirmed construction families if/when their exact geometry becomes resolvable.
14. The source explicitly warns against confirmation bias and asks viewers to inspect losses as well as wins. This is a methodological source principle, not a trading filter.
15. The source uses M1/M5 examples and states that lower timeframes are where this style is applied; this does not by itself authorize a production timeframe restriction because the broader source discussion also distinguishes strategy/timeframe contexts.

## Resolution decision

The atlas **does not justify Frozen Geometry**.

Current result:

- G1 P-Gap: **UNRESOLVED**
- G2 Entry: **UNRESOLVED**
- G3 SL: **UNRESOLVED**
- G4 Trigger: **UNRESOLVED**
- G5 AB=CD: **UNRESOLVED**
- G6 Leg2/TP1: **UNRESOLVED**
- G7 Pending replacement: **UNRESOLVED**
- G8 Bearish OHLC mirror: **UNRESOLVED / partial semantic resolution**

## Gate decision

**SOURCE RESOLUTION: semantic PASS**

**SYNTHETIC DISCRIMINATION: PASS**

**FROZEN GEOMETRY: BLOCKED**

**DEV and later validation gates: LOCKED**

This is an explicit source limitation, not a failed research process. No production formula is to be inferred from the atlas.