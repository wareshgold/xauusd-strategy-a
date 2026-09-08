# SP2L Leg-1 / AB=CD Geometry Gate — 2026-09-08

## Objective
Resolve whether the authoritative source uniquely defines the executable Leg-1 measurement and AB=CD projection anchors.

## Primary-source evidence
The source explicitly presents `SPIKE-2LEG`, writes `AB=CD`, and explains that after the first movement and correction the next leg is expected to have the same size. The narration also contrasts this candle-level treatment with classical internet AB=CD material that uses A/B/C and Fibonacci-style mapping.

The source therefore supports the semantic rule:

`Leg 2 magnitude ≈ Leg 1 magnitude`

and explicitly supports the name/relationship `AB=CD`.

## Visual inspection
The source frames around the AB=CD slide show the handwritten `AB=CD` annotation over a Spike sequence and later show the correction / entry diagrams. The drawings are conceptual and do not provide machine-readable price coordinates or unambiguous labels for A, B, C, and D.

The real XAUUSD chart frames around the later examples contain green setup regions, horizontal levels, and management annotations. They do not expose a sufficiently precise, source-labeled A/B/C/D coordinate system from which a universal OHLC formula can be recovered.

## Candidate anchor interpretations

| Hypothesis | Interpretation | Status |
|---|---|---|
| H1 | Leg 1 = Spike-origin price to Spike extreme; project equal distance from correction reference | UNRESOLVED |
| H2 | Leg 1 = first correction/reference extreme to Spike extreme | UNRESOLVED |
| H3 | Leg 1 = breakout/level reference to Spike extreme | UNRESOLVED |
| H4 | Classical A/B/C/D harmonic mapping | REJECTED AS CANONICAL |
| H5 | Same structural anchors but using candle body edges rather than wick extremes | UNRESOLVED |

H1 is a useful research hypothesis because it is compatible with the source's language of the initial Spike movement, but compatibility is not source proof.

## Important source constraint
The source explicitly says its AB=CD treatment is candle-level and distinguishes it from classical internet AB=CD/Fibonacci treatment. Therefore classical harmonic anchor conventions must not be imported into Strategy A.

## Tolerance
No source evidence found that defines an exact numerical tolerance for `AB=CD`. The phrase supports equality/approximately equal leg magnitude semantically, but does not establish a deterministic percentage, price-unit tolerance, ATR multiple, or rounding rule.

## Target semantics
The source strongly supports a base TP of 1:1 and discusses TP2 / 2X as larger or additional management. These management examples do not establish that every AB=CD projection must be executed as a single fixed TP formula.

## Decision
- AB=CD semantic: **RESOLVED**
- approximately equal Leg-1 / Leg-2 semantic: **RESOLVED**
- exact Leg-1 anchors: **UNRESOLVED**
- exact A/B/C/D candle identities: **UNRESOLVED**
- wick vs body: **UNRESOLVED**
- AB=CD tolerance: **UNRESOLVED**
- exact projection origin: **UNRESOLVED**
- classical Fibonacci mapping: **NOT CANONICAL**

## Gate impact
FROZEN GEOMETRY remains **BLOCKED**.

No executable LegProjection rule is promoted from these observations. No historical optimization may choose among H1-H5. Synthetic fixtures exist only to prevent accidental promotion of an unresolved anchor.

## Next source-resolution action
If further source evidence is pursued, the highest-value task is to isolate a real trade/example where the source visibly draws the first leg, correction reference, and second-leg target on the same candle sequence with enough resolution to map each line to OHLC. Without that evidence, the correct decision is to preserve the semantic contract and leave executable geometry unresolved.
