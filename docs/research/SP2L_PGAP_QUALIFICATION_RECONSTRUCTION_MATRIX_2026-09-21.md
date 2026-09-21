# SP2L P-Gap Qualification Reconstruction Matrix — 2026-09-21

## Purpose

The geometric primitive has now been tested. The next layer is qualification: determining when a strict adjacent-candle gap is the source-described P-Gap rather than merely a geometric gap.

This matrix is deliberately non-canonical.

| Dimension | Current evidence | Status | Action |
|---|---|---|---|
| Adjacent non-overlap | Source wording: high/low do not overlap | SOURCE-DISCRIMINATED | Tested |
| Construction sequence | Breakout→follow-through→gap and higher-lows→gap are described as equivalent concepts | SOURCE-DISCRIMINATED | Preserve variants; do not choose precedence |
| Candle indexing | Examples use different formation locations | UNRESOLVED | Reconstruct from labelled examples |
| Early-trend context | Source contrasts early opportunity/P-Gap with later extension/E-Gap | PARTIAL | Need deterministic boundary |
| Minimum gap size | No unique numeric threshold in preserved evidence | UNRESOLVED | Do not inherit legacy 1.0 |
| Breakout relation | P-Gap is associated with valid breakout/spike | PARTIAL | Need exact candle/level relation |
| Late/E-Gap exclusion | Source distinguishes P-Gap from E-Gap | PARTIAL | Need explicit classifier |
| Bearish mirror | Geometric mirror is source-consistent | SOURCE-CONSISTENT | Not independently promoted |
| Legacy fixed indexing | Existing implementation only | NOT SOURCE EVIDENCE | Quarantine |

## Current reconstructed model

Only the deterministic geometric predicate is supported:

- bullish: High[i] < Low[i+1]
- bearish: Low[i] > High[i+1]

This is a candidate primitive reconstructed from source, not a claim that the author stated this algebraic notation.

## What the fixtures prove

1. Strict non-overlap can be tested independently.
2. Equality is excluded from the primitive because the source describes non-overlap.
3. Multiple source-described construction families can be represented without forcing one sequence.
4. A geometric gap can be positive while P-Gap qualification remains unresolved.
5. The old fixed-index implementation must not be mistaken for the source rule.

## Next research pass

1. Map each labelled source example candle-by-candle.
2. Identify the exact pair where non-overlap appears.
3. Record the immediately preceding/following structure.
4. Compare P-Gap examples against later/E-Gap examples.
5. Derive the smallest common qualification predicate.
6. Add counterexample fixtures.
7. Only then consider implementation integration.

## Gate

- P-Gap primitive: **DISCRIMINATED / TESTED**
- P-Gap qualification: **BLOCKED**
- Canonical P-Gap formula: **NOT FROZEN**
- Frozen Geometry: **BLOCKED**
- Forward Test: **UNCHANGED**
- Production: **DISABLED**
