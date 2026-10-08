# SP2L Unresolved Fixture Coverage Plan — 2026-09-21

Objective: convert the frozen source boundary into auditable synthetic discrimination coverage without selecting a canonical rule.

Coverage families:
- P-Gap: non-overlap/equality/overlap, indexing, OHLC endpoints, threshold, pressure/compression boundary, early/repeated-extension context, bullish/bearish separation.
- F08: structural turn/fixed pivot, wick/body, multiple-candidate precedence, evolving HL/LH, asymmetric windows.
- F09: price-field/index alternatives, Pending Limit vs later reclaim, update/replacement precedence.
- F10: spike-origin mapping, wick/body/structural candidates, spread/buffer, touch/breach/close invalidation.
- F11: pending-valid, correction change, delete, replace, expire, fill, update-vs-invalidation precedence.
- F12: 1/2/3-candle families, previous-low/high, touch/breach/close, trigger/activation/fill, variant precedence.
- F13: 50%-relation reference states, filled/unfilled entry, refreshed Entry/SL, sizing, optional/mandatory, TP1/TP2 interaction.
- F14: structural/spike/candle anchors, A/B/C/D alternatives, observed/projected D, equality/near/material inequality, unresolved tolerance.
- F15: independently sourced bearish evidence only; synthetic mirror remains noncanonical.

Mandatory invariants:
1. canonicalEligible=false for unresolved fixtures.
2. Never choose outcomes from backtest performance.
3. Keep ambiguous geometry unresolved.
4. Synthetic bearish symmetry is not primary evidence.
5. Touch, activation, and fill are distinct.
6. Preserve provenance and source scope.
7. Frozen Geometry remains blocked while required executable fields are unresolved.

Exit condition: every unresolved blocker has counterexamples distinguishing its major interpretations, with the harness recording unresolved status rather than silently choosing one.
