# SP2L Multi-Stage Source Resolution — 2026-09-08

## Scope

This research pass resolves several linked questions without promoting unresolved geometry into the canonical Strategy A specification:

1. relevant candle for Entry during correction;
2. separation of P-Gap from Entry;
3. structural SL anchor;
4. Leg-1 origin / magnitude;
5. AB=CD implementation boundary;
6. cross-check against the public TradingView implementation description.

The authoritative hierarchy remains: source video/transcript > source visual evidence > source ledger > deterministic specification > implementation/research.

## Stage 1 — Entry reference candle

### Source evidence

The source video states that when the next candle starts correcting and moves below the first low in the bullish example, an order can be placed manually or as a pre-set limit. The later entry diagrams explicitly show a Buy Limit during the correction. The mirrored bearish explanation uses the previous high.

The official source wording also supports the semantic rule: bullish correction reaches the low of the previous candle; bearish correction reaches the high of the previous candle.

### Cross-check from public TradingView description

The public TradingView description says that in bullish SP2L, each previous low can be a potential Buy Entry and that the entry is activated when price returns to that level; the bearish mirror uses previous highs. It also describes consecutive HL/LH structures. This is useful secondary evidence, but the script is protected/closed-source and cannot establish the canonical formula.

### Resolution

**SOURCE-ALIGNED SEMANTIC:** correction reaches a relevant prior candle extreme; execution is a pending limit in the spike direction.

**STRONGEST CANDIDATE:** immediate/relevant previous candle Low for BUY and High for SELL.

**UNRESOLVED:** whether "relevant" always means the immediately preceding candle, the first candle of the correction, or a source-defined structural candle in every spike variant.

Do not freeze a universal candle index or generic swing algorithm.

## Stage 2 — P-Gap vs Entry

The video examples show P-Gap as a breakout-associated shaded gap/non-overlap region, while the entry diagram shows a separate correction/Entry line. The public TradingView description also separates the gap filter from the HL/LH entry structure.

### Resolution

**CONFIRMED SEMANTIC SEPARATION:** P-Gap is a breakout/spike validity concept; Entry is a correction-level execution concept.

Therefore these equations remain forbidden until source evidence proves them:

- Entry = P-Gap boundary
- Entry = FVG midpoint
- Entry = classical C
- Entry = 50% retracement

### P-Gap formula

Still unresolved. The source visuals do not uniquely establish wick-vs-body boundaries, equality/touch handling, minimum gap, or universal candle timing. Generic three-candle FVG remains rejected as a canonical assumption.

## Stage 3 — Structural SL anchor

The source video shows SL below the candle from which the bullish spike originated and the mirrored bearish placement above the spike-origin candle. The official source description independently states that SL is placed behind the candle where the spike originated, usually the lowest/highest point before the sharp move.

### Resolution

**SOURCE-ALIGNED SEMANTIC:** SL is structurally invalidated beyond the spike-origin candle.

**STRONGEST CANDIDATE:** BUY reference = low of spike-origin candle; SELL reference = high of spike-origin candle.

**UNRESOLVED:** exact executable price convention: wick vs body, strict beyond vs at-touch, tick/price buffer, spread handling, and exact origin identity across every accepted spike construction.

No numeric buffer is introduced.

## Stage 4 — Leg-1 origin and AB=CD

The source explicitly states that after the Spike, correction is expected and the second leg is expected to be the same size as the first leg. The source also explicitly contrasts its candle-level approach with classical internet AB/CD using A/B/C and Fibonacci. Therefore classical harmonic anchors must not be imported.

The strongest candidate remains:

`source-defined Spike-origin → source-defined Spike-extreme`

with mirrored bearish geometry.

### Resolution

**SOURCE CONFIRMED:** Leg 2 approximately/equally follows Leg 1 magnitude; AB=CD is a named source concept.

**STRONGEST CANDIDATE:** Leg 1 = spike-origin-to-spike-extreme.

**UNRESOLVED:** exact OHLC anchor, whether origin is wick/body price, whether the extreme is wick/body price, exact correction anchor for projection, and any numerical AB=CD tolerance.

No Fibonacci ratio, swing detector, or backtest-selected tolerance is introduced.

## Stage 5 — Public TradingView corroboration

The TradingView page is useful as external corroboration because it describes:

- Spike as a sharp directional movement;
- a gap/FVG consequence;
- previous lows/highs as potential entry levels;
- SL behind the spike-origin candle;
- TP1 1:1 and TP2 1:2 options;
- a configurable gap filter.

However, it is a protected third-party implementation description. It does not expose the actual source code or prove that its FVG implementation is identical to the source P-Gap. Therefore it remains secondary evidence only.

## Synthetic fixture matrix created by this pass

### ENTRY-M01 — immediate previous candle
Bullish correction reaches immediate previous candle Low. Candidate should select that Low.

### ENTRY-M02 — first-correction candle differs
Bullish correction contains multiple candles and the first correction candle Low differs from the immediately preceding candle Low. Candidate interpretations must disagree.

### ENTRY-M03 — bearish mirror
Bearish correction reaches the relevant previous High. BUY-only assumptions must fail.

### ENTRY-M04 — P-Gap/Entry separation
P-Gap zone and correction Entry level are numerically distinct. No implementation may collapse them.

### SL-M01 — origin wick vs body
Origin candle Low differs from its body Low. Exact executable SL remains unresolved.

### SL-M02 — origin identity competition
Spike-origin candle differs from breakout candle. No fixed breakout-index SL is allowed.

### LEG-M01 — origin-to-extreme vs breakout-to-extreme
The two candidate Leg-1 measurements differ. No implementation may silently select one.

### LEG-M02 — wick vs body extreme
Leg-1 magnitude differs depending on wick/body. Both remain unresolved.

### ABCD-M01 — no classical Fibonacci import
Classical A/B/C points are supplied but are intentionally unrelated to the source candle-level sequence. The source-aligned engine must not infer them.

### ABCD-M02 — tolerance boundary
Leg2 differs slightly from Leg1. No acceptance threshold is assumed.

## Gate decision

SOURCE RESOLUTION: **advanced, not complete**.

FROZEN GEOMETRY: **BLOCKED**.

DEV / VAL / Fresh Holdout: **remain locked**.

PRODUCTION: **unchanged**.

The current safest semantic model is:

`Range/context → valid breakout + source-defined P-Gap → Spike → correction → relevant prior Low/High → pending-limit entry → structural invalidation at spike-origin candle → second leg with source-confirmed equal-leg relationship.`

Only the semantics above may be carried forward. Exact P-Gap geometry, exact relevant candle selection, exact SL price, exact Leg-1 OHLC anchors, and AB=CD tolerance remain unresolved.
