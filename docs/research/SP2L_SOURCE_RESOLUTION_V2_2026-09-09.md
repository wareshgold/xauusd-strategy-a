# SP2L Source Resolution V2 — 2026-09-09

## Purpose

This is a source-resolution research record. It advances the Strategy A / SP2L geometry investigation using the authoritative timestamped transcript artifact and the uploaded source video. It does **not** authorize production implementation where geometry remains unresolved.

## Authoritative transcript recovery

The previous transcript-recovery blocker is closed at the artifact level.

- YouTube source: `7HEC5mO3d3U`
- Transcript registry: `docs/source/treasure_path/SP2L_SOURCE_TRANSCRIPT_REGISTRY_2026-09-08.md`
- Canonical transcript path recorded by the registry: `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
- Transcript content blob SHA: `47f867385338738a23b2d06dc48e67b852127243`
- The canonical path is not currently present on the examined branch, but the Git object exists and was recovered directly by SHA. The transcript therefore remains authoritative source evidence, while repository path synchronization is a separate housekeeping item.

## New source-confirmed findings

### 1. Spike is a sequence, not a single candle threshold

At 26:14–27:51 the source frames spike as a sharp/strong movement after a range. At 33:37–36:05 the teacher explains multiple candle constructions and explicitly treats several variants as the same Spike concept.

At 34:55 the source says one variant first forms higher lows and then creates the gap. At 35:37–36:05 the source groups the variants together and says the three shown states are being treated as Spike.

**Decision:** do not define Spike as a fixed candle-size threshold. The canonical semantic is a directional, structurally strong movement after context/range, with multiple source-recognized constructions.

### 2. P-Gap is a breakout sign and is not generic FVG

At 31:43 the source states that the breakout candle has P-GAP / pressure gap and explicitly distinguishes it from E-GAP. At 32:03–32:21 the source says P-GAP, E-GAP and Common-GAP are different concepts and that formation location matters. At 34:14–34:35 the source uses the non-overlap between the prior high and current low as the visual sign in the illustrated breakout example.

**Decision:** P-Gap semantic relationship is resolved strongly. However, the source still does not uniquely specify a universal OHLC formula, equality/touch rule, candle indexing rule, or minimum gap size across all variants.

**Production status:** executable P-Gap formula remains BLOCKED.

### 3. AB=CD / equal-leg relationship is explicit

At 36:15 the source explicitly identifies 2Leg with AB=CD. At 36:31–36:46 it contrasts classical internet A/B/C/Fibonacci treatment with the source's candle-level treatment. At 37:57 it says the next leg is expected to be the same size as the first leg.

**Decision:** the equality relationship is source-confirmed. Classical Fibonacci conventions are explicitly not to be imported automatically.

**Production status:** A/B/C/D OHLC anchors and numerical tolerance remain unresolved.

### 4. Entry semantics are materially more resolved than previously recorded

At 38:18 the source defines the Spike example as successive higher lows. At 38:38 it explicitly defines the correction as price moving below the **first low**, and says the order can be placed manually or as a pre-set limit there. At 39:11 it says the limit order can be placed within the initial three-candle construction without waiting for another candle. At 45:55–46:15 it again describes three-candle situations where the next candle returns to the relevant low and the first pullback becomes the entry opportunity.

The source visual sequence at approximately 38:50–39:50 also explicitly labels `Limit` / `Buy Limit` and shows a horizontal order level.

**Decision:** for the demonstrated bullish Spike variant, the source confirms a pending Buy Limit associated with the first-low / first-pullback structure. Bearish logic is the mirrored Sell Limit concept.

**Important limitation:** the transcript wording does not yet uniquely establish whether the executable order price is exactly the first-low OHLC value, a price inside the correction, or another source-defined boundary. No buffer/tick/spread rule is stated.

### 5. Pending-order lifecycle is source-confirmed

At 39:26 the source explains that the structural invalidation distance is known before fill. At 39:48–40:07 it explains that if another candle forms, the existing order can be deleted and replaced with a new order appropriate to the new distance to SL; if the distance is not materially larger, the teacher may keep the original order.

**Decision:** pending-limit lifecycle is part of the demonstrated execution model. The exact deterministic replacement threshold is not source-frozen.

### 6. Structural invalidation is source-confirmed

At 39:26 the source states that if price returns to the illustrated invalidation area, the scenario is cancelled. Earlier at 33:10–33:23 the source explains the conceptual reason: return to the lower structural level destroys the validity of the trend that created the setup.

**Decision:** structural invalidation is canonical semantics. Exact OHLC/tick placement behind the origin remains unresolved.

### 7. 2X is a separate management/add-on module

At 38:05 the source describes a second trade as `2X`. At 22:43 it explicitly describes 2X as entering when price reaches half of the target. At 42:26–42:37 it distinguishes TP1 and TP2 and says the teacher generally uses TP1, while TP2 is larger and should be backtested.

At 57:14 the source gives an example where 2X contributes additional return relative to the initial risk.

**Decision:** 2X is source-confirmed as a distinct management/add-on module, not the same thing as the core first entry. Exact target definition for the 2X trigger remains a separate resolution item.

## Geometry state after V2

| Component | State | Reason |
|---|---|---|
| SP2L identity | RESOLVED | direct source naming |
| Spike semantic | RESOLVED | multiple source-recognized constructions |
| Breakout + follow-through | RESOLVED | explicit source discussion |
| P-Gap semantic | RESOLVED | explicit P-GAP vs E-GAP distinction |
| P-Gap executable formula | BLOCKED | boundaries/index/touch/size unresolved |
| AB=CD semantic | RESOLVED | explicit source statement |
| Leg-1 A/B exact OHLC anchors | BLOCKED | candle-level mapping still ambiguous |
| Leg-2 C exact OHLC anchor | BLOCKED | not explicitly identified |
| Entry direction/type | RESOLVED | pending limit during correction |
| Entry anchor for demonstrated variant | PARTIALLY RESOLVED | first-low / first-pullback is explicit |
| Exact entry price | BLOCKED | equality/buffer/inside-correction convention unresolved |
| Structural invalidation concept | RESOLVED | explicit scenario cancellation |
| Exact SL price | BLOCKED | wick/body/buffer/origin convention unresolved |
| 2X existence | RESOLVED | distinct source module |
| 2X exact trigger formula | BLOCKED | target linkage not fully resolved |
| TP1/TP2 existence | RESOLVED | explicit source discussion |
| Canonical TP rule | BLOCKED | management module not fully frozen |

## What can now be frozen safely

A **semantic execution contract** can be frozen for research fixtures:

`context/range -> source-recognized Spike -> breakout + follow-through with source-recognized P-Gap -> correction -> first-low / first-pullback entry opportunity -> pending limit -> structural invalidation if the source-defined origin/invalid area is reclaimed -> second leg expected approximately equal to Leg 1.`

This contract is suitable for synthetic-discrimination work, but it is **not yet a production OHLC specification**.

## Synthetic fixture implications

The next fixtures should specifically discriminate:

1. first-low entry vs later higher-low entry;
2. exact-low fill vs entry inside the correction;
3. wick vs body interpretation for P-Gap boundaries;
4. first-candle vs later-candle P-Gap timing;
5. Spike-origin vs structural-swing SL anchor;
6. candidate A/B anchors for Leg 1;
7. candidate C anchors for Leg 2;
8. TP1/AB=CD/2X relationships without optimizing any tolerance.

No historical optimization is permitted to choose among these candidates.

## Gate state

- SOURCE RESOLUTION: **substantially advanced; transcript artifact recovered; semantic contract strengthened**
- SYNTHETIC FIXTURES: **ready for expanded discrimination**
- FROZEN GEOMETRY: **still blocked**
- DEV: **locked for canonical SP2L**
- UNTouched VALIDATION: **locked**
- FRESH HOLDOUT: **locked**
- PRODUCTION: **unchanged**

## Hard rule

Do not convert the newly recovered first-low wording into an exact executable price rule until the visual/source geometry proves the exact price convention. Do not use backtest performance to choose the convention.
