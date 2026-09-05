# Strategy A — Poorsamadi Codification Specification v1

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Status:** Semantic codification draft — no Strategy A implementation changes

## 0. Purpose

This document converts the currently source-established Poorsamadi/SP2L concepts into a deterministic state-machine specification **without inventing missing numeric rules**.

The raw source remains authoritative. Where the source is descriptive but insufficient for deterministic coding, the rule is explicitly marked `UNKNOWN/TBD`.

This document is a specification for review. It is **not yet an implementation contract** and must not be used to silently rewrite the existing backtest.

## 1. Non-negotiable codification rules

1. Only information available at the current candle may affect the current state.
2. No future candle may retroactively define a prior state.
3. Every action must be reproducible for materially equivalent input.
4. Source facts and project assumptions must remain separate.
5. Missing numeric thresholds remain `UNKNOWN/TBD`.
6. Post-entry research findings do not redefine the pre-entry source strategy.
7. Multi-position/2X behavior is modeled separately from the single-position baseline until its complete rules are established.
8. Stop/target semantics must be separated from backtest execution mechanics.
9. Same-candle ambiguity must be handled conservatively once execution rules are implemented.
10. Historical research artifacts must remain unchanged.

---

# 2. State machine

Working deterministic lifecycle:

`RANGE → BREAKOUT → FOLLOW_THROUGH → SPIKE → CORRECTION → PENDING_ORDER → FILL → LEG_2 → EXIT`

With invalidation/cancellation branches:

`CORRECTION → INVALIDATED/CANCELLED`

`PENDING_ORDER → CANCELLED`

`FILL → STOP/INVALIDATION`

This is the current best structural model, not a claim that every state has already been numerically defined by the source.

---

# 3. State specifications

## S0 — RANGE / PRECONDITION

### Source meaning
The source describes a spike as a sharp directional movement **after a range** and says the range can be small and need not last for a long time.

### Required information
- Candle history available before the directional move.
- A candidate range/context from which the movement emerges.

### Entry condition
A range/context must be identifiable before the candidate strong movement.

### Exit condition
Price produces a source-compatible breakout/strong directional movement.

### Invalidation
`UNKNOWN/TBD` — exact range invalidation is not defined by the source.

### Deterministic status
`SOURCE-ESTABLISHED CONCEPT / NUMERIC TBD`

### Open definitions
- minimum candles;
- maximum candles;
- maximum range width;
- normalized vs absolute range width;
- whether range is defined by high/low, closes, bodies, or another structure.

**No numeric range threshold should be invented yet.**

---

## S1 — BREAKOUT

### Source meaning
A breakout is described as a candle closing beyond a relevant prior level. The source also gives an example of a candle closing above the previous high.

### Required information
- Relevant structural level established before the breakout candle.
- Current candle OHLC.

### Entry condition
For bullish direction:
`current.close > relevantResistance`

For bearish direction:
`current.close < relevantSupport`

### Exit condition
A follow-through/key-bar condition is observed or the candidate fails.

### Invalidation
`UNKNOWN/TBD` for the general breakout state.

### Deterministic status
`SOURCE-ESTABLISHED / LEVEL DEFINITION TBD`

### Important distinction
The current implementation uses the highest/lowest of a fixed five-candle lookback. The source does **not** establish that five-candle lookback as canonical.

Therefore:
`lookback = 5` is an implementation parameter, not a source fact.

---

## S2 — FOLLOW_THROUGH / KEY BAR

### Source meaning
The source describes breakout followed by a next candle / FT or key bar that cannot return into or overlap the prior area.

### Required information
- Breakout candle.
- Broken level.
- Next candle(s), as permitted by the final codification.

### Entry condition
A source-compatible follow-through occurs after breakout.

### Exit condition
FT is accepted and strong-movement/spike classification can continue.

### Invalidation
If the required follow-through fails, the candidate is not a valid spike branch.

### Deterministic status
`SOURCE-ESTABLISHED / EXACT TIMING AND OVERLAP TBD`

