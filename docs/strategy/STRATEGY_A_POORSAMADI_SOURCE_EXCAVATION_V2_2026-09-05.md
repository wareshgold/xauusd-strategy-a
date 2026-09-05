# Strategy A — Poorsamadi Source Excavation v2

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Status:** Source-extraction update — no Strategy A implementation changes

## Purpose

This document records additional rules and constraints extracted directly from the preserved Poorsamadi source after the initial semantic audit and Codification Specification v1.

The goal is to reduce `UNKNOWN/TBD` items without inventing rules. A statement is classified as **source-established** only when the transcript explicitly supports it. Numeric examples are not automatically promoted to universal canonical parameters.

---

# 1. Breakout + Follow-Through: stronger evidence

## 1.1 Breakout is close-based

The source explicitly gives the example of a candle closing above the previous high and identifies that as a breakout/trend event.

**Source evidence:** approximately 20:37–20:48 and 32:21–32:28.

**Deterministic rule supported:**

Bullish:
`current.close > relevant prior high/level`

Bearish:
`current.close < relevant prior low/level`

The exact definition of `relevant prior level` remains unresolved.

## 1.2 Follow-through is specifically the next candle in the demonstrated pattern

At approximately 31:02–31:18 the source describes a valid breakout as a candle closing beyond a level and the **next candle** acting as FT/key bar while failing to return into/overlap the prior area.

At approximately 33:51–34:35 the source again describes the sequence as breakout followed by a signal/key bar or FT, and discusses whether the first/second candle relationship creates a pressure gap.

### Consequence

The current `maxBarsAfterBreakout=2` is not source-established. The source strongly supports an **immediate-next-candle FT interpretation for the demonstrated SP2L branch**, but we should still verify whether later material permits a delayed FT generally.

**Status:** `SOURCE-STRONG / GENERALIZATION TBD`

---

# 2. No-return / overlap semantics

The source makes overlap a classification signal rather than merely a numerical strength score.

It explains that when the second candle overlaps the first, the movement can behave more like a channel; when the follow-through cannot overlap/return into the previous area, it is treated as a valid breakout/spike-oriented structure.

**Source evidence:** approximately 29:43–30:48 and 31:02–31:29.

### Deterministic implication

The future implementation must distinguish at least:

- valid breakout + non-return FT;
- overlapping/channel-like movement;
- spike-oriented movement.

The existing average overlap ratio is not equivalent to this source concept.

**Status:** `SOURCE-ESTABLISHED CONCEPT / EXACT GEOMETRY TBD`

---

# 3. Spike grammar: three explicitly described strong-movement variants

The source explicitly summarizes three cases around 33:37–36:05.

## Variant A

`BREAKOUT → FT → higher lows/lower highs continuation`

## Variant B

`higher lows/lower highs → pressure gap (P-GAP)`

## Variant C

A short structural sequence where the directional low/high is formed and the following candle reverses rather than continuing the extension.

The teacher says these are conceptually the same strong-movement family for the current strategy and could be split into separate strategies later, but **should not be split now**.

### Consequence

The spike detector should eventually represent a common strong-movement family with variant metadata rather than silently using a single overlap/directional-fraction score.

**Status:** `SOURCE-ESTABLISHED FAMILY + VARIANTS / EXACT FORMAL GRAMMAR TBD`

---

# 4. Spike starts from a range, and range can be short

The source defines a spike as a sharp move after a range and explicitly says the range does not need to be long; a few candles can constitute the relevant range context.

It also demonstrates that the range can contain imperfect candles and even an occasional full-body candle while still behaving as a range/context.

**Source evidence:** approximately 26:30–27:20 and 45:02.

### What is established

- A range/context precedes the spike.
- The range may be candle-level and short.
- A long-duration consolidation is not mandatory.

### What remains TBD

- minimum/maximum number of candles;
- exact range width;
- whether width is absolute or normalized;
- body-vs-wick construction;
- exact boundary selection.

**Status:** `SOURCE-ESTABLISHED CONCEPT / NUMERIC TBD`

---

# 5. Higher-low / lower-high structure is explicitly important

The source repeatedly describes strong directional movement using successive higher lows in bullish movement and successive lower highs in bearish movement.

