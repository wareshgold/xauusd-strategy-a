# G352 — Transcript Deep Source Audit

Date: 2026-09-12  
Gate: SOURCE RESOLUTION  
Canonical status: **NO GEOMETRY FREEZE**

## Scope

Primary textual source: `پورصمدیSP2L TRANSCIBE.txt`, the direct timestamped transcript of the SP2L lesson video.

This audit extracts only what the transcript explicitly supports. It does not convert examples, visual annotations, or common trading terminology into canonical executable rules.

## Evidence map

| Timestamp | Transcript evidence | Source-supported meaning | Executable status |
|---|---|---|---|
| 19:52–20:48 | Candle-by-candle reading; high/close/open/low are inspected; examples ask whether a close is below a prior level and whether gaps occur inside candles | Candle-level observation and breakout/gap context are part of the teaching method | **Semantic only**; no universal OHLC selector/fixed threshold |
| 27:51–28:29 | Strong movement can be expressed through higher lows; inverse case uses lower highs | Spike/strong directional movement can be represented by a sequence of structural price movements | **Unresolved** exact spike-start/end algorithm |
| 35:10–36:05 | Three observed spike forms are discussed; one includes breakout + FL + P-GAP, another higher lows followed by a gap, and another ends around creation of a low followed by a bearish candle; all are treated as Spike | Spike is a family of observed directional structures, not necessarily one candle shape | **Semantic only**; no deterministic selector |
| 36:15–36:59 | SP2L is described as Spike–2Leg; 2Leg is explicitly equated with AB=CD; the teacher says the method works at candle level rather than classical generic A/B/C/Fibonacci treatment | AB=CD is a core conceptual relationship and is adapted to candle-level analysis | **Canonical concept**; A/B/C/D anchors remain unresolved |
| 36:59–37:08 | After a Spike, expectation is a correction and completion of the second leg, with Leg 1 and Leg 2 equal | Core SP2L sequence and equal-leg expectation | **Canonical semantic rule**; exact measurement/anchor/tolerance unresolved |
| 37:22–37:57 | A later third leg is acknowledged but intentionally deferred; after the increase, expectation is a correction and another leg approximately equal to the first | Current lesson scope is Leg 1 → correction → Leg 2; Leg 3 is outside this rule freeze | **Do not implement as Strategy A core** |
| 38:05–38:18 | In an example, first pullback is used to place SL/order and a second position may be added at 2X | Entry/position-management examples exist | **Example only** for exact placement/2X mechanics |
| 38:38–39:48 | During correction, a limit order can be placed; if price returns through the described invalidation area, the scenario is invalidated | Pending-limit semantics and structural invalidation are source-supported | **Canonical semantic rule**; exact limit price and invalidation price remain unresolved |
| 41:18–42:37 | Next candle activates the order; SL is shown; second position is optional; TP may be TP1 or TP2; presenter generally uses TP1 | Pending order becomes a trade when price reaches it; TP1/TP2 are explicit outcome labels | **Canonical semantic**; exact price formulas unresolved |
| 45:02–45:55 | After a range, price chooses a direction; trader enters in that direction for the second leg; entry is described as highly favorable and backtesting is recommended | Range/context → directional move → second-leg participation is core narrative | **Semantic only** for range algorithm and entry price |
| 49:47–50:44 | M1 MA60 is used as context; prior high is broken; P-GAP/E-GAP terminology is applied; later move may be considered Leg 2 | P-GAP/E-GAP are source concepts and market-context tools | **Blocked** for formula/classification algorithm |
| 50:56–51:39 | Repeated target progression can increase E-GAP likelihood; when situation is risky, wait for equilibrium/MA | P-GAP/E-GAP classification affects setup quality; MA is described as equilibrium in this example | **Not a hard session/MA gate**; no deterministic E-GAP threshold |
| 53:16–53:54 | One-, two-, or three-candle structure can create a trigger; a limit entry can be placed; later price may pull back to the beginning of Leg 2 | Candle-count examples and pending-limit entry are source-supported | **No universal 1/2/3 candle trigger rule** |
| 54:10–54:29 | When probability is lower, risk can be reduced; a buy-limit can provide another opportunity | Risk scaling and repeat limit entry are management examples | **Not a canonical fixed risk formula** |
| 59:20–59:42 | Positions can have R2/R1 outcomes; one position may remain without TP; combined positions can change effective reward | R1/R2 are reward/position-management outcomes | **No fixed numeric TP formula** |
| 1:02:31–1:03:03 | Reversal toward the end of a bearish scenario is assessed using a sequence of lower highs; Leg 1 and Leg 2 are explicitly identified | Structural sequence and Leg 1/Leg 2 labeling are source-supported | **No deterministic swing/fractal algorithm** |
| 1:03:03–1:04:32 | A nested 2Leg exists; larger movement can be treated as one leg and the subsequent move as another; a deep leg is identified; seven lower highs are counted; a pending order is placed; parent Leg 1 is later described from the deep-leg origin; TP1 is R1 and R2 is also possible | Multi-scale/nested leg concept, deep-leg origin, pending-limit execution, R1/R2 target outcomes | **Canonical semantic chain**; scale selection, anchor coordinates and exact formulas unresolved |

