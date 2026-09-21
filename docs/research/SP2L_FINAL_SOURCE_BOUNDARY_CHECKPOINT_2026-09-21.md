# SP2L Final Source Boundary Checkpoint — 2026-09-21

## Purpose
Freeze the current evidence boundary after Batch45/Batch46 and the final primary-source gap sweep. This is a research boundary record, not canonical strategy geometry.

## Evidence result
The 2026-09-21 final primary-source sweep found no new executable primary evidence sufficient to uniquely determine any remaining blocker.

### Source-confirmed concepts retained
- SP2L = Spike → 2 Leg.
- P-Gap is a pressure-gap concept associated with valid breakout and distinct from E-Gap/Common Gap.
- Correction / higher-low / lower-high structures are source-supported.
- Bullish trigger concept references the previous candle low; bearish trigger concept references the previous candle high.
- Pending Buy Limit exists in the source and can be deleted/replaced as structure/stop distance changes.
- F10 stop is structurally behind the candle from which the spike originated.
- AB=CD / Leg2 approximately equal to Leg1 is source-supported.
- 2X is a distinct optional secondary-position concept; the 50%-of-entry-to-stop relation is source-supported at concept level.

## Executable blockers remain unresolved
| Feature | Status | Blocking field |
|---|---|---|
| P-Gap | UNRESOLVED | OHLC endpoints, indexing, threshold/boundary, bearish mirror |
| F08 | UNRESOLVED | swing algorithm, lookback, indexing, tie-break |
| F09 | UNRESOLVED | exact Entry field/index/update precedence |
| F10 | UNRESOLVED | exact SL OHLC anchor, spread/buffer, invalidation event |
| F11 | UNRESOLVED | delete predicate, timeout, replacement, fill semantics |
| F12 | UNRESOLVED | trigger index, activation event, precedence, fill semantics |
| F13 | UNRESOLVED | complete 2X coordinate/lifecycle/sizing/exit semantics |
| F14 | UNRESOLVED | A/B/C/D endpoints, price field, D semantics, tolerance |
| F15 | UNRESOLVED | complete bearish executable geometry |

## Canonicalization firewall
No unresolved item is promoted from author implementation, backtest performance, synthetic symmetry, conventional definitions, secondary descriptions, or current forward-test observations.

## Gate
- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: BLOCKED
- Production: BLOCKED / DISABLED

## Next permitted stage
Build/complete synthetic discrimination fixtures for every unresolved executable state. Fixtures must encode competing hypotheses and expected status as unresolved; they must never select a canonical winner.

NO_NEW_EXECUTABLE_PRIMARY_SOURCE_EVIDENCE
PRIMARY_SOURCE_BOUNDARY_FINAL_UNTIL_NEW_SOURCE_MATERIAL