At approximately 27:51–28:29, this is presented as a primary way a strong movement can develop. At 32:44–33:23 the same structure is used in an actual trading example.

### Deterministic implication

The implementation must eventually identify structural sequences such as:

Bullish:
`L1 < L2 < L3 ...`

Bearish:
`H1 > H2 > H3 ...`

But the minimum count is not universally established by the source. Three candles are used illustratively elsewhere, but the transcript explicitly presents multiple counts and examples.

**Status:** `SOURCE-ESTABLISHED CONCEPT / MINIMUM COUNT TBD`

---

# 6. P-GAP is not simply "any gap"

The source explicitly distinguishes P-GAP from E-GAP, Common-GAP and morning gap, and says location is important in distinguishing them.

At approximately 31:43–32:12, P-GAP is described as a pressure gap and explicitly separated from other gap categories.

At approximately 34:14–35:37, P-GAP is used as a visual marker of the strong-movement sequence.

### Deterministic implication

`hasPGAPEvidence = false` is not a canonical implementation of the source. The final model should either implement a source-grounded P-GAP definition or keep it explicitly unknown.

The transcript available here does not provide a safe numeric P-GAP formula.

**Status:** `SOURCE-ESTABLISHED CONCEPT / FORMULA TBD`

---

# 7. Correction boundary and pending order: strong evidence

The source gives a much stronger description than the initial audit alone.

At approximately 38:18–38:53:

- a bullish spike is represented by successive higher lows;
- when the next candle **starts correcting below the first low**, an order can be placed;
- the order can be manual or a pre-defined limit order.

This directly supports a structural correction boundary tied to the first relevant low/high of the spike.

### Deterministic implication

For the bullish SP2L example:

`correction begins when price moves below first relevant spike low`

For the bearish mirror:

`correction begins when price moves above first relevant spike high`

The exact definition of "first relevant" still depends on canonical Spike/Leg 1 boundaries.

**Status:** `SOURCE-STRONG / BOUNDARY DEPENDENCY REMAINS`

---

# 8. Pending limit order is a real source behavior, not an optional interpretation

At approximately 38:38–40:22, the source explains that the trader can place the order in advance, including a limit order, while the correction is developing.

The source also says the distance between limit entry and SL is known before activation.

If the setup changes and the risk distance becomes too large, the order can be deleted and a new one placed.

### Confirmed architecture requirement

The machine model needs separate events/states for:

`SETUP ELIGIBLE`
→ `PENDING ORDER`
→ `FILL`

and must not require a future candle close to create the pending order.

### Still unknown

The source excerpt does not give a universal numeric threshold for "too large" risk distance.

**Status:** `SOURCE-ESTABLISHED / NUMERIC RISK THRESHOLD TBD`

---

# 9. Entry level: current close-reclaim implementation is definitely not canonical

The current prototype waits for a post-correction candle close to reclaim the correction extreme.

The source instead demonstrates pre-positioning the limit order around the structural level created by the spike/correction sequence.

Therefore the current `CORRECTION_EXTREME_RECLAIM` close-entry rule must be treated as an implementation-specific research rule, not the source-canonical entry.

**Status:** `CONFIRMED CONFLICT`

---

# 10. Leg 1 / Leg 2: relationship confirmed, exact endpoints still unresolved

At approximately 36:59–38:05 the source explicitly states:

- a spike creates the first directional leg;
- a correction follows;
- the expected second leg completes at a magnitude equal to the first leg.

Conceptually:

`Leg2 magnitude = Leg1 magnitude`

This is the core SP2L relationship.

However, the transcript does not establish that Leg 1 should be measured as:

`first candle open → last candle close`

Therefore the current `LegProjection.ts` formula remains an implementation assumption.

### Required next extraction

Determine whether the source examples imply endpoints based on:

- first structural low/high;
- breakout level;
- spike extreme;
- candle open/close;
- or another structural reference.

**Status:** `SOURCE-ESTABLISHED RELATIONSHIP / ENDPOINTS TBD`

---

# 11. TP1 vs TP2: useful source evidence

At approximately 42:26–42:48, the source states that take profits can be TP1 or TP2 and explicitly says the teacher generally uses TP1 for this strategy because the stop is relatively larger and TP2 is less suitable.

