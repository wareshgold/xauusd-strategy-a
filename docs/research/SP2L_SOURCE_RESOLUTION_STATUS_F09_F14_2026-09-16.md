# SP2L Source Resolution Status — F09–F14 — 2026-09-16

## Purpose

Record the current evidence boundary after transcript recovery and transcript-to-visual reconciliation. This matrix is an audit artifact, not a frozen geometry specification.

| ID | Topic | Source-confirmed / source-supported meaning | Missing canonical detail | Status | Next evidence required |
|---|---|---|---|---|---|
| F09 | Entry anchor | Pending Limit belongs to the correction sequence; the demonstrated bullish visual sequence supports movement toward the currently relevant completed higher-low | Universal exact entry anchor; whether the same anchor applies across all Spike variants; explicit entry vs Leg-2-origin semantics in a worked source example | **PARTIAL** | Source example jointly exposing entry anchor and subsequent Leg-2 origin |
| F10 | SL anchor | Structural invalidation is distinct from entry and is deeper than the demonstrated pending entry level | Exact OHLC/wick/body anchor and any buffer/spread treatment | **PARTIAL** | Explicit worked stop/invalidation example with price-level semantics |
| F11 | Limit refresh | Source supports delete/re-place when a new candle materially changes the stop distance; small changes may retain/move the existing order | Deterministic mandatory replacement threshold/condition | **PARTIAL** | Explicit source wording or worked example that uniquely defines when refresh is mandatory |
| F12 | Trigger | One-, two-, and three-candle structures plus Bar/Key-Bar variants are source-described | Deterministic acceptance algorithm, classifier, and precedence | **PARTIAL** | Executed source setup tying a trigger form to acceptance/precedence |
| F13 | 2X | Optional second position; source associates it with approximately half-target positioning and a larger-R later entry | Exact price anchor, sizing, stop, target and fill semantics | **PARTIAL** | Worked source 2X example with exact levels and execution/sizing semantics |
| F14 | AB=CD | SPIKE-2LEG is explicitly linked to AB=CD; Leg 2 is expected to match Leg 1 in magnitude | Exact A/B/C/D endpoints, OHLC convention, and tolerance | **PARTIAL** | Worked source AB=CD example exposing all four anchors and measurement convention |

## Cross-cutting P-Gap blocker

P-Gap is source-distinguished from E-Gap/Common-Gap and tied to breakout construction, including multiple source-described ordering variants. Exact deterministic OHLC formula remains **UNRESOLVED**.

## Evidence policy

1. Source meaning outranks backtest performance.
2. A source statement can freeze a field only when it uniquely determines executable meaning.
3. A visual example can narrow a demonstrated variant but cannot silently generalize it to all setups.
4. Fixture discrimination does not substitute for source evidence.
5. Backtest performance cannot resolve a source-definition ambiguity.
6. If required evidence is absent, preserve the unresolved canonical action.

## Gate impact

The fixture infrastructure is advanced and the evidence boundary is materially strengthened. Source Resolution remains **PARTIAL**; Frozen Geometry remains **BLOCKED**. Untouched Validation, Robustness/Stability, Fresh Holdout, and Production remain locked/off.

## Canonical action

For every F09–F14 field above, canonical executable geometry remains **UNRESOLVED** until the listed evidence uniquely determines the rule.
