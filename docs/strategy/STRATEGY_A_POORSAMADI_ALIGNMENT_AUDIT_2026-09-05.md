# Strategy A — Poorsamadi Alignment Audit

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Status:** Initial source-vs-code audit — no production rule changes yet

## 1. Purpose

This audit compares the current deterministic Strategy A implementation with the supplied Poorsamadi SP2L source.

The raw source remains the semantic authority. Existing code is evidence of current machine behavior, not proof of intended meaning.

Status vocabulary:

- **MATCH** — current behavior is consistent with the source statement.
- **PARTIAL** — directionally compatible, but important details are missing or implementation-specific.
- **CONFLICT** — current behavior contradicts an explicit source statement.
- **UNKNOWN** — the source does not provide enough information to determine the canonical rule safely.

No rule is changed merely because it looks different. A code change requires an explicit source-grounded reason and a deterministic specification.

---

## 2. Initial findings

### A. Breakout detection — PARTIAL / implementation-specific

**Current code:** `src/domain/market/BreakoutDetector.ts`

The detector uses a fixed `lookback=5`, computes the highest high / lowest low of those five prior candles, and calls a breakout when the current candle closes beyond that level.

Source alignment:

- The source explicitly describes breakout as a close beyond a relevant level.
- However, the source material reviewed here does **not** establish that the canonical level is always the highest/lowest of exactly five prior candles.
- Therefore the close-beyond-level concept is aligned, but the `5`-candle lookback is not source-established.

**Status:** PARTIAL

**Action:** Do not change the `5` yet. Mark it as an implementation parameter requiring canonical extraction or an explicit project assumption.

---

### B. Follow-through — PARTIAL / likely conflict in exact timing semantics

**Current code:** `src/domain/market/FollowThroughDetector.ts`

The implementation searches up to two candles after breakout and accepts the first candle whose close is further in the breakout direction than the breakout close, while also remaining beyond the broken level.

The source describes a breakout followed by a next candle / follow-through (FT or key bar) that must not return into / overlap the prior area.

Important differences:

1. Current code allows a follow-through on either of the next **two** candles.
2. Source wording emphasizes the **next candle** in the demonstrated breakout sequence.
3. Current code tests close progression and close beyond the broken level; the source additionally discusses return/overlap behavior.

**Status:** PARTIAL, with an unresolved semantic conflict around exact FT timing and overlap definition.

**Action:** Do not silently change it. Extract the complete FT rule before recoding.

---

### C. Spike detection — CONFLICT / major semantic gap

**Current code:** `src/domain/strategy-a/SpikeDetector.ts`

Current implementation:

- derives the spike window around an already-detected breakout + FT;
- uses a maximum of 8 candles;
- requires directional candle-body fraction >= 0.50;
- rejects average candle-range overlap > 0.80;
- sets spike start to the first candle of that 8-candle window;
- sets spike end to FT;
- does not actually detect a preceding range;
- always sets `hasPGAPEvidence=false`.

The source explicitly states that a spike is a sharp movement **after a range**, that structure/sequence matters, that overlap affects movement classification, and that breakout/FT/P-GAP sequencing and higher-low/lower-high structures are relevant.

The current detector therefore does not yet encode the source's semantic spike definition. In particular, it can produce a `SpikeCandidate` without proving the required preceding range/context and without distinguishing the source-described strong-movement variants.

**Status:** CONFLICT / major semantic gap

**Action:** This is a primary refactor target, but only after the exact source-to-rule mapping is completed. Do not tune the existing `0.50`, `0.80`, or `8` thresholds as if they were teacher rules.

---

### D. Correction detection — PARTIAL

**Current code:** `src/domain/strategy-a/CorrectionDetector.ts`

For bullish setups, correction starts after the spike and is recognized when a candle's low falls below `spike.startPrice`; bearish is symmetric using high above `spike.startPrice`.

The source describes a correction after the directional movement and specifically demonstrates a correction that breaches the first relevant low/high before an order can be placed.

The semantic direction is compatible, but the correctness depends on whether `spike.startPrice` truly represents the source's first relevant low/high. Because current spike construction is not yet source-equivalent, this boundary is not yet proven canonical.

**Status:** PARTIAL

**Action:** Re-evaluate after spike/Leg 1 canonicalization. Do not independently optimize correction depth.

---

### E. Entry trigger — CONFLICT / major semantic difference

**Current code:** `src/domain/strategy-a/EntryTrigger.ts`

Current behavior waits for a **completed post-correction candle** whose close reclaims the correction extreme. Entry price is that candle's close.

The source explicitly demonstrates that when the correction begins, an order can be placed **in advance**, including a limit order at a structural level. The source also discusses knowing the SL distance before activation and managing the pending order based on that risk distance.

Therefore the current `CORRECTION_EXTREME_RECLAIM` close-entry model is not equivalent to the demonstrated source entry model.

This is the clearest current semantic conflict.

**Status:** CONFLICT

**Action:** Replace only after the canonical entry rule is extracted completely. The likely architecture needs to distinguish:

- setup becomes eligible;
- pending order placement;
- order activation/fill;
- trigger/confirmation variants;
- cancellation/invalidation before fill.

The existing single `EntryTrigger` abstraction may be too narrow for the source semantics.

---

### F. Leg 2 projection — PARTIAL / major endpoint uncertainty