### Open definitions
- Is FT strictly the immediate next candle?
- Is one later candle ever allowed?
- What exactly constitutes “return into/overlap prior area”?
- Is the relevant area the broken level, breakout candle body, full range, or prior range?
- Are wicks or closes used for the no-return test?

The current `maxBarsAfterBreakout=2` must not be treated as canonical.

---

## S3 — SPIKE / STRONG MOVE

### Source meaning
Spike is a sharp movement after a range. The source discusses:
- directional structure such as successive higher lows/lower highs;
- candle overlap as information about movement strength/type;
- valid breakout as central to the spike-oriented branch;
- multiple strong-movement sequence variants involving breakout, FT and P-GAP;
- P-GAP as a distinct pressure-gap concept.

### Required information
- Prior range/context.
- Direction.
- Breakout/FT evidence where applicable.
- Directional candle structure.
- Gap/pressure evidence where applicable.

### Entry condition
A source-defined strong movement variant is recognized.

### Exit condition
Spike ends when the directional movement gives way to correction/pullback according to the final deterministic boundary.

### Invalidation
`UNKNOWN/TBD` until spike grammar is fully defined.

### Deterministic status
`SOURCE-ESTABLISHED CONCEPT / FORMAL GRAMMAR TBD`

### Accepted variants currently supported by source evidence
The source discusses several variants as expressions of the same strong-movement concept, including sequences where:
- breakout + FT precede structural higher lows/lower highs;
- structural higher lows/lower highs precede a gap/pressure movement;
- breakout/FT/P-GAP elements appear in different orderings.

Do not split these into separate strategy branches unless explicitly adopted after source review.

### Open definitions
- spike start boundary;
- spike end boundary;
- minimum directional structure;
- overlap calculation;
- P-GAP exact definition;
- whether all variants are equally eligible;
- minimum/maximum spike duration;
- minimum spike magnitude.

The current `maxCandles=8`, `minDirectionalFraction=0.50`, and `maxOverlapFraction=0.80` are **not source-established rules**.

---

## S4 — CORRECTION / FIRST PULLBACK

### Source meaning
After the directional movement, a correction occurs. In the demonstrated SP2L pattern, when the next candle begins correcting below the first relevant low (or above the corresponding high for a bearish setup), an order can be prepared.

The source also discusses first-pullback behavior as a common way to reach Leg 2.

### Required information
- Completed/recognized spike.
- First relevant structural low/high of the spike.
- Current candle OHLC.

### Entry condition
Bullish candidate: correction reaches/breaches the first relevant low.  
Bearish candidate: correction reaches/breaches the first relevant high.

### Exit condition
The correction reaches the order-placement level / pending-order state, or the setup becomes invalid.

### Invalidation
Exact general formula remains `TBD`.

### Deterministic status
`SOURCE-ESTABLISHED CONCEPT / EXACT BOUNDARY TBD`

### Critical dependency
The current code uses `spike.startPrice` as the first relevant level. That is only canonical if the Spike state defines `startPrice` exactly as the source's first relevant low/high.

---

## S5 — PENDING_ORDER

### Source meaning
The source explicitly demonstrates placing a limit order in advance when correction starts, at a structural level, with the distance from entry to SL known before activation.

### Required information
- Direction.
- Structural entry level.
- Structural invalidation/SL level.
- Current risk distance.
- Setup status.

### Entry condition
The source-defined correction/order condition is reached.

### Action
Create a pending order rather than assuming an immediate market entry.

### Exit conditions
1. Price reaches the limit level → `FILL`.
2. Setup becomes invalid → `CANCELLED`.
3. Risk distance becomes too large under the source's order-management rule → `CANCELLED/REPLACED`.

### Deterministic status
`SOURCE-ESTABLISHED / EXACT LEVEL AND RISK THRESHOLD TBD`

### Important rule
The source says the order can be placed before the next candle completes. Therefore implementation must preserve event timing and must not require a future candle close to create the pending order.

### Open definitions
- exact limit price;
- exact SL placement;
- whether entry is always limit or whether confirmation variants exist;
- exact “too large” risk-distance threshold;
- exact replacement behavior.

---

## S6 — FILL

