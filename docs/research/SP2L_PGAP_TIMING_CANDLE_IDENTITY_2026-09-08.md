# SP2L P-Gap Timing / Candle Identity Resolution — 2026-09-08

## Objective
Resolve whether the authoritative source fixes P-Gap to a universal candle index or a universal three-candle timing pattern.

## Primary source inspection
The source teaching sequence around 34:14–35:37 was inspected frame-by-frame and cross-checked against the transcript. The instructor describes P-Gap as a visual marker of where the breakout occurred and explicitly presents multiple accepted-looking constructions.

The narration describes, among other variants:
- breakout followed by continuation/follow-through and P-Gap evidence;
- a directional sequence with higher lows before the gap evidence;
- another distinct candle arrangement that is still treated within the same Spike hierarchy.

The source explicitly says these states are currently treated as the same Spike concept rather than being separated into different strategy modules.

## Source-safe timing invariant
P-Gap is not established as a fixed candle number such as “always candles 1–3”. The strongest defensible invariant is:

`P-Gap evidence is associated with the valid breakout / follow-through structure inside the source-defined Spike sequence.`

This is a relational timing rule, not an executable candle-index formula.

## What the deeper visual inspection adds
The blue P-Gap rectangles are drawn after the instructor has differentiated the constructions and are visually attached to the local breakout/gap area. However, the rectangles do not provide machine-readable OHLC boundaries. In particular, they cannot distinguish with source-safe certainty between wick and body edges, adjacent-candle extremes, or a boundary spanning a different pair of candles.

The accepted-looking examples therefore provide positive discrimination evidence for a gap/non-overlap concept, but not enough information to identify the exact pair of candle fields used by the instructor.

## Explicit non-conclusions
The inspection does NOT authorize any of the following as canonical:
- fixed three-candle P-Gap;
- previous High -> next Low as the universal formula;
- body-to-body formula;
- wick-to-wick formula;
- a fixed candle offset from the breakout candle;
- equality/touch behavior;
- minimum gap size;
- generic FVG equivalence.

## Gate decision
**Semantic timing:** partially resolved — P-Gap belongs to the breakout/follow-through / Spike sequence.

**Exact candle identity:** unresolved.

**Exact OHLC boundary:** unresolved.

**Frozen Geometry:** remains BLOCKED.

No production code was changed and no historical performance was used to choose among these interpretations.

## Next highest-value source action
Use the clearest real XAUUSD examples in which both the Spike structure and the subsequently drawn P-Gap/order level are simultaneously visible. The target observation is not merely “where the rectangle appears”, but whether the same candle field relationship can be demonstrated repeatedly across real examples. If it cannot, retain an explicit unresolved geometry state.
