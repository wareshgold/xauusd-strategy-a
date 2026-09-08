# SP2L Source Resolution — Multi-Step Checkpoint

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Overall state:** `PROGRESSING — CANONICAL FREEZE STILL BLOCKED`

## Steps completed in this checkpoint

### Step 1 — P-Gap evidence narrowed

Primary transcript evidence now establishes three distinct facts together:

1. P-Gap is a distinct gap type, not every visible gap.
2. P-Gap is used as a marker for the breakout location.
3. The source describes a non-overlap between a referenced high and low when explaining one P-Gap construction.

The source also says another accepted construction creates the gap one candle later, so a single fixed candle index is not yet justified.

The strongest candidate is therefore an adjacent-candle range non-overlap associated with the breakout/early-trend construction, but exact wick/body and timing rules remain open.

### Step 2 — P-Gap vs E-Gap context narrowed

At 50:09–50:56 the instructor contrasts an early clean trend opportunity (P-Gap) with a later extended condition that is described as likely E-Gap and more risky. This confirms that *location/context* is part of the P-Gap/E-Gap distinction.

No numeric definition of “early” is source-confirmed.

### Step 3 — Entry semantics cross-checked

At 38:38–39:26 the source states that when correction begins below the first bullish low, the order can be placed manually or as a pre-set Limit, and that the Limit may be placed during the first three candles. This confirms pending-limit semantics and rejects a later close-reclaim substitute.

Exact Limit price remains unresolved.

### Step 4 — Base target isolated from 2X

At 42:26–42:37 the instructor says he generally uses TP1 and that TP2 is relatively large for this strategy because the stop is relatively large, followed by the statement that TP should be 1 in that context. The official SP2L page states default TP = 1:1.

The optional 2X/secondary position is therefore treated as a separate management module rather than part of the base signal geometry.

### Step 5 — A/B/C/D interpretation corrected

The later real-chart material does not provide sufficiently legible evidence to freeze classical A/B/C/D OHLC anchors. The primary transcript explicitly says the classical internet AB=CD presentation is not the source's candle-level execution method.

Therefore classical harmonic A/B/C/D anchors are not imposed on Strategy A.

### Step 6 — Research guardrails expanded

The research fixture suite now includes 13 unresolved discriminators covering:

- immediate boundary separation;
- higher-lows-then-gap;
- third construction;
- channel overlap;
- touch/equality;
- wick-only separation;
- body-only separation;
- delayed gap;
- early-breakout P-Gap context;
- late-extension E-Gap candidate;
- generic gap without breakout context;
- pending Limit before fill;
- 2X as a separate management module.

No fixture promotes itself to canonical geometry.

## Current source-aligned chain

`context/range → breakout + follow-through → P-Gap/Spike → correction → pending Limit → structural invalidation → Leg 2 ≈ Leg 1 → base TP1 ≈ 1R`

Optional:

`2X / secondary position → separate management module`

## Remaining blockers before FROZEN GEOMETRY

1. P-Gap exact boundaries: wick vs body.
2. P-Gap exact candle timing across the accepted variants.
3. Exact pending-Limit price anchor.
4. Exact structural SL candle-level anchor.
5. Exact Leg 1 endpoints.
6. Intrabar fill ordering.
7. AB=CD equality implementation/tolerance.
8. Exact 2X trigger/price formula if the module is later included.
9. Deterministic rejection predicate for the red-X example.

## Gate status

| Gate | Status |
|---|---|
| SOURCE RESOLUTION | 🟠 progressing |
| SYNTHETIC FIXTURES | 🟢 expanded |
| FROZEN GEOMETRY | 🔴 blocked |
| DEV | 🔒 not authorized |
| UNTOUCHED VAL | 🔒 untouched |
| ROBUSTNESS / STABILITY | 🔒 not authorized |
| FRESH HOLDOUT | 🔒 locked |
| PRODUCTION | 🟢 unchanged |

## Primary-source references

- Transcript: `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`, SHA `47f867385338738a23b2d06dc48e67b852127243`
- Uploaded source video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`, SHA-256 `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- Official SP2L page: `https://poursamadi.com/sp2l-strategy/`
