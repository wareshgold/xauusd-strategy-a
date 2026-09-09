# SP2L Source Ledger v1 — 2026-09-09

## Evidence policy

Primary evidence is the creator's source material: YouTube video `7HEC5mO3d3U`, its recovered transcript, and direct frame inspection. Secondary web material is context only and cannot override primary evidence.

## Canonical concepts and current evidence status

| Concept | Status | Source evidence | Deterministic implication | Open question |
|---|---|---|---|---|
| Market context / range | STRONGLY SUPPORTED | Teacher discusses range/clean-vs-dirty market and avoiding range interiors | Context state exists | Exact range algorithm unresolved |
| Breakout (BO) | CONFIRMED | Source repeatedly labels BO and discusses valid breakout | Breakout is a required structural event | Exact breakout threshold/anchor unresolved |
| Spike | CONFIRMED | Dedicated source section presents multiple spike constructions | Spike is a directional first-leg structure | Exact taxonomy-to-rule mapping still needs formalization |
| P-Gap | CONFIRMED CONCEPT / GEOMETRY UNRESOLVED | Source explicitly links valid BO with P-Gap and distinguishes P-Gap from E-Gap/Common-Gap | P-Gap must be represented as a first-class concept | Formula/anchors/candle relation unresolved |
| Correction / pullback | CONFIRMED | Source describes correction below/around structural low and pending-limit placement during correction | Correction is the entry phase | Exact structural boundary unresolved |
| Pending-limit entry | CONFIRMED | Transcript and frames explicitly show Limit / Buy Limit and pre-positioned order | Entry mechanism is pending limit | Exact price anchor unresolved |
| Structural invalidation | CONFIRMED | Source explicitly discusses SL and deletion/replacement when structure/risk changes | Stop is structural, not arbitrary fixed-distance | Exact invalidation anchor and replacement threshold unresolved |
| Leg 1 / Leg 2 | CONFIRMED | Source explicitly labels first/second leg and discusses continuation | Setup contains two directional legs | Exact anchor definitions unresolved |
| AB=CD | CONFIRMED | Direct slide explicitly states AB=CD | Leg-2 projection must use source relationship | Exact A/B/C/D anchors and tolerance unresolved |
| TP1 / TP2 | CONFIRMED | Source explicitly distinguishes TP1 and TP2; teacher generally uses TP1 and says TP2 should be backtested | Exit candidates are source-defined | Exact implementation/priority unresolved |
| 2X | CONFIRMED CONCEPT / FORMULA UNRESOLVED | Source explicitly labels 2X and describes a half-target-type trigger | 2X is source terminology, not yet a frozen numeric rule | Exact calculation unresolved |
| Trigger | CONFIRMED CONCEPT / TAXONOMY UNRESOLVED | Source discusses 1/2/3-candle trigger examples | Trigger is part of setup | Exact trigger family and acceptance criteria unresolved |
| New York / good hours | SUPPORTED | Source discusses good hours/New York | Time-of-day may be relevant | Whether it is canonical filter unresolved |

## Important negative findings

The source review does NOT authorize treating the following as canonical Strategy A rules: liquidity sweep, BOS/MSS, displacement, generic FVG, generic retest, Fibonacci retracement, market-close reclaim, or a generic three-candle imbalance substituted for P-Gap.

## Entry geometry finding

Current visual evidence supports an abstraction stronger than a fixed initial-low-only interpretation: the teacher demonstrates a pending Buy Limit at a relevant/current structural higher-low while the structural invalidation remains below. Transcript language also references the first Low. Therefore the canonical abstraction remains **Relevant Structural Low/High → Pending Limit**, with the exact anchor unresolved.

## Leg-2 distinction

Source discussion of a later pullback to the start of Leg 2 does not prove that the start of Leg 2 is the original entry price. Direct visual examples show separate Entry and Leg-2/target-region levels. Therefore `Entry = Leg2Start` is rejected as a canonical assumption.

## Status gate

SOURCE RESOLUTION is not complete. The ledger is a frozen evidence map, not a frozen trading specification.
