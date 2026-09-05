# Strategy A — Poorsamadi Codification Specification v2

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Status:** Research specification only — no Strategy A implementation changes

## 1. Purpose

This specification converts the source-excavation findings into a deterministic state model without inventing missing teacher rules.

The raw Poorsamadi transcript remains the semantic authority. Existing Strategy A code remains evidence of the current implementation, not evidence of teacher intent.

Rules are classified as:

- `SOURCE-ESTABLISHED`: explicitly supported by the source.
- `SOURCE-STRONG`: strongly demonstrated but still requires scope/generalization caution.
- `IMPLEMENTATION-ASSUMPTION`: current code behavior that is not source-proven.
- `TBD`: insufficient source information; must not be fitted silently.
- `RESEARCH-CANDIDATE`: a deterministic hypothesis that may be tested, but is not canonical.

---

# 2. Canonical conceptual lifecycle

The source-grounded SP2L lifecycle is:

```text
RANGE / CONTEXT
    ↓
BREAKOUT / STRONG-MOVE INITIATION
    ↓
FOLLOW-THROUGH (source-demonstrated immediate next bar)
    ↓
SPIKE FAMILY
    ├── breakout → FT → structure
    ├── structure → P-GAP
    └── other source-described strong-move variant
    ↓
FIRST STRUCTURAL LOW/HIGH
    ↓
CORRECTION BEGINS
    ↓
PENDING LIMIT ORDER
    ↓
FILL
    ↓
FIXED STRUCTURAL STOP
    ↓
LEG 2 ≈ LEG 1
    ↓
TP1 BASE EXIT
    ↓
OPTIONAL SEPARATE 2X POSITION
```

This lifecycle is semantic. It is not yet an executable implementation contract because several geometric definitions remain unresolved.

---

# 3. State S0 — RANGE / CONTEXT

## Source meaning

A spike is described as a sharp directional movement occurring after a range. The range can be short and candle-level; a long consolidation is not required.

## Deterministic requirement

A candidate spike must have an identifiable preceding context that satisfies a future, explicitly defined range predicate.

## Not yet defined

- minimum candles;
- maximum candles;
- absolute range width;
- normalized range width;
- wick/body treatment;
- boundary selection.

## Status

`SOURCE-ESTABLISHED CONCEPT / NUMERIC TBD`

No arbitrary range threshold is promoted from current code.

---

# 4. State S1 — BREAKOUT

## Source meaning

A candle closing above a relevant prior high is explicitly described as breakout/trend; bearish symmetry is below a relevant prior low.

## Source-grounded expression

Bullish:
`close[t] > priorRelevantHigh`

Bearish:
`close[t] < priorRelevantLow`

## Unresolved

`priorRelevantHigh/Low` has not yet been formally defined.

The existing five-candle lookback is therefore an implementation assumption, not canonical source truth.

## Status

`SOURCE-ESTABLISHED EVENT / LEVEL ALGORITHM TBD`

---

# 5. State S2 — FOLLOW-THROUGH

## Source meaning

The demonstrated breakout pattern uses the next candle as FT/key bar. It must not simply return into/overlap the prior area.

## Research baseline candidate

For the SP2L branch under study:

`FT.index = BREAKOUT.index + 1`

and FT must satisfy a source-grounded no-return/non-overlap predicate once exact geometry is defined.

## Important restriction

Do not retain the current `maxBarsAfterBreakout=2` as canonical merely because it already exists in code.

## Status

`SOURCE-STRONG / GENERALIZATION TBD`

---

# 6. State S3 — SPIKE FAMILY

## Source meaning

Spike means a sharp movement after range/context. Strong movement may be expressed through structural higher lows/lower highs, breakout + FT, and P-GAP-related sequences.

The source describes multiple variants as belonging to the same family for the current strategy.

## Required representation

The future detector should expose variant metadata rather than collapsing all movement into a single score.

Suggested semantic variants:

```text
BREAKOUT_FT_STRUCTURE
STRUCTURE_PGAP
OTHER_SOURCE_STRONG_MOVE
```

These labels are descriptive and are not independent strategy gates.

## Existing implementation conflict

The current detector's:

- `maxCandles`
- `minDirectionalFraction`
- `maxOverlapFraction`

are implementation assumptions. They may be used only as research candidate parameters until source geometry is established.

## Status

`SOURCE-ESTABLISHED FAMILY / FORMAL GRAMMAR TBD`

---

# 7. State S3a — P-GAP

## Source meaning

P-GAP is explicitly distinguished from E-GAP, Common-GAP and morning gap and is used as evidence of pressure/strong movement.

The source gives sequences including:

`BREAKOUT → FT → P-GAP`

and

`HIGHER-LOW / LOWER-HIGH STRUCTURE → P-GAP`

## What is safe to codify now

`P-GAP` is a named semantic feature inside the spike family.

## What is NOT safe to codify

The transcript does not provide enough information to define whether the gap is measured between:

- full candle ranges;
- bodies;
- specific high/low boundaries;
- closes/opens;
- or a combination.

Wick tolerance is also unresolved.

## Status

`SOURCE-ESTABLISHED CONCEPT / EXACT FORMULA TBD`