### Important distinction

This establishes a **preference/example**, not necessarily a universal prohibition of TP2.

For the base research population, TP1 should therefore remain a clearly separated exit mode. TP2 must not silently replace TP1.

**Status:** `SOURCE-ESTABLISHED PREFERENCE / EXACT TP FORMULA TBD`

---

# 12. 2X trigger: stronger numeric evidence

At approximately 22:43–23:10 and 41:53–42:17, the source gives a concrete 2X example.

The second position is entered when the first trade reaches **half of its target**.

The second position has its own entry and stop/risk, and because its entry is later/better, the effective reward can be larger.

The source explicitly presents a separate 2nd-position money-management teaching.

### Deterministic rule supported by this source

`2X trigger = first position reaches 50% of its target`

### What remains separate/TBD

- exact second-entry level;
- whether this is always a limit/market entry;
- exact second-position SL;
- whether every SP2L setup permits 2X;
- aggregation and exit rules;
- whether 2X is part of the base strategy or an optional management overlay.

**Status:** `SOURCE-STRONG FOR 50% PROGRESS TRIGGER / FULL RULE TBD`

---

# 13. 2X must remain a separate position

The source explicitly discusses two separate trades with different entry levels and then discusses their combined average/effective outcome.

Therefore the backtest should not merge the two into one synthetic trade.

Each position needs its own:

- entry;
- stop;
- risk amount;
- target;
- activation timestamp/index;
- outcome.

A separate portfolio-level aggregation can then calculate the combined result.

**Status:** `SOURCE-ESTABLISHED ARCHITECTURAL REQUIREMENT`

---

# 14. Money-management scaling is explicitly adaptive to setup quality

At approximately 54:10 the source describes reducing risk when the probability/quality of the setup is lower, e.g. 2% → 1% or 1% → 0.5%, while still taking a directional trigger.

This is important, but it is not yet a deterministic Strategy A rule because the transcript does not define a numeric mapping from setup quality to risk percentage.

### Decision

Do not implement a risk-percentage optimizer from this statement.

Record the concept as:

`setup quality may alter position risk`

with the actual mapping `TBD`.

---

# 15. Round-number context: source provides actual gold examples

At approximately 43:21–44:29 the source explicitly discusses round/trend levels for gold, with examples around 3200, 3250, 3255 and very fine scalping levels such as 3257.5.

It then states that trend-number separation can be done by:

- 250 points;
- 500 points;
- 1000 points;

depending on trading style/time horizon.

### Critical distinction

This is stronger evidence than the initial audit suggested, but it still does **not** prove that the project's current:

`roundStep = 50`

is the intended canonical Strategy A parameter.

In fact, the source examples make `50` look inconsistent with the stated 250/500/1000 point grouping unless the project's point/price-unit conversion is different.

### Decision

Do not change the current baseline yet. Instead, resolve the instrument's point definition and map the source's gold-number examples to actual XAUUSD price units.

**Status:** `SOURCE-ESTABLISHED CONTEXT / UNIT MAPPING REQUIRED`

---

# 16. Moving average as equilibrium/context

At approximately 51:25–51:31, the source calls the moving average the market's "equilibrium price" and describes waiting for price to return to it before making decisions in the illustrated context.

This establishes that moving-average context can be meaningful in the broader strategy framework.

It does **not** establish EMA period 60 as canonical.

**Status:** `SOURCE-ESTABLISHED CONTEXT / PERIOD TBD`

---

# 17. Session/time-of-day is real, but exact windows are not yet canonical

The source explicitly states that time of day is part of strategy and gives concrete examples:

- activity from around 07:00 onward in the demonstrated M1 sequence;
- European/Frankfurt/London opening around 09:00 local chart time in the example;
- separate discussion of London and New York timing strategies.

At approximately 52:29–52:50 the source explicitly says time analysis can be separated by London and New York sessions.

### Decision

The concept is source-established, but the current UTC windows:

- London 07:00–16:00;
- New York 13:00–22:00;

remain project parameters until timezone/chart-time conventions are confirmed.

**Status:** `SOURCE-ESTABLISHED CONCEPT / EXACT WINDOWS TBD`

---

# 18. Clean vs dirty market context is source-relevant

