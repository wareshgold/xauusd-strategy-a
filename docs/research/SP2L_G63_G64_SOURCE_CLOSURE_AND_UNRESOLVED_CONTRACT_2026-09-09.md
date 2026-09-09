# SP2L G63/G64 — Source Closure + Unresolved Geometry Contract — 2026-09-09

## Purpose
G63 closes the current source-resolution search for the executable geometry that remains absent or non-unique in the authoritative material. G64 converts that result into an explicit engine contract so unresolved geometry cannot silently acquire defaults.

## Source-closure decision
The indexed source evidence is sufficient to freeze the semantic model but is not sufficient to uniquely freeze all executable OHLC geometry for B1-B6.

### B1 — P-Gap
Source-supported: P-Gap is a named valid-breakout condition associated with breakout/follow-through and distinct from E-Gap/Common-Gap. Multiple constructions are demonstrated.
Closure: no unique source-confirmed participating-candle boundary or formula. **UNRESOLVED.**

### B2 — Entry
Source-supported: pending Buy/Sell Limit during correction at a relevant structural Low/High; demonstrated levels can update as structure evolves.
Closure: no universal source-confirmed wick/body/OHLC anchor. **UNRESOLVED.**

### B3 — Stop / invalidation
Source-supported: structural invalidation and a stop distinct from Entry.
Closure: no unique source-confirmed exact OHLC boundary. **UNRESOLVED.**

### B4 — Trigger
Source-supported: one-, two-, and three-candle forms plus Key-Bar examples; trigger is part of the setup flow.
Closure: exact acceptance condition, indexing, timing, and precedence are not uniquely specified. Market reclaim is not equivalent. **UNRESOLVED.**

### B5 — AB=CD
Source-supported: explicit AB=CD and Leg1/Leg2 magnitude relationship.
Closure: A/B/C/D endpoint model and tolerance are not uniquely specified. **UNRESOLVED.**

### B6 — Leg2 / TP / 2X
Source-supported: second-leg continuation, TP1 preference, larger TP2 research concept, and 2X concept.
Closure: executable projection/endpoints and exact 2X mechanics are not uniquely specified. **UNRESOLVED.**

## G64 unresolved geometry contract
Any production-capable Strategy A component must fail closed when a required geometry field is unresolved. It must not substitute a wick, body, pivot, Fibonacci, ATR, fixed buffer, generic FVG, market reclaim, or arbitrary tolerance.

Required state vocabulary:
- RESOLVED_SOURCE_GEOMETRY
- CANDIDATE_RESEARCH_GEOMETRY
- UNRESOLVED_SOURCE_GEOMETRY
- BLOCKED_PRODUCTION

Candidate research implementations must remain namespaced and must never be imported by production signal generation.

## Gate result
SOURCE RESOLUTION: CLOSED AS PARTIAL — semantic closure achieved; executable geometry remains explicitly unresolved.
SYNTHETIC FIXTURES: PASS/ONGOING.
FROZEN GEOMETRY: BLOCKED.
DEV/VAL/FRESH_HOLDOUT Strategy A validation: LOCKED.
PRODUCTION: LOCKED.

## Next admissible work
The project may proceed with deterministic infrastructure, data, synthetic execution, reporting, and isolated candidate research. It may not claim a validated Strategy A edge or emit production BUY/SELL until the frozen geometry gate is independently satisfied.
