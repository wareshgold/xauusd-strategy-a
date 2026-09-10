# SP2L G276 — Target Gate Decision

Date: 2026-09-10

## Gate matrix

| Item | Status |
|---|---|
| TP1 exists as source concept | CONFIRMED |
| TP2 exists as source concept | CONFIRMED |
| Entry/TP1/TP2/SL shown together | CONFIRMED |
| Round level discussed | CONFIRMED |
| Point-distance language discussed | CONFIRMED |
| 250/500 point exact unit | UNKNOWN |
| TP1 = 1R executable rule | NOT FROZEN |
| TP2 = 2R executable rule | NOT FROZEN |
| AB=CD -> TP mapping | UNKNOWN |
| Entry -> TP1 formula | UNKNOWN |
| Entry -> TP2 formula | UNKNOWN |
| Terminal TP selector | UNKNOWN |

## Decision

The source-resolution gate has materially improved for target construction, but Frozen Geometry is still BLOCKED because the source has not yet supplied a unique executable mapping from the schematic/annotations to exact order prices.

The correct implementation state is fail-closed:

- preserve TP1/TP2 as source concepts;
- preserve Round Level and point-distance as source concepts;
- do not choose between R-multiple, AB=CD, round-level, or point-distance constructions by backtest performance;
- do not merge multiple candidate constructions into a composite rule without source evidence.

## Next research target

Search the source for a concrete worked example that links the target-construction annotations to explicit numeric price levels. If no such bridge exists, formally freeze only the semantic target concepts and keep executable target geometry unresolved.

`FROZEN_GEOMETRY = BLOCKED`
`CANONICAL_TARGET_ENGINE = NOT_AUTHORIZED`