Do not fabricate a gap formula.

---

# 8. State S3b — STRUCTURAL DIRECTION

## Source meaning

Bullish strong movement is repeatedly represented by successive higher lows. Bearish movement is represented by successive lower highs.

## Semantic invariant

Bullish structural sequence:
`L1 < L2 < L3 ...`

Bearish structural sequence:
`H1 > H2 > H3 ...`

## Unresolved

The transcript does not establish a universal minimum count. Three candles appear in examples but are not promoted to a hard requirement.

## Status

`SOURCE-ESTABLISHED CONCEPT / MINIMUM COUNT TBD`

---

# 9. State S4 — CORRECTION

## Source meaning

In the demonstrated bullish sequence, correction begins when price starts moving below the first relevant low. Bearish symmetry uses the first relevant high.

## Source-grounded candidate

Bullish:
`correctionReference = firstStructuralLow`

Bearish:
`correctionReference = firstStructuralHigh`

`correctionBegins` occurs when price reaches/crosses that structural boundary according to the eventual simulator execution policy.

## Dependency

The exact `firstStructuralLow/High` depends on the finalized spike grammar.

## Status

`SOURCE-STRONG / STRUCTURAL ALGORITHM DEPENDENT`

---

# 10. State S5 — PENDING LIMIT ORDER

## Source meaning

The source explicitly describes placing the order before the correction candle has completed. A predefined limit order can be waiting for price to reach the structural entry level.

## Source-grounded event sequence

```text
SPIKE RECOGNIZED
→ CORRECTION BEGINS
→ PENDING_LIMIT_CREATED
→ PRICE REACHES LIMIT
→ FILL
```

## Base research candidate

Bullish:
`BUY LIMIT = firstStructuralLow`

Bearish:
`SELL LIMIT = firstStructuralHigh`

This candidate matches the demonstrated structural logic but remains dependent on the final definition of first structural low/high.

## Explicit conflict with current code

The current `CORRECTION_EXTREME_RECLAIM` close-entry trigger is not source-canonical.

## Status

`SOURCE-ESTABLISHED EVENT MODEL / EXACT LEVEL DEPENDENT`

---

# 11. State S5a — ORDER REPLACEMENT

## Source meaning

If subsequent candles change the setup so that entry-to-stop distance becomes too large, the existing pending order can be deleted and a new order placed with adjusted sizing.

## Deterministic requirement

A future implementation must support:

`PENDING_ORDER_ACTIVE`
→ `RISK_DISTANCE_INVALID`
→ `ORDER_CANCELLED`
→ optional `REPLACEMENT_ORDER_CREATED`

## Missing parameter

The source does not establish a universal numeric maximum risk distance.

## Status

`SOURCE-ESTABLISHED BEHAVIOR / THRESHOLD TBD`

Do not optimize this threshold against VAL or fresh holdout before a source-independent research protocol is approved.

---

# 12. State S6 — FILL / EXECUTION

## Source meaning

The pending limit becomes an active trade when price reaches the limit level.

## Simulator policy still required

- intrabar touch semantics;
- OHLC ambiguity;
- spread/slippage;
- exact same-candle ordering when limit and stop are both reachable;
- whether a correction candle can both create and fill the order.

These are execution policies, not teacher semantics, and must be frozen before comparative backtests.

## Status

`SOURCE-ESTABLISHED EVENT / SIMULATOR POLICY TBD`

---

# 13. State S7 — STOP / INVALIDATION

## Source meaning

The stop is structural. The entry-to-stop distance is known before activation, and the risk should not simply be widened because price moves against the trade.

## Base semantic rule

`SL = fixed structural invalidation level`

## Important distinction

The source meaning does not by itself resolve whether the simulator treats invalidation as:

- intrabar touch;
- candle close;
- or broker-style stop execution.

The current close-only implementation is therefore not declared canonical.

## Status

`SOURCE-ESTABLISHED SEMANTIC RULE / EXECUTION TBD`

---

# 14. State S7a — LEG 1

## Source meaning

The first directional movement is Leg 1.

## Confirmed relationship

Leg 2 is expected to reproduce approximately the magnitude of Leg 1.

## Unresolved endpoint candidates

Potential references include:

- first structural low/high;
- breakout level;
- spike extreme;
- first candle open;
- final directional close;
- another structural A/B endpoint.

No one candidate is source-proven by the transcript.

## Status

`SOURCE-ESTABLISHED CONCEPT / ENDPOINTS TBD`

The existing `first.open → last.close` implementation remains a research assumption.

---

# 15. State S8 — LEG 2

## Source meaning

SP2L expresses AB=CD at candle-level price action: after the correction, the expected second leg is approximately equal to the first leg.

## Semantic invariant

`Leg2Magnitude ≈ Leg1Magnitude`

## Unresolved

- projection origin;
- exact equality tolerance;
- whether target is exact equality or a zone;
- whether TP1 is the exact Leg2 completion or another predefined level.

## Status

`SOURCE-ESTABLISHED RELATIONSHIP / GEOMETRY TBD`

---

# 16. State S9 — TP1 / TP2

## Source meaning

