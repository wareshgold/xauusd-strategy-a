# SP2L Remaining Source Blockers Matrix — 2026-09-21

## Purpose

Consolidate the current Primary-Source forensic state for F08–F13 and P-Gap after the F10, F11 and F12 audits. This document is a source-resolution boundary, not a strategy specification.

**Rule:** source meaning outranks implementation/backtest performance. No unresolved item is promoted to canonical geometry.

## Status Matrix

| Feature | Current status | What Primary Source supports | Executable blocker | Further primary-video forensic value |
|---|---|---|---|---|
| F08 Structural Correction / Swing Selection | PARTIAL / UNRESOLVED | Structural correction and relevant Low/High; actionable reference can evolve with structure | Universal swing-selection algorithm, lookback, tie-break, exact index | LOW unless a new source segment explicitly names selection rule |
| F09 Entry Geometry | PARTIAL / UNRESOLVED | Pending Limit concept; Entry and SL are separate; HL/LH/deep-leg examples | Exact Entry price field, candle/index anchor, update precedence, deterministic placement | MEDIUM only if an unreviewed explicit entry statement/frame exists |
| F10 Stop / Structural Invalidation | PARTIAL / UNRESOLVED | Invalidation concept; Entry ≠ SL; SL visually behind/below source structure in BUY examples | Exact wick/body/High/Low anchor, spread/buffer, event semantics, bearish field | LOW; primary audit found no Shadow/Spread rule |
| F11 Pending Lifecycle | PARTIAL / UNRESOLVED | Buy Limit exists; Delete exists; possible replacement after changed stop distance | Delete predicate, timeout, replacement condition/price, fill semantics, SELL lifecycle | LOW unless new explicit lifecycle wording is found |
| F12 Trigger / Activation | PARTIAL / UNRESOLVED | 1/2/3-candle presentation family; correction/reach concept; BO/FT context | Exact candle roles/indexing, trigger event, activation event, fill semantics, precedence | MEDIUM only for genuinely unsearched explicit trigger statements |
| F13 2X Target Binding | PARTIAL / UNRESOLVED | Distinct optional 2X position; half-target wording exists as paraphrase | Exact price anchor and binding to TP1/TP2/AB=CD-D/Entry-SL; sizing/fill/TP lifecycle | LOW; primary-only audit found no coordinate binding |
| P-Gap | PARTIAL / UNRESOLVED | P-Gap is a source concept associated with valid breakout; distinct from generic gap | Exact OHLC endpoints, candle indexing, bullish/bearish construction, threshold/boundary | LOW; primary-only audit did not provide executable formula |

## Classification of Remaining Unknowns

### A. Potentially resolvable from Primary Video

These remain worth reopening only if a genuinely new primary-source segment/frame is identified:

1. F09 exact Entry anchor.
2. F12 exact trigger wording/role if an unreviewed explicit statement exists.
3. Any explicit bearish Pending/Trigger statement not covered by the current search.
4. Any explicit source statement binding 2X to a named target/price level.

A new audit must cite timestamp + frame and must change the evidence state, not merely reinterpret existing visuals.

### B. Explicitly source-unresolved after current forensic coverage

These should remain unresolved rather than being inferred:

- F08 universal swing-selection algorithm.
- F10 exact SL OHLC field.
- F10 spread/buffer semantics.
- F10 touch/close/penetration semantics.
- F11 delete predicate.
- F11 numeric timeout.
- F11 replacement threshold and precedence.
- F11 fill semantics.
- F12 candle indexing.
- F12 exact trigger event.
- F12 activation event.
- F12 trigger/fill/activation relationship.
- F12 1/2/3 precedence.
- F13 exact 2X price coordinate/binding.
- P-Gap executable formula/indexing/threshold/mirror.

## Evidence Boundary

The following are **not** canonical substitutes for missing Primary-Source geometry:

- author implementation code;
- external gap video formulas;
- webpage descriptions;
- backtest performance;
- current research detectors;
- assumed bullish/bearish symmetry;
- conventional 3-candle imbalance definitions;
- fixed-risk-distance substitutions;
- inferred touch=fill semantics.

## Promotion Gate

A feature may become canonical only when its executable rule is supported by auditable source evidence sufficient to specify the required inputs, boundaries, event semantics, and direction where applicable.

Current state:

**Frozen Geometry = BLOCKED**

No production BUY/SELL logic may be promoted from this matrix.

## Recommended Next Research Action

Do not repeat F10/F11/F12 using the same evidence.

If continuing source work, perform one final **Primary-Source Evidence Gap Sweep** across the full video for only the unresolved candidates above. For every candidate, return one of:

- SOURCE-CONFIRMED EXECUTABLE
- PARTIAL / SOURCE-DISCRIMINATED
- PARTIAL / UNRESOLVED
- NOT FOUND

If no new executable evidence is found, freeze the blocker boundary and move to synthetic-fixture design for unresolved states without pretending those states are canonical.

## Audit Lineage

- F10 Primary Source Stop Anchor Forensic Audit — 2026-09-21
- F11 Primary Source Pending Order Lifecycle Forensic Audit — 2026-09-21
- F12 Primary Source Trigger / Activation / 1–2–3 Candle Family Forensic Audit — 2026-09-21
- Batch45 P-Gap Evidence Closure — 2026-09-21
- Batch46 F08/F10/F11/F12 source-closure boundary — 2026-09-21
