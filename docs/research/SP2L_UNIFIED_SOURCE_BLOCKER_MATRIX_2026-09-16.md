# SP2L Unified Source Blocker Matrix — 2026-09-16

## Purpose

Unify the current source evidence, fixture discrimination status, and implementation boundary before any geometry freeze.

## Matrix

| ID | Topic | Source boundary | Exact canonical geometry | Status |
|---|---|---|---|---|
| C01 | P-Gap | Relevant to valid breakout | OHLC/index/boundary formula | UNRESOLVED |
| C02 | SL | Structural invalidation distinct from risk budget | Exact anchor, wick/body, buffer | UNRESOLVED |
| C03 | AB=CD | Leg-2 magnitude relates to Leg-1 | A/B/C/D anchors + tolerance | UNRESOLVED |
| C04 | TP1/TP2/2X | Source concepts confirmed | Exact target and 2X numeric semantics | UNRESOLVED |
| C05 | M15/MA50 | Context concept exists in working implementation | Canonical filter semantics/parameters | UNRESOLVED |
| C06 | Pending order | Pending Limit and qualitative refresh supported | Exact replacement condition | UNRESOLVED |
| C07 | Trigger | 1/2/3-candle family supported | Exact classifier/acceptance rule | UNRESOLVED |
| C08 | Correction/invalidation | Correction is entry phase; invalidation separate | Exact swing/OHLC and breach semantics | UNRESOLVED |
| F08 | Relevant swing | Visual evidence supports dynamic latest relevant low in demonstrated bullish case | Universal swing algorithm | UNRESOLVED |
| F09 | Entry vs Leg-2 start | Source-supported separation | Exact anchors | SOURCE_DISCRIMINATED boundary only |
| F10 | Risk vs structural stop | Distinct concepts | Exact structural OHLC rule | UNRESOLVED |
| F11 | Pending refresh | Refresh/update permitted qualitatively | Replacement threshold | UNRESOLVED |
| F12 | Trigger family | 1/2/3 candle family | Exact taxonomy | UNRESOLVED |
| F13 | 2X | Second-position concept | Exact formula | UNRESOLVED |
| F14 | AB=CD | Leg2 ≈ Leg1 | A/B/C/D + tolerance | UNRESOLVED |
| F15 | Bearish mirror | Synthetic symmetry only | Source-confirmed bearish geometry | UNRESOLVED |

## Freeze rule

Only source-discriminated semantics may be promoted. Synthetic fixtures establish discrimination capability but cannot decide between source-equivalent interpretations.

## Current conclusion

The project has a coherent source boundary, but not enough evidence for Frozen Geometry. Performance must not resolve these blockers.

## Gate

Source Resolution: `PARTIAL PASS`
Frozen Geometry: `BLOCKED`
Validation: `LOCKED`
Production: `OFF`