The source distinguishes TP1 and TP2 and says TP1 is generally preferred for this strategy in the demonstrated context because the stop is comparatively large.

## Base research treatment

`TP1` remains the primary single-position exit candidate.

`TP2` is a separate exit mode and must not silently replace TP1.

## Status

`SOURCE-ESTABLISHED PREFERENCE / FORMULA TBD`

---

# 17. State S10 — 2X POSITION

## Source meaning

The second position is a separate trade. The source provides a concrete example where it is activated after the first position has progressed to half of its target.

## Source-strong trigger

`2X trigger = POSITION_1 reaches 50% of its target distance`

## Required separate fields

`POSITION_2.entry`

`POSITION_2.stop`

`POSITION_2.risk`

`POSITION_2.target`

`POSITION_2.activationIndex`

`POSITION_2.result`

## Still TBD

- exact second entry level;
- market vs limit mechanics;
- second-position stop;
- target;
- whether 2X is enabled for every setup;
- portfolio aggregation;
- whether 2X belongs to base strategy or optional money-management overlay.

## Status

`SOURCE-STRONG TRIGGER / FULL RULE TBD`

Do not merge 2X into the single-position baseline.

---

# 18. Context: round levels

The source provides gold-number examples and discusses 250/500/1000-point groupings depending on style/time horizon.

This establishes round-number context but does not establish the current project value `roundStep=50` as canonical.

Before changing any parameter, the project's XAUUSD price-unit/point convention must be mapped explicitly to the source terminology.

## Status

`SOURCE-ESTABLISHED CONTEXT / UNIT MAPPING REQUIRED`

---

# 19. Context: moving average

The source describes a moving average as an equilibrium-price context and demonstrates waiting for price to return toward it.

This does not establish EMA 60 as a canonical Strategy A period.

## Status

`SOURCE-ESTABLISHED CONTEXT / PERIOD TBD`

---

# 20. Context: sessions

Time of day is explicitly part of the strategy. London/European and New York timing are discussed separately.

The current project UTC session windows remain implementation parameters until chart timezone and exact source windows are reconciled.

## Status

`SOURCE-ESTABLISHED CONCEPT / EXACT WINDOWS TBD`

---

# 21. Context: clean vs dirty market

The source distinguishes clean directional structure from messy/choppy/ranging conditions and treats cleanliness as relevant to setup quality.

No deterministic numeric cleanliness score is provided.

The current `QualityScore` therefore remains research machinery, not teacher-canonical logic.

## Status

`SOURCE-ESTABLISHED CONCEPT / NUMERIC MODEL TBD`

---

# 22. Research candidate matrix

The following are legitimate research candidates but are **not canonical rules**:

| Candidate | Source basis | Safe status |
|---|---|---|
| immediate next-bar FT | strongly demonstrated | RESEARCH-CANDIDATE |
| first structural low/high as correction reference | explicit example | RESEARCH-CANDIDATE |
| pending limit at first structural level | explicit behavior | RESEARCH-CANDIDATE |
| intrabar touch fill | execution interpretation | SIMULATOR POLICY |
| intrabar structural SL | execution interpretation | SIMULATOR POLICY |
| P-GAP as spike evidence | explicit role | RESEARCH-CANDIDATE |
| Leg2 magnitude equal to Leg1 | explicit relationship | SOURCE-ESTABLISHED RELATIONSHIP |
| 2X at 50% target progress | explicit example | RESEARCH-CANDIDATE |
| TP1 as base exit | explicit preference | RESEARCH-CANDIDATE |
| EMA context | explicit broader context | RESEARCH-CANDIDATE |
| round-level context | explicit broader context | RESEARCH-CANDIDATE |
| clean-market filter | explicit concept | RESEARCH-CANDIDATE |

No candidate is promoted merely because it improves historical results.

---

# 23. Implementation gate

**No production Strategy A code change is approved by this document.**

Implementation may begin only after:

1. P-GAP geometry is either extracted from an actual gap lesson or explicitly marked optional/unknown.
2. Spike grammar is represented without arbitrary hidden thresholds.
3. Leg1 endpoints are source-grounded or a clearly labelled research hypothesis.
4. Leg2 projection reference is explicit.
5. Stop semantics and intrabar execution policy are frozen.
6. Pending-order replacement logic is explicitly defined or excluded from baseline.
7. 2X is modelled separately from the base single-position population.
8. A deterministic fixture/test set is written for every adopted state transition.
9. Backtests compare the new candidate against the canonical Strategy A baseline without rewriting historical reports.
10. DEV/VAL/fresh-holdout boundaries remain chronological and untouched by exploratory fitting.

---

# 24. Immediate next research task

The next task is not optimization.

It is **geometry resolution**:

```text
1. Leg1 endpoint extraction
2. Leg2 projection origin
3. structural SL level
4. intrabar/same-candle execution policy
5. exact P-GAP geometry if source material becomes available
```

If the missing source lesson cannot be recovered, each unresolved item must remain explicitly `TBD` or become a separately labelled research candidate.

This preserves the distinction between:

**what Poorsamadi said**
vs.
**what the machine assumes**
vs.
**what the data later validates**.
