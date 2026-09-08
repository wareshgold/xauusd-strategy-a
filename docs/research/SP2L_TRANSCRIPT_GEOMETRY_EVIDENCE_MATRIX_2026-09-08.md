# SP2L Transcript Geometry Evidence Matrix

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Purpose:** Consolidate the recovered timestamped transcript evidence into a source-first geometry decision record without freezing unresolved formulas.

## 1. Direct transcript findings

| Time | Source wording / meaning | Deterministic implication | Status |
|---|---|---|---|
| 30:48–31:18 | Channel-like overlap is not Spike-axis trading; Spike occurs where a valid breakout happens; breakout requires a close beyond a prior level and a follow-through/key bar that cannot return into the prior range | Breakout + follow-through belong in Spike grammar; channel overlap must not be silently classified as Spike | RESOLVED SEMANTICALLY |
| 33:51–34:14 | Breakout from a level followed by key-bar close is described as a powerful trend; P-Gap is a visual marker for where breakout occurred | P-Gap is source-linked to breakout location, not merely any visual gap | RESOLVED SEMANTICALLY |
| 34:25–34:35 | In one construction, the referenced high and low do not overlap and a gap occurs with breakout + follow-through; another construction gets the gap on the next candle | Source confirms a non-overlap/gap relationship and more than one temporal construction | FORMULA STILL OPEN |
| 34:44–35:37 | Breakout-first and higher-low-first constructions are treated as conceptually the same; multiple states are considered Spike | Do not force one candle-count grammar yet | VARIANT TAXONOMY OPEN |
| 35:50–36:15 | Three-candle example is discussed; a sequence/hierarchy of movements is treated as Spike; strategy name is SPIKE-2LEG | Multiple visual Spike constructions are canonical at concept level | SEMANTICALLY RESOLVED |
| 36:15–36:46 | 2Leg is explicitly equated with AB=CD; source contrasts classical A/B/C/fibonacci treatment with candle-level work | AB=CD is canonical concept; classical fib implementation must not be assumed | RESOLVED SEMANTICALLY |
| 36:59 | After Spike, correction is expected and the second leg should complete with Leg 1 equal to Leg 2 | Leg2 projection is tied to Leg1 magnitude | RESOLVED SEMANTICALLY; ANCHORS OPEN |
| 38:38 | Correction is described as moving below the first low in the bullish example; order can be manual or pre-set Limit | Pending-limit entry during correction is canonical; the phrase identifies a structural low in the example but does not prove C mapping | STRONG |
| 38:53–39:11 | Gap + breakout + follow-through creates order space/trend; no need to wait for another candle; limit order can be placed within the first three candles | Entry is anticipatory/pending, not a later close-reclaim | STRONG / CANONICAL SEMANTIC |
| 39:26 | Buy Limit is placed; SL distance is known before activation; if price returns to the invalidation area, scenario is invalid | Stop/invalidation is structural and pre-defined before fill | STRONG |
| 39:48–40:07 | Pending order may be deleted/replaced if later candle materially changes risk distance; otherwise it can be retained | Order-management semantics are dynamic, but exact threshold is not source-defined | SEMANTICALLY RESOLVED; NUMERIC THRESHOLD OPEN |
| 42:26–42:48 | TP1/TP2 are discussed; author says he generally uses TP1; TP2 is considered large for this strategy and says TP should be 1 in that context | Base target concept includes 1:1, but relation to AB=CD projection and 2X requires separate resolution | TARGET MODULE OPEN |

## 2. Geometry decisions

### P-Gap

**Source-confirmed:** P-Gap is associated with valid breakout and is visually used to identify the breakout location. The transcript describes a gap/non-overlap between a referenced high and low and also shows that the gap can appear in more than one candle construction.

**Not source-confirmed:**

- exact candle indices;
- exact high/low/open/close boundaries;
- whether the relevant boundaries are wick extrema or bodies;
- whether P-Gap is always exactly the same three-candle relation;
- numeric tolerance.

**Decision:** keep P-Gap as an explicit unresolved source input. Do not implement the generic three-candle imbalance as canonical.

### A / B / C / D

The source explicitly connects 2Leg with AB=CD and real-chart material visibly contains A/B/C/D-style labels. However, the recovered transcript does not, in the inspected geometry teaching region, provide an unambiguous OHLC definition for those labels.

Candidate anchors remain hypotheses only:

- A = structural origin / swing origin;
- A/B = breakout reference to spike extreme;
- A/B = spike start/end;
- A/B = candle open to spike extreme;
- C = correction extreme;
- C = structural HL/LH;
- C = explicit Buy Limit line;
- D = projected equal-leg endpoint.

**Decision:** no candidate is promoted. In particular, `entry = C` is prohibited until directly source-confirmed.

### AB = CD tolerance

The source states equality conceptually. No numeric tolerance is stated in the inspected transcript.

**Decision:** equality is a source concept; executable tolerance remains unresolved. Do not invent ±5%, ±10%, ±20%, ATR-based, tick-based, or optimization-derived tolerance.

### Pending-limit fill

The transcript explicitly says Buy Limit can be placed before a later candle and that the order is active during correction.

**Decision:** production semantics must use a pending-limit representation once geometry is frozen. A market close-reclaim trigger is not an allowed substitute.

## 3. New source-resolution conclusion

The recovered transcript closes the previous **missing-subtitle/transcript** blocker and materially strengthens the semantic chain:

**context/range → breakout + follow-through / P-Gap → Spike → correction → pending Limit → structural invalidation → second leg ≈ first leg / AB=CD**

It does **not** close executable geometry. The remaining blockers are now narrower and more explicit:

1. P-Gap boundaries/formula;
2. exact A/B/C/D anchors;
3. exact relation between C and pending-limit price;
4. AB=CD tolerance;
5. spike-variant deterministic taxonomy;
6. intrabar fill ordering;
7. target/TP1/TP2/2X relationship;
8. exact invalid/red-X rejection predicate.

## 4. Production protection

No canonical strategy geometry is frozen by this document. No production signal logic is changed. The legacy generic P-Gap detector and close-reclaim entry remain research-only/non-canonical.

## 5. Primary source artifact

`docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`

Transcript SHA: `47f867385338738a23b2d06dc48e67b852127243`

Registry: `docs/source/treasure_path/SP2L_SOURCE_TRANSCRIPT_REGISTRY_2026-09-08.md`
