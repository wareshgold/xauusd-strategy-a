# SP2L Source Resolution Status — F09–F14 — 2026-09-16

## Purpose

Record the current evidence boundary after the source-discrimination fixture pass. This matrix is an audit artifact, not a geometry specification.

| ID | Topic | Source-confirmed statement | Missing canonical detail | Status | Next evidence required |
|---|---|---|---|---|---|
| F09 | Entry anchor | Limit entry can be placed in the initial structure during correction | Exact price anchor and whether it is distinct from Leg-2 start | UNRESOLVED | Locate a source example where entry and subsequent Leg-2 origin are both observable |
| F10 | SL anchor | Setup invalidation is tied to the relevant structural level | Exact wick/body/swing anchor and any buffer | UNRESOLVED | Locate explicit stop/invalidation example with price-level semantics |
| F11 | Limit refresh | Source permits order deletion/replacement when stop distance changes | Mandatory refresh condition or threshold | UNRESOLVED | Locate transcript wording that states when replacement is required rather than merely permitted |
| F12 | Trigger | One-, two-, and three-candle structures plus Bar/Key-Bar confirmation are source-described | Canonical acceptance rule and precedence | PARTIAL | Find explicit trigger-selection/confirmation example tied to an executed setup |
| F13 | 2X | Optional second position exists and is associated with approximately half-target positioning / larger-R outcome | Exact entry anchor, sizing, target and stop semantics | UNRESOLVED | Locate a worked 2X example with both positions and numeric levels |
| F14 | AB=CD | SP2L maps Spike → Correction → Leg 2 ≈ Leg 1 | Exact A/B/C/D anchors and equality tolerance | UNRESOLVED | Locate a worked AB=CD example where all four anchors and measurement convention are observable |

## Evidence policy

1. A source statement can promote a field only when it uniquely determines the executable meaning.
2. A source statement that merely permits multiple interpretations cannot freeze geometry.
3. Fixture discrimination does not substitute for source evidence.
4. Backtest performance cannot resolve a source-definition ambiguity.
5. If the required evidence is absent, preserve `UNRESOLVED`.

## Gate impact

The fixture infrastructure is now in place for F09–F14. Source Resolution remains Partial; Frozen Geometry remains BLOCKED. No production signal generation is authorized.
