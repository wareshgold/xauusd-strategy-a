# Strategy A — Poorsamadi P0 Rules v1

**Date:** 2026-09-05
**Branch:** `research/strategy-a-poorsamadi-alignment`
**Status:** research/codification only — no production implementation change

## Purpose

Resolve the highest-priority semantic unknowns before touching the Strategy A implementation:

1. P-GAP role
2. first relevant low/high
3. limit-entry timing
4. stop/invalidation geometry
5. Leg 1 / Leg 2 geometry
6. 2X separation

The raw transcript remains authoritative. A statement is marked **source-established** only where the transcript explicitly supports it. Missing numeric tolerances remain TBD.

---

## 1. P-GAP — SOURCE-ESTABLISHED ROLE, EXACT GEOMETRY TBD

The source explicitly uses P-GAP as a visual marker of a strong breakout/spike and distinguishes it from E-GAP and Common-GAP. It describes two equivalent sequence variants:

- breakout → FT → later P-GAP
- higher lows → P-GAP

The source says these variants are conceptually the same and are treated as one strategy for now.

### Codification decision

`P-GAP` should be represented as **evidence inside the SPIKE family**, not as an independent mandatory gate for every spike.

### Still TBD

- exact P-GAP candle geometry;
- whether wick overlap is allowed;
- whether P-GAP means a gap between full ranges, bodies, or specific high/low boundaries;
- whether a P-GAP is mandatory or merely strengthening evidence in each branch.

The transcript explicitly says the concept is explained in a separate gap lesson, so this SP2L transcript alone is insufficient to invent the numeric/price-boundary formula.

### Evidence

At 34:14–35:37, P-GAP is described as a useful sign for identifying the breakout/strong movement and appears in both sequence variants. fileciteturn101file0L2-L2

---

## 2. FIRST RELEVANT LOW/HIGH — STRONGLY SOURCE-ESTABLISHED

For a bullish SP2L example, the source says that when the next candle begins correction, correction means price moves **below the first low**. This is the level where the order can be prepared.

For bearish symmetry, the corresponding structural level is the first relevant high.

### Codification decision

For bullish:

`correctionReference = first structural low of the recognized spike`

For bearish:

`correctionReference = first structural high of the recognized spike`

The phrase "first low" is source-established; the exact algorithm for identifying that candle's structural significance remains part of spike grammar.

### Important consequence

The current prototype's `spike.startPrice` is valid only if SpikeDetector defines that field as this first structural low/high. It must not merely mean the first candle's OHLC endpoint by implementation convenience.

Evidence: 38:18–38:53. fileciteturn99file0L2-L2

---

## 3. LIMIT ENTRY — SOURCE-ESTABLISHED EVENT MODEL

The source explicitly says the trader does **not** need to wait for the next candle to complete. Once the spike/strong-movement context and beginning of correction are known, the limit order can already be placed.

For the bullish example:

`BUY LIMIT = first structural low / correction reference`

The pending order exists before fill. Price later activates it.

### Codification decision

The event sequence must be:

`SPIKE recognized → CORRECTION begins → PENDING_LIMIT_CREATED → price reaches level → FILL`

It must **not** be:

`CORRECTION → wait for close reclaim → market entry`

### Order replacement

The source also says that if a later candle changes the setup and the distance to SL becomes too large, the old order can be deleted and a new order placed with adjusted size. The exact maximum-risk-distance rule is TBD.

Evidence: 38:38–40:16. fileciteturn99file0L2-L2

---

## 4. STOP / INVALIDATION — STRUCTURAL AND FIXED

The source gives the semantic reason for the stop: if price returns to the invalidating structural level, the scenario is no longer valid. It also explicitly states that the entry-to-stop distance is known before activation.

The source later emphasizes that stop should not simply be moved farther away when the market goes against the trade.

### Codification decision

The base model should use:

`SL = structural invalidation level`

and preserve that risk geometry after fill unless a separately source-defined management rule is adopted.

### Execution semantics

The semantic level is established, but the exact simulator mechanics remain TBD:

- touch vs close;
- spread/slippage treatment;
- same-candle entry + SL ordering.

For research, these must be explicit simulator policies and must never be silently mixed with the semantic rule.

Evidence for known pre-fill risk distance and invalidation: 39:26–40:16. fileciteturn99file0L2-L2

---

## 5. LEG 1 — CONCEPT ESTABLISHED, ENDPOINTS STILL TBD

The source establishes that the first directional movement is Leg 1 and that after correction the expected next movement is Leg 2.

It does **not** provide enough textual information in this transcript to prove that Leg 1 equals:

`first.open → last.close`

or any other exact OHLC endpoint formula.

### Codification decision

Keep:

`Leg1 = canonical first directional movement magnitude`

but leave endpoint selection as `TBD` until the source geometry is extracted more precisely.

No optimization of endpoint formula is allowed against validation data at this stage.

---

## 6. LEG 2 — RELATIONSHIP ESTABLISHED

The central SP2L expectation is explicitly stated:

`Leg2 ≈ Leg1`

The teacher describes this as AB=CD brought down to candle-level price action.

### Codification decision

The baseline target should be conceptually:

Bullish:
`TP1 = Leg2 reference + Leg1 magnitude`

Bearish:
`TP1 = Leg2 reference - Leg1 magnitude`

But the exact projection reference is still TBD because the transcript uses several chart annotations and the precise A/B/C/D endpoint convention is not numerically specified.

Evidence: 36:15–37:08. fileciteturn101file0L2-L2

---

## 7. 2X — SEPARATE POSITION EVENT

The source explicitly distinguishes the second position from the first. It says the second trade is entered after the first has moved toward target and illustrates that the second position can have a larger reward relative to its own risk.

The exact 2X trigger belongs to the dedicated second-position teaching and should not be inferred from the abbreviated SP2L example alone.

### Codification decision

Model 2X separately:

`POSITION_1`

and, if enabled:

`POSITION_2 / 2X`

Do not contaminate the single-position baseline with 2X economics.

The source also explicitly says TP1 is generally preferred for this strategy in the demonstrated context.

Evidence: 41:26–42:37. fileciteturn99file0L2-L2

---

# 8. P0 implementation contract — NOT YET APPROVED FOR CODE

Before implementation, the following semantic contract is now sufficiently constrained:

```text
RANGE
  ↓
BREAKOUT (close beyond relevant level)
  ↓
FOLLOW-THROUGH (immediate next-bar behavior)
  ↓
SPIKE FAMILY
  ├─ breakout/FT → structure → P-GAP
  ├─ structure → P-GAP
  └─ other source-described strong-move variant
  ↓
CORRECTION begins through first relevant low/high
  ↓
PENDING LIMIT created immediately
  ↓
FILL when price reaches limit
  ↓
FIXED STRUCTURAL SL
  ↓
LEG 2 expected ≈ LEG 1
  ↓
TP1 baseline
```

### Still blocking implementation

1. Exact P-GAP geometry
2. Exact spike start/end grammar
3. Exact Leg1 endpoints
4. Exact Leg2 projection reference/tolerance
5. Exact SL level semantics
6. Exact pending-order replacement threshold
7. Exact intrabar execution policy

These are **not** to be solved by fitting the existing backtest.

---

# 9. Research boundary

This document deliberately does not modify Strategy A production code and does not reinterpret the existing validated research results.

The next research task is **Source Excavation v3**, focused on the separate gap/2nd-position material and the exact chart-level definitions needed to close the remaining P0 geometry gaps.