### Source meaning
A pending limit order becomes an actual position when price reaches the entry level.

### Required information
- Pending order.
- Current candle high/low.
- Entry level.

### Entry condition
Price touches/crosses the pending limit level in the correct direction.

### Execution status
`SOURCE-COMPATIBLE / EXACT INTRABAR MECHANICS TBD`

### Important backtest rule
Once implementation begins, intrabar ambiguity must be handled explicitly. If a single candle can touch both entry and stop/target, the simulator must use a documented conservative ordering rule rather than hindsight.

---

## S7 — LEG 1

### Source meaning
Leg 1 is the first directional movement that is followed by correction. The source later expects Leg 2 to equal Leg 1.

### Required information
- Canonical spike start.
- Canonical spike end.
- Direction.

### Measurement
`UNKNOWN/TBD`

### Current implementation
The prototype measures:
`abs(last.close - first.open)`

This is **not source-proven**.

### Deterministic status
`SOURCE-ESTABLISHED CONCEPT / ENDPOINTS TBD`

### Open definitions
- start price: open, low/high, close, or another structural point;
- end price: close, high/low, or another structural point;
- whether Leg 1 includes the breakout candle and FT candle;
- whether P-GAP extension changes the endpoint.

No projection ratio optimization should occur before this is resolved.

---

## S8 — LEG 2

### Source meaning
After correction, the expected next directional leg is Leg 2, with the core relationship:

`Leg 2 ≈ Leg 1`

This is presented as an AB=CD-like relationship brought down to candle-level price action.

### Required information
- Direction.
- Canonical Leg 1 magnitude.
- Correction endpoint/entry reference.

### Projection
Conceptually:

Bullish:
`Leg2Target = correctionReference + Leg1Size`

Bearish:
`Leg2Target = correctionReference - Leg1Size`

### Deterministic status
`SOURCE-ESTABLISHED RELATIONSHIP / EXACT REFERENCE TBD`

The exact projection reference and tolerance are not yet established.

---

## S9 — EXIT / TP1 / TP2

### Source meaning
The source discusses TP1 and TP2 and indicates TP1 is generally preferred for this strategy in the demonstrated money-management context. It also emphasizes fixed planned exits and risk/reward discipline.

### Required information
- Position entry.
- SL.
- Leg 1 / Leg 2 projection.
- Position-management mode.

### Base candidate
TP1 is the primary exit candidate for the base single-position Strategy A until a fuller source extraction establishes otherwise.

### Deterministic status
`SOURCE-ESTABLISHED EXIT CONCEPT / EXACT FORMULA TBD`

TP2 remains a separate possible exit mode and must not be mixed silently into the same baseline population.

---

## S10 — INVALIDATION / STOP

### Source meaning
SL is structural, tied to the scenario's invalidating level. The source explicitly warns not to widen SL merely because the trade is moving against the trader.

### Required information
- Position direction.
- Structural invalidation level.

### Rule
Once the position is active, SL remains fixed according to the planned rule unless a separate source-defined management rule exists.

### Deterministic status
`SOURCE-ESTABLISHED PRINCIPLE / EXACT LEVEL + EXECUTION TBD`

### Important distinction
Semantic SL level and backtest execution must be separate.

The current code checks only candle close crossing the invalidation level. The source's examples refer to price reaching the level, so close-only behavior is not yet proven canonical.

---

## S11 — 2X / SECOND POSITION

### Source meaning
The source describes a second position entered after the first position has moved a defined amount toward its target. The example uses a target fraction and shows that the second entry can have a better effective reward.

### Required information
- First active position.
- Its target/risk geometry.
- Defined progress threshold.
- Second entry level.

### Deterministic status
`SOURCE-ESTABLISHED CONCEPT / FULL RULE TBD`

### Important architecture rule
2X must be represented as a **separate position event**, not silently merged into the original entry.

Until the dedicated second-position teaching is fully available, the base Strategy A single-position backtest should remain separate from 2X experiments.

---

# 4. Cross-cutting context

## Timeframe

Source explicitly discusses M1, M5 and M15. This establishes low-timeframe relevance but does not prove identical numeric rules across all three.

