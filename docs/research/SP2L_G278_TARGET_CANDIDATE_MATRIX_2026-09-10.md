# G278 — Target Candidate Geometry Matrix

Date: 2026-09-10

## Purpose
Cross-reference the source schematic, numeric target annotations, and earlier order-panel evidence without promoting any candidate to canonical geometry.

| Candidate | Source support | Conflict / missing bridge | Status |
|---|---|---|---|
| TP1 = 1R from Entry | Schematic visually resembles equal risk intervals | Exact numeric construction not stated; order examples do not prove it | HYPOTHESIS |
| TP2 = 2R from Entry | Schematic visually resembles two risk intervals | Concrete TP values do not consistently equal simple 2R | REJECTED_AS_CANONICAL |
| TP1 = +250 points | `250 point` explicitly appears in target-construction sequence | No explicit statement that it is TP1 selector or exact unit mapping | HYPOTHESIS |
| TP2 = +500 points | `500 point` explicitly appears | Same unresolved unit/selector problem | HYPOTHESIS |
| TP1/TP2 = round levels | `Round level` explicitly appears and is annotated near construction | No explicit rule selecting which round level is TP1/TP2 | HYPOTHESIS |
| TP = AB=CD endpoint | AB=CD explicitly taught elsewhere | No direct bridge from AB=CD endpoint to terminal TP in this construction | HYPOTHESIS |
| TP derived from Leg-2 projection | Second leg and target concepts are source-supported | Projection anchors and formula unresolved | HYPOTHESIS |

## Hard exclusion
The matrix must not collapse to a single formula using backtest performance. The order-panel example with Entry 3229.08, SL 3237.12 and TP 3213.44 is incompatible with treating the displayed TP as an exact simple 2R calculation from those values.

## Decision
No executable terminal-target selector is frozen. The highest-value next source search is an explicit worked example linking one of: `250 point`, `500 point`, `Round level`, `AB=CD`, or a named candle/price to TP1/TP2.