# SP2L Source-Resolution Batch — F12–F15 — 2026-09-14

## Purpose

Consolidate the remaining synthetic source-discrimination dimensions before any geometry freeze.

This document is non-canonical research. It does not authorize engine implementation or profitability-based selection.

## F12 — Trigger Acceptance

### Source-resolved

The source demonstrates a family of one-, two-, and three-candle trigger constructions. Therefore a universal one-candle-only trigger rule is rejected.

### Still unresolved

The source does not uniquely provide a deterministic acceptance classifier covering candle indexing, required confirmation, overlap/priority when multiple constructions coexist, and rejection conditions.

### Result

`SOURCE-DISCRIMINATED` for family existence.

`BLOCKED` for the final executable classifier.

No numerical threshold or priority rule is invented.

---

## F13 — 2X / TP1 / TP2

### Source-resolved

The source supports a second-position / reward-management concept and a preference for TP1. These are preserved as semantic concepts.

### Still unresolved

No unique executable formula is established for:

- exact meaning of 2X;
- target anchor;
- fraction/position-management sequence;
- TP1 formula;
- TP2 formula;
- relationship to AB=CD for every variant.

### Negative controls

Do not substitute 2R, 1:1, 50%, Fibonacci, or any fixed target formula unless directly source-confirmed.

### Result

`SOURCE-DOES-NOT-DISCRIMINATE` at executable level.

---

## F14 — AB=CD

### Source-resolved

The source explicitly supports the magnitude relationship:

`Leg2Magnitude ≈ Leg1Magnitude`

This is a structural/reward relationship, not a license to invent four-point geometry.

### Still unresolved

The source does not uniquely determine:

- A candle/index;
- B candle/index;
- C candle/index;
- D endpoint semantics;
- OHLC field selection;
- equality tolerance;
- whether Entry universally equals C.

### Negative controls

Do not substitute Fibonacci ratios or choose A/B/C anchors from backtest performance.

### Result

`SOURCE-DOES-NOT-DISCRIMINATE` at executable anchor/tolerance level.

---

## F15 — Bearish Mirror

### Source-resolved

There is insufficient evidence to claim that every bullish executable rule can simply be sign-flipped into a bearish implementation.

### Still unresolved

The available evidence does not uniquely establish a complete deterministic bearish specification covering:

- P-Gap geometry;
- Entry anchor;
- Spike-origin invalidation;
- pending refresh;
- trigger taxonomy;
- AB=CD anchors;
- 2X/targets.

### Negative controls

Do not assume wick/body mirroring, sign-flipped P-Gap, sign-flipped AB=CD anchors, mirrored refresh thresholds, or mirrored 2X/TP rules without direct evidence.

### Result

`BLOCKED` pending sufficient bearish source evidence.

---

## Combined F12–F15 gate

| Fixture | Source result | Executable status |
|---|---|---|
| F12 | 1/2/3-candle family confirmed | BLOCKED classifier |
| F13 | 2X/TP concepts confirmed | SOURCE-DOES-NOT-DISCRIMINATE |
| F14 | Leg2 ≈ Leg1 confirmed | SOURCE-DOES-NOT-DISCRIMINATE |
| F15 | Complete bearish mirror not evidenced | BLOCKED |

## Overall gate

- SOURCE RESOLUTION: **IN PROGRESS — remaining executable dimensions unresolved**
- SYNTHETIC FIXTURES F8–F15: **DEFINED and adjudicated to current evidence boundary**
- FROZEN GEOMETRY: **BLOCKED**
- DEV: **LOCKED**
- UNTOUCHED VALIDATION: **LOCKED**
- ROBUSTNESS/STABILITY: **LOCKED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **LOCKED**

## Stop condition

This pass deliberately does not force a geometry freeze. A source-resolution dimension may advance only when authoritative evidence uniquely discriminates the executable rule. Otherwise its unresolved status is the correct research result.
