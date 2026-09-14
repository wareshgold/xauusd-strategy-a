# SP2L Evidence Hunt — 2026-09-14

## Scope

Research-only evidence hunt following the transcript/video cross-resolution pass. Objective: test whether additional Tier-1 transcript evidence discriminates any remaining executable geometry. Source meaning outranks backtest performance. No canonical promotion, engine changes, optimization, or invented execution semantics.

## Evidence reviewed

Authoritative transcript: `پورصمدیSP2L TRANSCIBE.txt`.

### P-GAP / breakout

31:02–31:18: breakout is described as a candle closing beyond the prior level followed by a follow-through candle that cannot return/overlap the prior area. 31:43–31:55 identifies P-GAP as a sign of the breakout and explicitly distinguishes it from E-GAP.

33:51–35:37: the source presents two orderings: breakout/follow-through followed by higher lows and P-GAP, or higher lows followed by the gap. The source treats these as the same strategy concept for the current strategy.

Result: semantics strengthened; exact candle pair, index convention, and OHLC/wick/body boundaries remain undiscriminated.

### Entry / SL / pending refresh

38:38–39:48: correction starts after the spike; the correction is described as moving below the first low; a Buy Limit can be placed during the first three candles; return to the cited lower level invalidates the scenario and establishes the SL distance. Later candle formation can lead to deleting/replacing the pending order, with retention/movement discussed when the new distance is not large enough to damage money management.

41:18–42:26: the source shows Buy + SL, optional 2X position, and TP1/TP2 choices.

Result: source behavior is confirmed, but the exact entry price anchor, structural OHLC boundary, and deterministic refresh threshold are still absent.

### AB=CD / Leg 2

35:50–37:08: three spike constructions are accepted conceptually; the source explicitly reframes AB=CD at candle level and states that the expected second leg completes to the same size as the first leg.

Result: `Leg2Magnitude ≈ Leg1Magnitude` is confirmed semantically. A/B/C/D candle/price endpoints and equality tolerance remain unresolved.

### TP1 / TP2 / 2X

41:26–42:37: 2X is presented as an optional second position and TP1/TP2 are explicit target choices; the source says TP1 is generally preferred and TP2 is relatively large for the strategy.

49:47–51:25: target 1 is emphasized as the practical target in an early-trend/P-GAP example, while later extension toward E-GAP is treated as riskier.

Result: target concepts and preference are source-confirmed, but no unique executable TP1/TP2/2X price formula is supplied by the reviewed text.

### Bearish mirror

31:43–32:54: the source distinguishes P-GAP/E-GAP and includes a strong bearish trend example where the first pullback is used for a sell entry.

The later bearish educational/order examples provide sell and SL semantics, but they do not uniquely state that every bullish anchor, trigger classifier, invalidation boundary, and projection rule is to be mechanically sign-inverted.

Result: bearish examples are confirmed; deterministic mirror remains unresolved.

## Discrimination matrix after hunt

| Dimension | New source discriminator? | Status |
|---|---|---|
| P-GAP formula/indexing | No | BLOCKED |
| Entry price anchor | No | BLOCKED |
| Leg-2 start anchor | No | BLOCKED |
| Structural invalidation OHLC boundary | No | BLOCKED |
| Pending retain/replace threshold | No | BLOCKED |
| 1/2/3-candle acceptance classifier | No | BLOCKED |
| AB=CD A/B/C/D anchors | No | BLOCKED |
| AB=CD equality tolerance | No | BLOCKED |
| TP1/TP2 executable formulas | No | BLOCKED |
| 2X executable formula | No | BLOCKED |
| Deterministic bearish mirror | No | BLOCKED |

## Stop-condition assessment

The additional transcript search does not create a source discriminator for any remaining executable dimension. Therefore the finite source-resolution stop condition is reached for this evidence-hunt pass.

This is **not** a statement that the strategy has no edge. It is a statement that the authoritative material currently available does not uniquely define enough geometry to justify canonical executable rules.

## Next permitted gate

Do not select among unresolved hypotheses by backtest performance. Do not introduce generic P-GAP, Fibonacci, AB=CD tolerance, candle buffers, fill semantics, or sign-inverted bearish rules as canonical behavior.

The next source-resolution advance requires genuinely new Tier-1/2 evidence that visibly discriminates at least one blocked dimension, ideally an annotated source frame/passage with exact candle boundaries or explicit price construction.

## Status

`SOURCE_RESOLUTION_STOPPED_PENDING_NEW_TIER1_TIER2_DISCRIMINATOR`
