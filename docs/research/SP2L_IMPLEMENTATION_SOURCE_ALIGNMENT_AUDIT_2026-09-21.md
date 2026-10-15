# SP2L Strategy A Implementation Audit — 2026-09-21

## Scope
Audit of the current Strategy A research implementation against the final primary-source boundary recorded in PR #263.

## Result
The implementation is **not identical to the teacher's executable rules**. It contains useful research primitives, but several executable choices are implementation hypotheses and must remain non-canonical.

## Confirmed / source-aligned concepts
- Spike research is separated from canonical trading decisions.
- Breakout + follow-through are represented as research-stage spike evidence.
- Bullish/bearish directional handling exists.
- P-Gap is explicitly labelled research-only and not promoted as a trading rule.
- Correction/HL-LH structure is represented as a research concept.
- Leg 2 is represented as a projection from a correction extreme.
- Strategy code does not claim the unresolved P-Gap detector is canonical.

## Non-canonical implementation choices that must remain quarantined
### P-Gap
Current `PGAPResearch.ts` uses a three-candle heuristic (`i-2` to `i`) and adjacent high/low separation. Source resolution has not established this indexing or three-candle formula as universal P-Gap logic.

### F08 Swing / correction
`CorrectionDetector.ts` defines correction using a fixed relationship to `spike.startPrice`. The source supports structural turning/reference areas and evolving HL/LH, but does not uniquely establish this deterministic pivot/threshold rule.

### F09 Entry
`EntryTrigger.ts` uses post-correction close reclaim and sets entry to candle close. The source supports Pending Limit and directional previous-candle references, but exact price field, trigger precedence, and 1/2/3-candle execution family remain unresolved. This implementation is therefore research-only.

### F10 Stop
`StructureStopLoss.ts` places the stop beyond the correction extreme. This is **not** the source-confirmed canonical F10 meaning. Source says SL is behind the candle from which the spike originated. Exact wick/body/buffer/invalidation semantics remain unresolved. The existing implementation must not be promoted.

### F14 AB=CD
`LegProjection.ts` currently measures Leg 1 as absolute distance from the spike-start candle open to spike-end candle close and projects from the correction extreme. Source supports structural AB=CD / approximately equal legs, but exact A/B/C/D anchors and tolerance are unresolved. This is a research hypothesis, not canonical geometry.

## Execution / lifecycle
Pending-order lifecycle, trigger-vs-fill semantics, timeout, replacement, 2X lifecycle and risk aggregation remain unresolved by source. Existing execution code must not be treated as the frozen teacher implementation.

## Gate decision
- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: BLOCKED
- Production: BLOCKED/DISABLED

## Required next step
Do not tune these implementation hypotheses to improve backtest results. The next promotion step requires new primary-source evidence that discriminates the unresolved alternatives, especially P0 F08 Swing and F10 Stop.

This audit is descriptive; it does not select a canonical geometry rule.