At approximately 54:36–56:20, the source repeatedly distinguishes "clean" market structure from messy/ranging/choppy candle behavior.

The teacher recommends trading cleaner structures and says that messy candle behavior signals lower-quality conditions. He also notes that very advanced traders may still trade inside messy areas.

### Deterministic implication

A future quality/context model may legitimately include a market-cleanliness state, but the transcript does not define a safe numeric cleanliness score.

The current `QualityScore` therefore should not be presented as the teacher's formula.

**Status:** `SOURCE-ESTABLISHED CONCEPT / NUMERIC MODEL TBD`

---

# 19. Source-grounded rule ledger update

| Rule | New evidence | Current status |
|---|---|---|
| Breakout close | Explicit | SOURCE-ESTABLISHED |
| Immediate FT | Strongly demonstrated | SOURCE-STRONG / generalization TBD |
| No-return/overlap | Explicit | SOURCE-ESTABLISHED / geometry TBD |
| Spike after range | Explicit | SOURCE-ESTABLISHED |
| Higher lows/lower highs | Explicit | SOURCE-ESTABLISHED / count TBD |
| 3 strong-movement variants | Explicit | SOURCE-ESTABLISHED family |
| P-GAP distinct from other gaps | Explicit | SOURCE-ESTABLISHED / formula TBD |
| Correction below first low / above first high | Explicit example | SOURCE-STRONG |
| Pending limit order | Explicit | SOURCE-ESTABLISHED |
| Risk distance known before fill | Explicit | SOURCE-ESTABLISHED |
| Cancel/re-place if risk becomes too large | Explicit | SOURCE-ESTABLISHED / threshold TBD |
| Leg2 equals Leg1 | Explicit | SOURCE-ESTABLISHED |
| TP1 preferred | Explicit | SOURCE-ESTABLISHED preference |
| 2X at 50% target progress | Explicit example | SOURCE-STRONG |
| 2X separate position | Explicit | SOURCE-ESTABLISHED |
| Risk scaling with quality | Explicit concept | NUMERIC TBD |
| Round levels 250/500/1000 points | Explicit gold context | SOURCE-ESTABLISHED context / unit mapping TBD |
| Moving average as equilibrium | Explicit | SOURCE-ESTABLISHED context |
| London/New York timing matters | Explicit | SOURCE-ESTABLISHED concept / windows TBD |
| Clean vs dirty market | Explicit | SOURCE-ESTABLISHED concept / formula TBD |

---

# 20. Immediate implementation blockers removed

The following items now have enough source evidence to move from pure `UNKNOWN` to source-grounded codification work:

1. Breakout is close-based.
2. The demonstrated FT is the immediate next candle.
3. FT must not return/overlap the prior area in the demonstrated spike branch.
4. Spike follows a range/context.
5. Higher-low/lower-high sequences are a core strong-movement representation.
6. Multiple strong-movement variants belong to one current family.
7. Correction can be recognized when price moves through the first relevant low/high.
8. A pending limit order can be created before correction completes.
9. Fill is a separate event from order placement.
10. Leg 2 is expected to equal Leg 1.
11. TP1 is the preferred base exit in the demonstrated strategy.
12. 2X has a concrete 50%-of-target progress trigger in the example.
13. 2X is a separate position.

---

# 21. Remaining highest-priority unknowns

The next source-extraction pass should focus on only these items:

### P0
- exact structural level used for breakout;
- exact P-GAP geometry;
- exact first-low/high definition;
- exact Leg 1 endpoints;
- exact pending limit entry price;
- exact SL placement;
- exact fill/cancel ordering.

### P1
- exact spike start/end;
- minimum structural higher-low/lower-high count;
- exact correction endpoint;
- exact Leg 2 projection reference;
- exact TP1 formula;
- exact 2X second-entry and SL rules.

### P2
- exact round-level unit conversion;
- exact EMA period/context;
- exact London/New York windows;
- numeric market-cleanliness criteria;
- timeframe-specific differences M1/M5/M15.

---

# 22. Research boundary

None of the above source findings changes the historical Strategy A research results.

The existing DELAY1/T1 research remains evidence about the prior deterministic implementation. It must not be mixed into the semantic source reconstruction.

No production rule is promoted by this document.
