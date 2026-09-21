# SP2L P-Gap Source Reconstruction — 2026-09-21

## Purpose
Reconstruct a deterministic P-Gap detector from MohammadAli Poursamadi's source wording and preserved SP2L evidence. This is a research reconstruction, not yet a canonical production rule.

## Direct source evidence

The preserved transcript states:
- At 31:43, the breakout candle has P-GAP (گپ فشار) and P-GAP is distinct from E-GAP.
- At 32:12, not every visible gap should be treated as the same gap; formation location matters.
- At 34:14, P-GAP is explicitly presented as a visual marker for distinguishing the breakout.
- At 34:25, the first example is described as a gap where the high of one candle and the low of the next do not overlap.
- At 34:35, another example does not have the gap in the first candle but forms it in the following candle.
- At 34:44–35:02, two constructions are described: breakout followed by higher lows, and higher lows followed by the gap. The teacher says they are conceptually the same and are treated as one strategy condition.
- At 35:37–36:05, the source describes three closely related variants and treats the sequence as a spike.
- At 50:09, taking the opportunity early in the trend is described as P-GAP rather than E-GAP.
- At 50:56, after repeated extension the opportunity is described as more likely E-GAP, and entry is avoided.

## Reconstructed minimum geometric predicate

For a bullish gap event between adjacent candles i and i+1:

    High[i] < Low[i+1]

For a bearish gap event:

    Low[i] > High[i+1]

This expresses the source's explicit no-overlap observation. Equality is intentionally not included because the source wording says the high and low do not overlap.

## SP2L qualification layer

A gap event alone is NOT sufficient to classify a P-Gap.
The source additionally requires the event to be interpreted in the context of the early/strong directional trend and breakout construction. The source explicitly permits multiple sequence variants:
1. breakout -> continuation / higher lows -> gap
2. higher lows -> gap
3. closely related three-candle spike constructions

Therefore fixed indexing such as [-4],[-3],[-2] is NOT source-confirmed.

## Current reconstruction status

- P-Gap concept: SOURCE-CONFIRMED
- Adjacent-candle non-overlap geometry: SOURCE-DISCRIMINATED
- Bullish mirror: SOURCE-CONSISTENT
- Bearish mirror: SOURCE-CONSISTENT, not independently demonstrated in the preserved excerpt
- Exact sequence/indexing: UNRESOLVED
- Minimum gap size/price threshold: UNRESOLVED
- Definition of early trend as a deterministic condition: UNRESOLVED
- Exact breakout-level relation: PARTIAL
- Universal P-Gap formula for every SP2L variant: UNRESOLVED

## Research rule

Do not replace the existing forward-test P-Gap implementation yet. This document establishes the reconstructed geometric primitive only. A candidate detector must next be tested against source fixtures covering all stated sequence variants and explicit non-P-Gap/E-Gap counterexamples.

## Gate

Frozen Geometry remains BLOCKED until the sequence qualification can be made deterministic without contradicting the source.

## Cross-gate finding: Spike / Leg-1 boundary

The source visual ledger confirms that the Spike-to-two-leg construction is structural, not reducible to a fixed candle count. The Leg-1 endpoints are visually identifiable structural turning areas, while the exact OHLC field remains unresolved. The research branch therefore keeps anchor hypotheses separate from the source-confirmed structural concept.

This does not alter the P-Gap primitive or promote any executable rule. Frozen Geometry remains BLOCKED.


## AB=CD discrimination status

Source evidence supports the structural concept `AB=CD` / Leg 2 approximately matching Leg 1. Exact A/B/C/D OHLC anchors and any numeric tolerance remain unresolved. The new research matrix intentionally includes exact equality, near-equality, and materially unequal examples so future source evidence can discriminate them without backtest-driven selection.


## F08 / F09 / F15 geometry discrimination

### F08 Swing selection
Source evidence supports structural turning areas, but does not uniquely define swing-selection mechanics or wick/body fields. Research hypotheses are isolated without canonical promotion.

### F09 Entry geometry
Source evidence supports Pending Limit execution and a 1/2/3-candle family, while exact entry price geometry and replacement precedence remain unresolved. The close-reclaim implementation is not treated as source-canonical.

### F15 Bearish executable geometry
Bearish Spike/Leg-2 structure is source-consistent and visually mirrored. Bearish P-Gap remains only source-consistent rather than independently demonstrated in the preserved excerpt. No bearish executable formula is promoted.

**Gate result: PASS — unresolved geometry is explicitly quarantined. Frozen Geometry remains BLOCKED.**


## F11 / F12 execution-semantics discrimination

Pending-order lifecycle and trigger semantics are now isolated in research fixtures. The matrix distinguishes **touch / breach / close / fill** from lifecycle actions such as place, refresh, delete, replace, and cancel. This prevents a trigger observation from silently becoming a fill rule.

Source evidence supports Pending Limit usage and demonstrates deletion/replacement when structure or stop distance changes, but exact mandatory predicates, timeout, touch-versus-fill behavior, and activation precedence remain unresolved.

**Gate result: PASS — execution semantics remain explicitly unresolved and noncanonical.**
