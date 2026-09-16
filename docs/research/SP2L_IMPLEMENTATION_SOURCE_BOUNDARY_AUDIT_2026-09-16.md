# SP2L Implementation vs Source Boundary Audit — 2026-09-16

## Purpose

Identify implementation rules that are more specific than currently source-discriminated evidence. This is an audit only; no geometry is changed.

## Findings

### EntryTrigger
Current implementation uses the first post-correction candle close beyond the correction extreme as Entry. Source evidence supports correction/trigger concepts, but does not uniquely establish this exact close-based classifier or price anchor.

Status: `WORKING TEST RULE / NOT CANONICAL`

### Invalidation
Current implementation uses the correction extreme and close-based breach. Source confirms structural invalidation is distinct from risk budget, but exact OHLC anchor, wick/body semantics, buffer, and breach condition remain unresolved.

Status: `WORKING TEST RULE / NOT CANONICAL`

### LegProjection
Current implementation defines Leg1 as absolute(last.close - first.open) and projects TP1 from correction extreme. Source confirms the Leg-2/AB=CD magnitude concept but does not uniquely establish these anchors or tolerance.

Status: `WORKING TEST RULE / NOT CANONICAL`

### Breakout / Follow-through
Current implementation has fixed lookback and timing parameters. These remain research parameters unless source evidence explicitly discriminates them.

Status: `WORKING TEST PARAMETERS / NOT CANONICAL`

### SpikeDetector
Directional fraction and overlap thresholds are implementation parameters. P-Gap is intentionally not inferred by the detector. These thresholds must not be treated as source rules.

Status: `WORKING TEST PARAMETERS / NOT CANONICAL`

### QualityScore / Context
EMA, round-level, session, and score thresholds are context/test parameters. The current score is explicitly described as research-stage and not a validated edge claim.

Status: `RESEARCH ONLY`

## 125R consequence

The audit does not modify or suppress the 125R observation. Its arithmetic remains auditable; geometry remains unresolved.

## Gate consequence

No implementation rule is promoted by this audit. Frozen Geometry remains `BLOCKED`; validation remains locked; Production remains `OFF`.
