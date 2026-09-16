# SP2L Batch 15 — Source Evidence F13/F14 — 2026-09-16

## Scope
P2 source-resolution pass for F13 (2X) and F14 (AB=CD geometry). Source meaning outranks implementation/backtest performance. No canonical formula is introduced where primary evidence is incomplete.

## F14 — AB=CD geometry

### Evidence
Primary/author-associated SP2L training material is explicitly described as covering “ترکیب 2L با Spike” and “نحوه اوردگذاری با این استراتژی SP2L”. The indexed author-associated post also identifies the original SP2L training video and its lesson list. However, the indexed material does not expose a deterministic A/B/C/D labeling algorithm, price-field semantics, or numeric AB=CD tolerance.

Secondary TradingFinder material repeatedly identifies the model as a Spike + 2-leg AB=CD structure and describes the spike as the initial wave / AB and the continuation as CD. One MT4 description states that after a valid spike, the spike is treated as wave AB and continuation is wave CD; it also describes entry after retracement/breakout. These are secondary implementation descriptions, not sufficient primary evidence for exact anchors.

### Discrimination result
**SOURCE-CONFIRMED CONCEPT / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED**

Still unresolved:
- exact A anchor;
- exact B anchor;
- exact C anchor;
- exact D anchor;
- wick/body/open/close/structural-swing semantics;
- whether D is observed or projected;
- whether AB=CD means exact equality, a ratio, or a tolerance band;
- numeric tolerance and rounding.

No Fibonacci substitution, ratio, tolerance, or anchor selection has been promoted to canonical geometry.

## F13 — 2X

### Evidence
The author-associated training index explicitly lists a lesson titled “نحوه و دلیل ورود در 2x” (how and why to enter in 2X). This confirms that 2X is a source-level concept in the training material. A secondary SP2L description has previously exposed a 50%-of-Entry-to-SL re-entry concept, but the indexed primary training material does not expose enough text to verify that exact formula or its conditions.

### Discrimination result
**SOURCE-CONFIRMED CONCEPT / SECONDARY 50%-DISTANCE EVIDENCE / CANONICAL FORMULA UNRESOLVED**

Still unresolved:
- exact 2X price calculation;
- whether 50% Entry→SL is canonical;
- conditions enabling 2X;
- pending vs market execution;
- fill/re-entry semantics;
- relationship to TP1/SL and shared invalidation.

The secondary 50% observation remains a hypothesis only. It is not used in geometry freeze or backtest selection.

## Source hierarchy
1. Primary/author-controlled training material — strongest.
2. Author-associated publication/channel — corroborating access/index evidence.
3. TradingFinder/other secondary descriptions — terminology/corroboration only.

## Gate consequence
F13 and F14 remain unresolved at the executable-rule level. Frozen Geometry remains **BLOCKED**. Untouched Validation, Robustness/Stability, Fresh Holdout, and Production remain locked/off.

125R remains untouched.
