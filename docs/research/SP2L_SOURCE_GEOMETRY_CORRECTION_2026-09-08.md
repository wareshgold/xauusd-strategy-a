# SP2L Source Geometry Correction — 2026-09-08

**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Status:** source-resolution correction; production unchanged

## 1. Why this correction exists

A closer frame-by-frame inspection of the real XAUUSD section around 62:00–63:00 shows that the small annotations on the chart are not sufficiently reliable to call them A/B/C/D labels. The visible marks include numbered/management-style annotations and labels such as `2X`, `E`, and `0.0`. At 640×360 the raster does not provide a defensible basis for mapping those marks to classical AB=CD points.

Therefore the earlier wording that treated the real-chart marks as `A/B/C/D-style labels` is **downgraded**. It must not be used as evidence for exact A/B/C/D OHLC anchors.

This correction is source-first: the earlier interpretation was too strong and is being explicitly superseded rather than silently retained.

## 2. Stronger evidence: the transcript rejects importing classical AB=CD mechanically

At 36:15–36:46 the instructor explicitly introduces 2Leg as AB=CD, then contrasts the classical internet treatment — taking A and B, moving to C, and applying Fibonacci — with the method taught here. He says the work is brought down to the candle level / wording level.

The direct transcript therefore supports:

- `AB=CD` is a source concept;
- classical Fibonacci AB=CD implementation is **not** automatically canonical;
- the source expects a candle-level interpretation;
- exact A/B/C/D labels are not required to be imported from generic harmonic-pattern conventions.

The transcript then states at 36:59 that after a Spike, a correction is expected and Leg 2 should equal Leg 1. At 37:57 it repeats that the next leg should be the same size as the first leg.

## 3. Real-chart section: what is actually established

The later real XAUUSD chart is valuable because the instructor verbally describes the geometry of the movement while showing the actual market structure.

At approximately 62:41–64:32 the transcript describes:

- a sequence of lower highs in the bearish scenario;
- the search for the second leg;
- a first leg and a later second leg;
- a deeper correction;
- placing an order during the later structure;
- the first leg magnitude and a 1R target;
- the market being evaluated candle-by-candle.

At ~64:19 the instructor describes placing the order and says that the first leg runs from one displayed structural point to another, with the SP2L target corresponding to the equal-leg projection. This is strong evidence for **leg-to-leg measurement**, but it still does not expose a machine-readable OHLC rule for selecting the exact endpoint candle/price.

## 4. Important geometry narrowing

The surviving source interpretation should therefore no longer be framed as:

`classical A/B/C/D harmonic pattern → calculate C → calculate D`

The stronger source-aligned formulation is:

`source-defined Spike movement → source-defined correction → source-defined Leg 1 magnitude → source-defined Leg 2 of equal magnitude`

This is materially narrower and avoids importing an external harmonic-pattern convention.

However, the following are still unresolved:

- exact candle/price endpoint for Leg 1;
- exact correction anchor used for the entry/second-leg start;
- whether the pending Limit is exactly the prior candle extreme;
- exact endpoint used for Leg 2 target;
- any numeric equality tolerance.

## 5. Entry anchor: evidence is now stronger

The recovered transcript says at 38:38 that, in the bullish example, correction means price moves below the first low and that the order can be placed there manually or as a pre-set Limit. At 38:53–39:26 it says the Limit can be placed during the first three candles and that the SL distance is known before activation.

The official SP2L page independently states that for an uptrend the corrective candle reaches the low of the previous candle, while for a downtrend it reaches the high of the previous candle; it then describes entry in the Spike direction and a structural SL behind the candle from which the Spike originated. citeturn1search0turn1search1

This materially strengthens the candidate:

- BUY-side correction/trigger reference: prior-candle Low;
- SELL-side correction/trigger reference: prior-candle High.

But the distinction between **trigger condition** and **pending Limit price** must remain explicit until the video drawing or a source statement proves they are numerically identical. Therefore `entry = prior-candle low/high` is now **STRONGLY SUPPORTED CANDIDATE**, not yet frozen as executable geometry.

## 6. P-Gap remains the primary hard blocker

The source repeatedly states `Valid BO = P-Gap`, distinguishes P-Gap from E-Gap/Common-Gap, and visually draws a gap/non-overlap relationship. The exact candle boundaries, wick/body treatment, and tolerance are still not explicit enough to promote the existing generic three-candle detector.

No P-Gap formula is introduced by this correction.

## 7. Synthetic fixtures to add next

The next discriminating fixtures should focus on the newly narrowed interpretation:

| Fixture | Discriminator |
|---|---|
| PG-01 | prior-candle Low/High equals the pending Limit |
| PG-02 | correction reaches prior-candle extreme but Limit is elsewhere |
| PG-03 | wick touches prior-candle extreme vs body-only touch |
| PG-04 | correction crosses the extreme intrabar and later closes back |
| PG-05 | P-Gap before correction vs P-Gap after higher-lows |
| LEG-01 | Leg 1 measured from Spike origin to Spike extreme |
| LEG-02 | Leg 1 measured from breakout candle to Spike extreme |
| LEG-03 | Leg 1 measured from first structural low/high to Spike extreme |
| LEG-04 | deep correction followed by equal Leg 2 |
| LEG-05 | same visual Leg 1 but different candle endpoint |

These fixtures distinguish source interpretations; they do not select one based on profitability.

## 8. Gate decision

### Promoted / strengthened

- SP2L = Spike → 2Leg.
- AB=CD means equal first/second-leg magnitude at source semantic level.
- Classical harmonic/Fibonacci AB=CD must not be imported automatically.
- Pending-limit entry during correction is source-confirmed.
- Prior-candle Low/High is a strongly supported correction/trigger reference.
- Base TP 1:1 is strongly supported by the official source and the video discussion.

### Still blocked

1. P-Gap executable geometry.
2. Exact Spike variant predicates.
3. Exact pending-Limit price vs correction-trigger price.
4. Exact Leg 1 endpoints.
5. Exact Leg 2 endpoint.
6. Intrabar fill semantics.
7. AB=CD equality tolerance.
8. Exact red-X rejection predicate.

### Gate status

**SOURCE RESOLUTION: PROGRESSING**  
**FROZEN GEOMETRY: BLOCKED**  
**DEV: NOT AUTHORIZED FOR CANONICAL SP2L**  
**VAL: UNTOUCHED**  
**FRESH HOLDOUT: LOCKED**  
**PRODUCTION: UNCHANGED**

## 9. Guardrail

This document supersedes the earlier interpretation that the ~62:30 real-chart marks were reliable A/B/C/D labels. The earlier document remains in the repository as historical research evidence, but this correction is the current source-resolution interpretation.
