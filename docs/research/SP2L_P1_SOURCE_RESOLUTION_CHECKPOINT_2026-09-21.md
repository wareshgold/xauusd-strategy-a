# SP2L P1 Source Resolution Checkpoint — 2026-09-21

## Scope
This checkpoint consolidates the P1 source-boundary pass for F09, F11, F12, F13, and F14.

## F09 — Entry
Source-supported: Pending Limit exists; corrective development is represented by a 1/2/3-candle family.
Unresolved: exact entry price field/index; Pending Limit versus later reclaim precedence; replacement/update precedence; activation/fill semantics.
Current close-reclaim implementation remains non-canonical.

## F11 — Pending lifecycle
Source-supported: Pending setup can be refreshed/updated qualitatively.
Unresolved: invalidation event; replacement threshold/mechanics; timeout/expiry; delete versus replace precedence; fill semantics.

## F12 — Trigger
Source-supported: 1/2/3-candle corrective family; directional previous-candle level; bearish High and bullish Low references.
Unresolved: touch/breach/close; trigger versus fill; activation precedence; exact candle/index selection.

## F13 — 2X
Source-supported: optional/additional second-position concept; Entry-to-SL midpoint relationship at concept level.
Unresolved: exact coordinate lifecycle after refresh; sizing/aggregation; optional versus mandatory execution state; TP/exit and replacement lifecycle.
No risk or sizing rule was selected from performance.

## F14 — AB=CD
Source-supported: Leg2 approximately/equally relates to Leg1.
Unresolved: A/B/C/D anchors; wick/body versus structural endpoints; observed/projected D; numerical tolerance; hard eligibility versus qualitative relationship.

## Consolidated decision
P1 source resolution is PARTIAL.
No unresolved executable rule was promoted.

### Gates
- Source Resolution: PARTIAL
- Synthetic Fixtures: PASS
- Frozen Geometry: BLOCKED
- DEV: LOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: BLOCKED
- Production: DISABLED

## Canonicalization firewall
Backtest performance, optimization, synthetic symmetry, implementation convenience, and forward observations remain prohibited as mechanisms for resolving these source blockers.

## Next phase
P1 evidence boundary is documented. Next permissible work: primary-source evidence discovery if additional archived evidence exists; otherwise evidence-exhaustion checkpoint. Only after source resolution can Frozen Geometry be reconsidered.

This checkpoint is not a strategy specification.