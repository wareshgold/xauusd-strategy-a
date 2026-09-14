# SP2L Official-Web Source Corroboration — 2026-09-14

## Purpose

This document records newly recovered source evidence from the creator's published SP2L page. It is a source-evidence artifact, not a geometry-freeze gate. No statement below is promoted to production merely because it appears on a web page; the evidence must still be reconciled with the raw source video and exact frame evidence.

## Source

Official creator page:

- `https://poursamadi.com/sp2l-strategy/`
- Page title: `استراتژی SP2L (Spike–2Leg) محمدعلی پورصمدی`

The page explicitly describes SP2L as a price-action method based on a sharp spike followed by a correction and second leg. It also identifies three main components: Spike, Second Leg, and Entry Level.

## Newly recovered source statements

### 1. Spike / P-Gap

The official page states that a valid SP2L spike is a strong, sudden move, usually consisting of several large candles in one direction, and explicitly states that an important feature of a valid spike is the presence of a price gap identified as `P-Gap`.

It further states that a sharp movement without a gap is not considered valid in the strategy.

**Evidence impact:**
- strengthens the source interpretation that P-Gap is a required validity condition for the spike;
- does NOT define the executable P-Gap OHLC boundaries or formula;
- does NOT justify replacing P-Gap with a generic three-candle imbalance predicate.

### 2. Second-leg trigger

For an upward setup, the official page states that after the spike/correction, the corrective candle is expected to reach the low of the previous candle. For a downward setup, it states that the corrective candle is expected to reach the high of the previous candle.

**Evidence impact:**
- this is materially stronger source evidence for the event/trigger semantics of the second leg;
- it provides a concrete source statement that should be reconciled against the 37:20–38:40 video drawings;
- it still does not uniquely resolve A/B/C geometric anchors or fill-price semantics.

### 3. Entry and stop

The page states that entry is in the direction of the spike. It states that the stop-loss is placed behind the candle from which the spike originated.

**Evidence impact:**
- strengthens the existing source evidence for a structural stop tied to the spike-origin candle;
- provides a source-defined semantic reference for the stop that should be compared against G404 hypotheses;
- does NOT by itself define the exact executable price field, wick/body boundary, buffer, or pre-fill invalidation behavior.

### 4. Target

The official page states a default take-profit of 1:1 risk-to-reward.

**Evidence impact:**
- introduces an explicit published target convention that should be treated as source evidence;
- does NOT erase the separate video evidence showing TP1/TP2 and therefore does not by itself resolve the canonical multi-target mapping;
- no target formula is promoted from this statement alone.

### 5. Secondary 50% entry

The page additionally describes a secondary entry at 50% of the distance from entry to stop-loss.

**Evidence impact:**
- this is evidence of an additional/secondary entry mechanism;
- it must remain separate from the primary SP2L pending-limit geometry until reconciled with the video;
- it is not promoted into the canonical Strategy A entry rule at this stage.

## Evidence reconciliation with the raw-video register

The newly recovered web evidence is consistent with the already registered raw-video findings:

- SP2L = Spike → 2 Leg.
- P-Gap is associated with valid spike/breakout construction.
- correction precedes second-leg continuation.
- the setup has a source-defined entry level.
- structural stop is associated with the spike-origin candle.

The web page adds useful semantic detail, but it does not replace the raw video. In particular, the exact P-Gap formula, exact A/B/C anchors, AB=CD tolerance, exact pending-limit price/fill semantics, executable stop price, and TP1/TP2 mapping remain unresolved.

## Provenance rule

This page is treated as **secondary source material published by the strategy creator**, below the raw source video but above generic price-action conventions. Any conflict with the raw source video must be investigated explicitly; backtest performance must not decide the conflict.

## Current blockers after this recovery

- `UNRES-PGAP-GEOMETRY`: OPEN — semantic requirement strengthened, executable formula unresolved.
- `UNRES-ABCD-ANCHORS`: OPEN — no exact A/B/C anchor resolution.
- `UNRES-ABCD-TOLERANCE`: OPEN — no tolerance supplied.
- `UNRES-ENTRY-PRICE`: OPEN — source confirms entry level semantics, exact executable mapping unresolved.
- `UNRES-ENTRY-TIMING`: PARTIALLY INFORMED — second-leg trigger wording recovered, pending-limit persistence/fill/invalidation semantics still require video reconciliation.
- `UNRES-STOP-BOUNDARY`: PARTIALLY INFORMED — spike-origin candle reference recovered, exact price boundary/buffer remains unresolved.
- `UNRES-TARGET-MAPPING`: PARTIALLY INFORMED — default 1:1 TP recovered, but TP1/TP2 video mapping remains unresolved.

## Gate decision

This artifact does **not** clear G400. Canonical executable geometry remains frozen/blocked until the raw-video evidence and this published source wording are reconciled at the exact-frame level.

## Next research action

Reinspect the registered raw-video windows around:

- 36:00–36:20 for the P-Gap construction;
- 37:20–38:40 for the corrective-candle / second-leg trigger;
- 38:40–40:20 for the entry level and spike-origin stop;
- 40:20–44:30 for TP1/TP2 versus the published 1:1 target statement.

Use exact timestamp + zero-based frame indexing and record whether the video visually supports, narrows, or contradicts the published statements.
