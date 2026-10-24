# SP2L F10 / F12 / F14 — Synthetic Discrimination Matrix — 2026-09-19

## Purpose
Convert remaining source ambiguities into explicit, testable alternatives without selecting a canonical rule.

This is a discrimination-fixture specification, not a strategy definition. It may verify that competing interpretations remain distinct and that the harness fails closed. It may not select an interpretation from backtest performance.

## F10 — Stop / invalidation alternatives
Source-confirmed boundary: SL is associated with / behind the spike-origin candle; Entry and SL are distinct; exact price field and breach semantics remain unresolved.
Candidates: wick extreme; body boundary; structural-origin level; buffered boundary; invalidation on touch; penetration; close.
Fixture: construct candles where wick, body, and structural-origin candidates differ, and where touch/penetration/close produce different outcomes. Assert each interpretation separately and never promote one automatically.

## F12 — Trigger alternatives
Source-confirmed boundary: bullish corrective trigger references previous-candle low; bearish trigger references previous-candle high; source describes 1/2/3-candle structures and Bar/Key-Bar variants; entry follows the second-leg trigger.
Candidates: touch, wick penetration, body penetration, close; 1/2/3-candle constructions; Bar; Key-Bar; competing precedence.
Fixture: synthetic candles must separate touch/wick/body/close timing and include multiple valid-looking variants. Assert each classifier separately and never introduce precedence by convenience.

## F14 — AB=CD alternatives
Source-confirmed boundary: SP2L is explicitly linked to AB=CD and Leg2 is expected to match Leg1 in magnitude. Exact A/B/C/D anchors and tolerance remain unresolved.
Candidates: structural swings; wick extremes; candle bodies; observed D; projected D; Entry=C; Entry distinct from C.
Entry=C is included only as a negative/disallowed candidate because the source has not established that identity.
Fixture: build nested-leg examples where anchor conventions differ; include cases where target coincidence occurs despite different anchors; include deviations that would require a tolerance without choosing the tolerance.

## Cross-field interaction
F12 trigger can change effective entry state. F10 SL interpretation changes Entry-to-SL distance. F13 2X therefore changes under unresolved F10/F12 interpretations. F14 projected D changes if A/B/C changes. P-Gap remains an external unresolved prerequisite and must not be synthesized from generic FVG rules.

## Acceptance rule
Pass when competing interpretations are explicit, outputs can differ on adversarial synthetic cases, accidental convergence is detected, no candidate is promoted, and the canonical no-go guard remains blocking while provenance is not SOURCE_CONFIRMED.

## Current source gate
F10: PARTIAL / UNRESOLVED
F12: PARTIAL / UNRESOLVED
F14: PARTIAL / UNRESOLVED
P-Gap: UNRESOLVED / QUARANTINED
Frozen Geometry: BLOCKED
Production: BLOCKED
Live Trading: DISABLED

## Evidence required for closure
Only new direct source evidence can close these blockers: explicit SL price-field/invalidation statement; explicit trigger classifier/precedence statement; worked AB=CD example with A/B/C/D labels or unambiguous calculation.
Backtest performance and conventional technical-analysis formulas are not admissible evidence for canonicalization.