**Current code:** `src/domain/strategy-a/LegProjection.ts`

Current Leg 1 size is:

`abs(spike.firstCandle.open - spike.lastCandle.close)`

and TP1 is projected from the correction extreme by that size.

The source explicitly establishes the conceptual relationship that after the spike and correction, Leg 2 is expected to equal Leg 1 (AB=CD at candle level).

However, the source does not justify the current exact Leg 1 endpoints (`first.open` → `last.close`) as the canonical measurement in the reviewed material.

Because the Leg 1 boundary is fundamental to the projection, the current formula is an implementation assumption unless further source evidence establishes those endpoints.

**Status:** PARTIAL / UNKNOWN on exact formula

**Action:** Do not optimize projection ratio. First define source-canonical Leg 1 start/end and then derive Leg 2 deterministically.

---

### G. Invalidation / stop — PARTIAL, with execution-semantics issue

**Current code:** `src/domain/strategy-a/Invalidation.ts`

The invalidation level is the correction extreme. The helper `isInvalidated()` returns true only when the **candle close** crosses the level.

The source establishes structural invalidation and explicitly warns against moving the SL farther away. The demonstrated setup treats reaching the invalidating level as cancellation/invalidation.

A close-only invalidation test is therefore not proven equivalent to a price-level stop. For a backtest, intrabar high/low interaction with the stop level and same-candle ambiguity need explicit treatment.

**Status:** PARTIAL

**Action:** Separate the semantic stop level from the execution/outcome model. Do not assume close-only invalidation is canonical.

---

### H. EMA / round-number / session quality gate — UNKNOWN as Poorsamadi rules

**Current code:** `src/domain/strategy-a/Context.ts` and `QualityScore.ts`

The research baseline uses:

- EMA period 60;
- round-number step 50;
- round-number distance 5;
- London 07:00–16:00 UTC;
- New York 13:00–22:00 UTC;
- a quality score combining structure, overlap, P-GAP evidence, location, EMA and session.

The source clearly says timeframe and time-of-day are part of a complete strategy, and it discusses adding SP2L as a trigger at meaningful locations. It does **not**, in the reviewed source, establish these exact numeric EMA/round/session parameters or the current A/B/C scoring formula.

**Status:** UNKNOWN / implementation-specific

**Action:** Keep these parameters isolated from source claims. They must not be described as "Poorsamadi rules" until separately established.

---

## 3. Highest-priority conflicts

| Priority | Area | Status | Why it matters |
|---|---|---|---|
| P0 | Entry model | CONFLICT | Current close-reclaim entry differs from demonstrated pre-placed limit-order behavior. |
| P0 | Spike definition | CONFLICT / gap | Current detector does not encode preceding range + source movement variants. |
| P1 | Follow-through | PARTIAL | Exact next-candle / no-return-overlap semantics are not fully represented. |
| P1 | Leg 1 measurement | PARTIAL | Current endpoints are not source-established. This directly changes TP1. |
| P1 | Stop execution | PARTIAL | Close-only invalidation may differ from level-touch stop behavior. |
| P2 | Breakout lookback | UNKNOWN | `5` is not established by the source reviewed. |
| P2 | EMA/round/session score | UNKNOWN | Exact parameters and scoring are not source-established. |

---

## 4. What we should NOT do yet

1. Do not alter the historical datasets.
2. Do not delete or rewrite previous research reports.
3. Do not optimize current thresholds to make the implementation look better.
4. Do not rerun the old research and call it validation of the corrected strategy.
5. Do not promote T1 findings into the canonical strategy.
6. Do not label current EMA/round/session parameters as teacher rules.
7. Do not invent missing numeric definitions.

---

## 5. Next implementation sequence

### Phase 1 — semantic extraction

Complete the source mapping for:

1. Spike variants;
2. exact breakout + FT relationship;
3. correction boundary;
4. entry/pending-limit mechanics;
5. invalidation/SL;
6. Leg 1 endpoints;
7. Leg 2 projection;
8. TP1/TP2;
9. 2X / second position;
10. session/timeframe constraints.

### Phase 2 — deterministic model

Introduce explicit state objects rather than forcing everything through a single entry-trigger abstraction:

`RANGE → BREAKOUT → FT → SPIKE → CORRECTION → PENDING ORDER → FILL → LEG2 → EXIT/INVALIDATION`

Only states supported by the source should become mandatory.

### Phase 3 — tests

For every source-grounded rule, add deterministic unit tests including boundary and invalid cases.

### Phase 4 — canonical reconstruction

Rebuild the Strategy A backtest from the corrected deterministic model.

### Phase 5 — re-validation

Only after the corrected implementation is stable:

`DEV → VAL → Fresh Holdout`

All previous research results remain historical evidence about the old implementation and must not be mixed with the corrected strategy's results.

---

## 6. Current conclusion

The existing Strategy A is a useful deterministic **research prototype**, but it is not yet demonstrably equivalent to the source semantics.

The biggest issue is not a missing parameter tweak. It is that the current architecture models the setup as a post-correction close-reclaim entry, while the source demonstrates a pending limit-order workflow and a richer sequence of spike/range/breakout/correction states.

Therefore the correct next move is **semantic reconstruction first, code rewrite second, backtest third**.

No production strategy rule has been changed by this audit.