Status: `SOURCE-ESTABLISHED / TIMEFRAME-SPECIFIC RULES TBD`

## Session / time of day

Source says time of day is part of a complete strategy. Current London/New York windows are implementation/research parameters, not source-proven rules.

Status: `SOURCE-ESTABLISHED CONCEPT / WINDOWS TBD`

## EMA / moving-average context

Source allows SP2L to be used as a trigger layered onto other concepts such as moving averages, cycles or channels. This does not prove EMA-60 is a canonical Poorsamadi requirement.

Status: `CONTEXT CONCEPT / CURRENT NUMERIC RULE NOT SOURCE-PROVEN`

## Round-number location

Current round-number parameters are implementation/research context. They are not established as mandatory source rules by the reviewed transcript.

Status: `UNKNOWN/TBD`

---

# 5. Current prototype → v1 mapping

| Current component | v1 state | Decision |
|---|---|---|
| BreakoutDetector | BREAKOUT | Retain concept; revisit level definition |
| FollowThroughDetector | FOLLOW_THROUGH | Redesign after exact FT semantics |
| SpikeDetector | SPIKE | Major rewrite required |
| CorrectionDetector | CORRECTION | Rebuild after canonical spike boundary |
| EntryTrigger | PENDING_ORDER + FILL | Replace abstraction; current close-reclaim is not canonical |
| LegProjection | LEG 1 + LEG 2 | Split measurement from projection |
| Invalidation | INVALIDATION/SL | Separate semantic level from execution |
| Context | CONTEXT | Keep source facts separate from research assumptions |
| QualityScore | RESEARCH FILTER | Do not present as source-defined strategy logic |

---

# 6. Confirmed conflicts requiring implementation later

### C-001 — Entry architecture
Current implementation waits for a post-correction candle close to reclaim the correction extreme. Source demonstrates a pending limit order being placed during correction and activated when price reaches the level.

**Status:** Confirmed conflict.

### C-002 — Spike detector semantics
Current implementation constructs a fixed window around breakout + FT and applies arbitrary directional/overlap thresholds. Source requires a preceding range and describes structural/sequence variants and P-GAP context.

**Status:** Confirmed semantic conflict/gap.

### C-003 — Leg 1 formula
Current implementation uses first open to last close. Source establishes Leg2=Leg1 conceptually but does not establish this exact endpoint formula.

**Status:** Unresolved implementation assumption; do not call canonical.

### C-004 — Close-only invalidation
Current implementation treats close crossing the level as invalidation. Source examples treat reaching the structural level as invalidation/SL behavior.

**Status:** Execution-semantic conflict requiring explicit backtest rule.

---

# 7. What is deliberately NOT specified in v1

The following remain `UNKNOWN/TBD`:

- exact range definition;
- breakout level algorithm;
- exact FT timing;
- exact no-return/overlap rule;
- exact P-GAP formula;
- spike duration threshold;
- spike size threshold;
- spike overlap threshold;
- exact higher-low/lower-high grammar;
- exact Leg 1 endpoints;
- correction tolerance/depth;
- exact limit-entry level;
- exact SL offset/placement;
- exact risk-distance cancellation threshold;
- exact Leg 2 projection reference;
- projection tolerance;
- exact TP1 formula;
- exact TP2 formula;
- complete 2X rule;
- session windows;
- timeframe-specific parameter differences;
- spread/slippage assumptions.

These are not omissions to be filled by optimization. They require additional source evidence, an explicit project assumption, or a separately labeled research hypothesis.

---

# 8. Implementation gate

**Do not modify Strategy A implementation from this document yet.**

Implementation may begin only after review confirms:

1. which v1 states are accepted;
2. which remaining unknowns may be explicit project assumptions;
3. exact execution semantics for pending orders/fills/stops;
4. exact Leg 1/Leg 2 geometry;
5. test cases for every adopted rule.

After implementation, the corrected strategy must be reconstructed and validated independently:

`DEV → VAL → Fresh Holdout`

Previous DELAY1/T1 research remains historical evidence about the previous implementation and must not be merged into the corrected source model.
