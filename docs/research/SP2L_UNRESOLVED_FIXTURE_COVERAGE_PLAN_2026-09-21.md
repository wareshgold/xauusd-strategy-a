# SP2L Unresolved Fixture Coverage Plan — 2026-09-21

## Objective
Convert the frozen source boundary into auditable synthetic fixtures so unresolved interpretations can be tested for determinism, dependency, contamination, and coverage without selecting a canonical rule.

## Required discrimination families
- P-Gap: adjacent non-overlap/equality/overlap; indexing; OHLC endpoints; threshold; pressure/compression boundary; early-vs-repeated-extension context; bullish/bearish separation.
- F08: structural turn vs fixed pivot; wick vs body; multiple-candidate precedence; evolving HL/LH; asymmetric windows.
- F09: price-field alternatives; candle/index alternatives; pending-limit vs later-reclaim; update/replacement precedence.
- F10: spike-origin mapping; wick/body/structural candidates; spread/buffer; touch/breach/close invalidation.
- F11: pending-valid; correction-change; delete; replace; expire; fill; update-vs-invalidation precedence.
- F12: 1/2/3-candle families; previous-low/high references; touch/breach/close; trigger/activation/fill; variant precedence.
- F13: 50%-relation reference states; filled/unfilled initial entry; refreshed Entry/SL; sizing; optional-vs-mandatory; TP1/TP2 interaction.
- F14: structural-swing/spike-extreme/candle-OHLC anchors; A/B/C/D alternatives; observed/projected D; equality/near/material inequality; tolerance unresolved.
- F15: bearish evidence kept separate from synthetic mirror; each bearish executable field remains independently unresolved unless directly sourced.

## Acceptance invariants
1. Every unresolved fixture is canonicalEligible=false.
2. No outcome is selected from backtest performance.
3. Ambiguous source geometry remains unresolved.
4. Synthetic bullish-to-bearish symmetry is never primary evidence.
5. Touch, activation, and fill remain distinct states.
6. Provenance and source-scope labels are mandatory.
7. Frozen Geometry cannot pass while required executable fields remain unresolved.

## Exit condition
Coverage is complete when each unresolved blocker has counterexample sets distinguishing its major competing interpretations and the harness records unresolved status without silently choosing one.

## Current gate
Frozen Geometry remains BLOCKED.
