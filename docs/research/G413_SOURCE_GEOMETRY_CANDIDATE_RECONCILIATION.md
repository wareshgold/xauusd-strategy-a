# G413 — Source Geometry Candidate Reconciliation

Date: 2026-09-14
Parent: G412
Status: SOURCE-RECONCILIATION / GEOMETRY NOT FROZEN

## Purpose

Reconcile the remaining executable-geometry candidates against the recovered Strategy A transcript without using backtest performance, trading convention, or implementation convenience as evidence.

This gate narrows candidates only where the source wording supports narrowing. It does not convert a visual resemblance into a canonical formula and does not authorize DEV, optimization, or production.

## Evidence basis

Primary evidence: `پورصمدیSP2L TRANSCIBE.txt`.
Supporting evidence: previously registered source-video frame observations and immutable frame hashes recorded by G337/G338/G409/G410.

The transcript repeatedly instructs the viewer to inspect the market candle-by-candle and explicitly distinguishes candle OHLC attributes such as high, low, open and close. Therefore exact executable geometry must still be resolved against the actual source visuals rather than inferred from terminology alone.

## 1. P-Gap

### Source-supported narrowing

At 31:43 the speaker identifies P-Gap as a pressure gap inside the breakout candle and distinguishes it from E-Gap. At 32:03–32:12 he states that P-Gap, E-Gap, Common-Gap and other gaps are distinct concepts and that the location of formation matters. At 34:25 he gives a visible example where the first candle high and following candle low do not overlap, associating that gap with breakout + follow-through. At 34:35–35:37 he explicitly accepts more than one event ordering as the same Strategy A concept.

### Candidate disposition

- `PGAP-H1 generic three-candle range separation`: NOT SOURCE-PROMOTED.
- `PGAP-H2 body-boundary separation`: NOT SOURCE-PROMOTED.
- `PGAP-H3 wick-boundary separation`: NOT SOURCE-PROMOTED.
- `PGAP-H4 source-specific pressure-gap construction`: RETAINED as the source-aligned semantic hypothesis.

### Still open

Exact candle pair, exact OHLC fields, minimum gap magnitude, tolerance, and whether the displayed non-overlap is a necessary/sufficient executable condition remain unresolved.

## 2. A/B/C/D and AB=CD

### Source-supported narrowing

At 36:15 the speaker explicitly identifies 2Leg with AB=CD. At 36:59–37:08 he states that after the spike and correction, the second leg is expected to equal the first. At 37:57 the same equality relationship is repeated.

At 1:04:00–1:04:19 the worked example describes a deep leg beginning from a sequence of lower highs and places the order progressively lower until activation. The transcript therefore demonstrates that the visually measured first leg can have a deeper structural origin than a simplistic order/fill point.

### Candidate disposition

- Semantic relationship `Leg2 magnitude = Leg1 magnitude`: SOURCE-CONFIRMED.
- Arbitrary candle-index A/B/C/D selectors: NOT PROMOTED.
- `fill = C`: EXPLICITLY NOT AUTHORIZED.
- Any fixed price field selection for A/B/C/D: UNRESOLVED.
- Any fixed equality tolerance: UNRESOLVED.

The worked example narrows the research question toward source-defined structural swing points, but does not by itself establish a deterministic selector.

## 3. Entry / Buy Limit

### Source-supported narrowing

At 38:38 the bullish correction is described as moving below the first low and the speaker states that a manual order or pre-defined limit may be placed there. At 39:11 he states that the limit can be placed within the first three candles rather than waiting for another candle. At 39:26 he explicitly calls it a Buy Limit and reasons about stop distance before activation. At 39:48 onward he describes order adjustment/deletion when subsequent candles materially change the scenario.

### Candidate disposition

- Pending-limit execution: SOURCE-CONFIRMED.
- Market-close reclaim: REJECTED as a replacement for the source method.
- Entry at geometric C: UNRESOLVED / NOT AUTHORIZED.
- Entry at an exact first-low OHLC field: NARROWED BUT NOT FROZEN.
- Touch/overshoot fill semantics: UNRESOLVED.
- Persistence/update/cancellation algorithm: UNRESOLVED.

