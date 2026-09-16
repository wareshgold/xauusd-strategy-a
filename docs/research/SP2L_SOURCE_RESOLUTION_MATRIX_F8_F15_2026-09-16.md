# SP2L Source Resolution Matrix — F8–F15 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F15** after completed evidence batches and direct forensic inspection of the user-supplied primary SP2L training video, including worked-trade reconstruction and micro-forensic inspection of order/2X/risk diagrams. This matrix records what the artifact supports and what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / ACTIVATION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **PRIMARY-ARTIFACT + WORKED-EXAMPLE EVIDENCE STRENGTHENED / PRICE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **PRIMARY-ARTIFACT ORDER-LIFECYCLE + WORKED-EXAMPLE EVIDENCE / REPLACEMENT RULE UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **PRIMARY-ARTIFACT TRIGGER + WORKED-EXAMPLE EVIDENCE STRENGTHENED / EXACT TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **PRIMARY-ARTIFACT CONFIRMED CONCEPT + PRIMARY GEOMETRIC MIDPOINT EVIDENCE / EXECUTION SEMANTICS UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **PRIMARY-ARTIFACT EXPLICIT AB=CD + TWO-LEG SYMMETRY EVIDENCE STRENGTHENED / A-B-C-D ANCHORS UNRESOLVED / EQUALITY-TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **PRIMARY-ARTIFACT + WORKED-EXAMPLE DIRECTIONAL EVIDENCE / EXACT EXECUTION GEOMETRY UNRESOLVED** | No | BLOCKED |

## Batch 21 — primary F14/F8/F12 micro-forensic update

Batch 21 inspected the dense primary teaching sequence around approximately 36:00–44:00 and recorded the direct visual evidence in `SP2L_BATCH21_PRIMARY_F14_F8_F12_MICRO_FORENSIC_2026-09-16.md`.

### F14 — AB=CD

The primary artifact visibly writes `AB=CD` around frame 2190 and retains the annotation around frame 2220. Around frame 2250 it shows a hand-drawn two-leg price path with visually corresponding impulse segments. This materially strengthens the primary evidence for an explicit two-leg symmetry/equality concept.

The artifact still does not uniquely label A, B, C, and D to exact candle prices/indices, does not state wick/body/OHLC anchor semantics, and does not state whether equality is exact or tolerance-based. No numeric tolerance or rounding rule is exposed.

### F8 — swing/level selection

Frames around 2310 mark multiple local lower points; frames around 2340 and 2490 show multiple horizontal structural/order levels, with `Buy` and `SL` visually separated. This strengthens the existence of local structural level selection but does not uniquely determine which candidate low is selected by an executable algorithm.

### F12 — breakout / trigger

The primary artifact visibly states `Valid BO = P-Gap` in the same teaching sequence. Frames around 2340–2400 show `BO`, a horizontal order level, and `Buy Limit`; frame 2490 labels `Buy` and a separate `SL` level. This supports a source-visible chain of breakout validation concept → structural level → pending Buy Limit → separate SL.

Exact P-Gap numeric definition, intrabar vs close semantics, 1/2/3-candle taxonomy, touch/break/close activation, retest/fill semantics, and exact order-placement timing remain unresolved.

## Gate decision

**Source Resolution: PARTIAL PASS — materially strengthened by direct primary visual evidence.**

**Frozen Geometry: BLOCKED** — F14 is conceptually confirmed but deterministic anchors/tolerance remain unresolved; F8 and F12 remain unresolved at executable-rule level.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

## Explicit non-canonical items preserved

- exact swing-selection algorithm;
- exact Entry activation timestamp/price semantics;
- exact Leg-2 start semantics;
- exact SL boundary/buffer;
- pending-order replacement/refresh/expiry/invalidation state machine;
- exact 1/2/3-candle trigger taxonomy;
- complete 2X activation/order/fill/sizing semantics (while midpoint geometry is primary-artifact-supported);
- A/B/C/D AB=CD anchors and equality/tolerance;
- exact bearish mirror geometry;
- P-Gap numeric formula;
- any assumption that account-table TP/SL ratios define canonical R semantics.

No backtest variant was selected from this evidence and no production implementation was changed.