## Resolved vs unresolved dimensions

### Source-confirmed / safe to preserve

1. **SP2L = Spike → 2Leg.**
2. **Spike → correction → Leg 2** is the central sequence.
3. **Leg 1 and Leg 2 are expected to be equal in the AB=CD sense.**
4. **Pending-limit entry during correction is part of the source workflow.**
5. **Structural invalidation exists.**
6. **TP1/TP2 and R1/R2 are real source terms.**
7. **Optional second/additional positions (2X/3X examples) are management concepts, not the core geometric definition.**
8. **Nested / parent-scale 2Leg structures are explicitly demonstrated.**
9. **P-GAP/E-GAP are source terminology and materially affect setup quality.**
10. **The transcript repeatedly instructs candle-by-candle inspection and backtesting rather than blind acceptance.**

### Still unresolved — must remain blocked

| Dimension | Current status |
|---|---|
| Exact P-Gap formula | **BLOCKED** |
| P-Gap minimum size / overlap / candle count | **BLOCKED** |
| Wick vs body vs open/close convention | **BLOCKED** |
| Exact Spike start/end candle | **BLOCKED** |
| Exact correction trigger | **BLOCKED** |
| Exact pending-limit price | **BLOCKED** |
| Exact SL price and offset | **BLOCKED** |
| A/B/C/D anchors | **BLOCKED** |
| AB=CD translation from geometry to executable price | **BLOCKED** |
| AB=CD tolerance | **BLOCKED** |
| Deterministic parent-vs-nested scale selection | **BLOCKED** |
| Exact TP1/TP2 numeric formulas | **BLOCKED** |
| Fixed meaning of 2X/3X as target multiples | **BLOCKED** |
| Seven lower highs as a universal rule | **REJECTED as canonical**; retained as example observation |
| M1/M5 as mandatory timeframe | **NOT CONFIRMED** |
| MA60 as mandatory gate | **NOT CONFIRMED** |
| Session/time windows as mandatory gates | **NOT CONFIRMED** |

## Important discrimination

The transcript is unusually explicit that the method is observed at the candle level, but it does **not** provide a complete machine-readable coordinate specification. In particular, the statement that classical AB=CD normally uses A/B/C while this method works "at candle level" does not itself tell us which OHLC field is each anchor.

Likewise, the presence of a pending-limit order does not establish that the limit price equals geometric C, a 50% retracement, a candle open/close, or any other candidate. Those remain competing research hypotheses until direct source evidence resolves them.

The same restriction applies to P-GAP: the transcript establishes that P-GAP is meaningful and associated with valid/early directional movement, but the transcript evidence audited here does not establish a deterministic gap formula.

## G352 gate decision

**PASS — transcript audit completed for the currently available direct transcript.**

**SOURCE-RESOLUTION STATUS: PARTIALLY RESOLVED / GEOMETRY STILL BLOCKED.**

No historical optimization, parameter fitting, production change, or geometry freeze is authorized by this artifact.

## Reopen / next evidence

The source-resolution gate can reopen if a genuinely authoritative artifact supplies one or more of:

- annotated chart showing explicit A/B/C/D labels tied to OHLC fields;
- explicit P-GAP/E-GAP definition;
- explicit pending-limit coordinate;
- explicit SL anchor and offset;
- explicit TP formula;
- official visual/document material that maps the candle-level terminology to executable coordinates.

Until then, the deterministic engine must treat these fields as unresolved rather than guessing.
