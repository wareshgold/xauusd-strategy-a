# SP2L F17 — B1–B3 Source Triangulation V1 — 2026-09-09

## Scope

Target blockers: B1 P-Gap geometry, B2 relevant Low/High and pending Entry anchor, B3 structural Stop/Loss anchor.

Evidence was checked against direct source frames from the uploaded primary video, including the P-Gap teaching segment (~31:43–36:10) and the entry/SL sequence (~38:18–39:50), plus the later Entry/SL/TP diagram (~45:40–46:40).

## B1 — P-Gap

### Direct observations

- The source explicitly distinguishes P-Gap from E-Gap/Common-Gap concepts.
- Multiple candle constructions are shown and annotated as P-Gap / valid breakout examples.
- Around ~35:35 the source annotation explicitly marks P-GAP across several constructions while also rejecting at least one construction.
- Around ~36:46 the slide states `Valid BO = P-Gap` alongside the `AB=CD` concept.

### Decision

**P-Gap concept: CONFIRMED.**

**Generic three-candle imbalance/FVG formula: REJECTED as a source substitute.**

**Exact P-Gap price/candle boundary: UNRESOLVED.**

The frames demonstrate source-marked constructions but do not provide a sufficiently explicit universal OHLC formula to freeze a detector without interpretation.

## B2 — Entry anchor

### Direct observations

- Around ~38:18 the source marks the bullish structure and discusses higher lows/correction.
- Around ~38:54 a horizontal level is drawn with an explicit `Limit` annotation.
- Around ~39:30 the source explicitly writes `Buy Lim` and the pending line is at a structural level inside the developing sequence.
- Around ~39:45 the source explicitly labels `Buy Limit` and separately labels `SL` below.
- Later diagrammatic examples (~45:40–46:40) show separate Entry and SL levels, with Entry above the structural base in the bullish example.

### Decision

**Pending Limit entry: CONFIRMED.**

**Entry is distinct from Leg-2 start: CONFIRMED.**

**Fixed original Spike low as a universal Entry anchor: NOT CONFIRMED.**

**Latest completed Higher-Low as a universal Entry rule: PLAUSIBLE but NOT UNIQUELY CONFIRMED.**

Current frozen-safe abstraction remains:

`Relevant Structural Low/High → Pending Limit`

No Fibonacci retracement, market-close reclaim, wick/body proxy, or arbitrary percentage level is authorized.

## B3 — Structural SL anchor

### Direct observations

- Around ~39:45 the source separately labels `SL` below the Buy Limit level.
- The later Entry/SL/TP diagram explicitly presents separate `Entry` and `SL` levels.
- The source discussion frames the stop as structural invalidation and discusses order management when structural risk distance changes.

### Decision

**Structural invalidation separate from Entry: CONFIRMED.**

**Exact OHLC anchor: UNRESOLVED.**

The current candidate family remains:

- wick extreme;
- body edge;
- structural pivot/base low or high.

The source frames do not uniquely label which OHLC component is canonical in every variant. No stop buffer is frozen.

## B1–B3 outcome

| Blocker | Result | Frozen? |
|---|---|---|
| B1 P-Gap concept | Confirmed | No — geometry unresolved |
| B2 Entry model | Pending Limit confirmed; relevant structural anchor candidate | No |
| B3 SL model | Structural invalidation confirmed | No — exact anchor unresolved |

## Gate impact

**F17 SYNTHETIC DISCRIMINATION: PASS**

**SOURCE RESOLUTION: PARTIAL PASS**

**FROZEN GEOMETRY: BLOCKED**

F17 reduces ambiguity but does not justify inventing a P-Gap formula, Entry anchor, or SL OHLC rule.

## Next targeted action

Move to B4–B6: trigger acceptance, AB=CD operational anchors/tolerance, and Leg1/Leg2/TP1 geometry. Use the same source-frame → candidate → fixture → discrimination process.
