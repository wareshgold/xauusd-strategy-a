# SP2L P-Gap Visual Resolution — 2026-09-08

## Objective
Determine whether the authoritative source visuals uniquely define the executable P-Gap OHLC geometry without importing a generic FVG/imbalance formula.

## Source material inspected
The authoritative SP2L video was inspected around the P-Gap teaching sequence (~35:00–37:00), including the slide that explicitly states `Valid BO = P-Gap` and shows four candle constructions: three accepted-looking variants and one red-X rejected construction.

## Observations

### 1. P-Gap is a validity condition for the breakout
The source explicitly associates a valid breakout with P-Gap. The narration describes a gap/non-overlap relationship in the breakout/follow-through context.

### 2. Three visually distinct constructions are accepted-looking
The source presents three different candle arrangements as valid-looking P-Gap/breakout constructions. This is important: the source does not present one rigid three-candle drawing as the only representation.

### 3. The rejected construction does not establish the exact predicate
The red-X example appears to lack the source-described gap/non-overlap condition, but the visual alone does not establish whether rejection is caused by overlap, sequence, candle count, or another unstated condition. Therefore the rejected example is recorded as discrimination evidence, not as a complete executable predicate.

### 4. The blue rectangles are not machine-safe OHLC boundaries
The highlighted P-Gap zones visually occupy the area associated with the non-overlap/gap relationship, but the frames do not uniquely establish whether the rectangle corresponds to:

- previous High -> next Low;
- previous Low -> next High for bearish symmetry;
- body-edge boundaries;
- wick extremes;
- a multi-candle boundary;
- a manually illustrated conceptual zone.

No equality/touch convention is visible with sufficient certainty.

### 5. Timing remains unresolved
The three accepted variants visibly differ in where the gap-like relationship appears in the local candle sequence. The source treats these variants as conceptually valid within the strategy. Exact candle-index/timing rules therefore remain unresolved.

### 6. Minimum size is unresolved
No source-safe numerical minimum gap size can be extracted from the teaching slide. No tick/point threshold is promoted.

## Candidate matrix

| Candidate interpretation | Status |
|---|---|
| P-Gap means source-described non-overlap/gap in breakout context | SOURCE-CONFIRMED SEMANTIC |
| P-Gap is required for a valid breakout | SOURCE-CONFIRMED |
| Generic three-candle FVG formula | REJECTED AS CANONICAL |
| Previous High -> next Low | UNRESOLVED |
| Body-to-body gap | UNRESOLVED |
| Wick-to-wick gap | UNRESOLVED |
| Multi-candle gap boundary | UNRESOLVED |
| Exact candle timing/index | UNRESOLVED |
| Equality/touch counts as gap | UNRESOLVED |
| Minimum gap size | UNRESOLVED |

## Gate decision

**Semantic P-Gap:** RESOLVED.

**Executable P-Gap geometry:** BLOCKED.

No formula is added to production or canonical strategy code. Generic FVG logic remains research-only and cannot be used as a proxy for P-Gap.

## Next source-resolution action
Cross-check the P-Gap teaching sequence against the clearest real XAUUSD examples where the instructor has already drawn the gap/order levels, looking specifically for a repeated OHLC boundary relationship. If the repeated relationship still cannot be established, keep P-Gap unresolved and proceed to a formal geometry specification containing explicit `UNRESOLVED` states only.