The source supports a level in the correction/first-low area, but not a sufficient numerical rule for selecting that level.

## 4. Structural invalidation / SL

### Source-supported narrowing

At 39:26 the speaker states that the scenario is invalid if price returns to the referenced invalidating area before activation. At 41:18 the activated position is shown with an SL. Existing source corroboration identifies the spike-origin candle as the structural stop reference.

### Candidate disposition

- Stop tied to source-defined structural/spike-origin invalidation: RETAINED.
- Full-wick boundary vs body boundary: UNRESOLVED.
- High/low vs open/close executable field: UNRESOLVED.
- Buffer: UNRESOLVED.
- Exact pre-fill cancellation boundary: UNRESOLVED.

No stop price is frozen by G413.

## 5. TP1 / TP2

### Source-supported narrowing

At 42:26 the source distinguishes TP1 and TP2 and states that TP1 is the speaker's usual choice. At 42:37–42:48 TP2 is described as relatively large and target 1 is preferred. The later 1:04:19–1:04:32 example explicitly demonstrates reward 1 and mentions reward 2 as an alternative. The 50:44–50:56 example also describes Leg 1 / Leg 2 and target 1.

### Candidate disposition

- Core target convention: R=1 / TP1: SOURCE-CONFIRMED.
- TP2 as a larger alternative: SOURCE-CONFIRMED.
- Exact TP1 geometric mapping: UNRESOLVED.
- Exact TP2 geometric mapping: UNRESOLVED.
- Arbitrary AB=CD-derived TP extension: NOT PROMOTED.

## 6. Context and time/session observations

The transcript contains contextual observations about range, higher-timeframe trend, moving averages, broker time, and market-opening periods. These may be source-supported contextual observations, but G413 does not promote them into mandatory Strategy A filters because their exact logical role and scope have not been frozen.

In particular, the transcript's mention of broker time and European market opening is not sufficient evidence for a deterministic session filter.

## 7. Reconciliation outcome

| G400 blocker | G413 result |
|---|---|
| `UNRES-PGAP-GEOMETRY` | OPEN / source-specific semantics narrowed |
| `UNRES-ABCD-ANCHORS` | OPEN / structural-origin evidence strengthened |
| `UNRES-ABCD-TOLERANCE` | OPEN |
| `UNRES-ENTRY-PRICE` | OPEN / first-low correction area narrowed |
| `UNRES-ENTRY-TIMING` | PARTIALLY RESOLVED / execution semantics open |
| `UNRES-STOP-BOUNDARY` | PARTIALLY RESOLVED / exact executable price open |
| `UNRES-TARGET-MAPPING` | PARTIALLY RESOLVED / R=1 primary, geometry open |

## Gate decision

`G413 = PASS — SOURCE CANDIDATE RECONCILIATION`

This is a research/source-resolution pass only.

`G400 = BLOCKED`

`FROZEN_GEOMETRY = NOT AUTHORIZED`

`DEV = NOT AUTHORIZED`

`VALIDATION = PROTECTED`

`PRODUCTION = BLOCKED`

## Next required action

The remaining work is no longer broad transcript discovery. It is controlled visual resolution of the narrowed questions against the registered source-video frames:

1. 34:14–35:50 — identify the exact P-Gap candle boundaries and OHLC field relationship.
2. 36:15–37:10 — identify the visual A/B/C anchors used for AB=CD.
3. 38:18–40:16 — identify the actual Buy Limit level and cancellation/update boundary.
4. 41:18–42:48 — identify the exact stop boundary and TP1/TP2 visual mapping.
5. 1:04:00–1:04:42 — reconcile deep-leg origin, entry movement, Leg 1 and R=1/R=2.

If the source visuals do not uniquely resolve any item, it must remain unresolved. No optimization is permitted as a substitute for source resolution.
