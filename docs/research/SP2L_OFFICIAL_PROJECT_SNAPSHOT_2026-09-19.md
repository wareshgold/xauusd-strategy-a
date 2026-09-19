# SP2L Official Project Snapshot — 2026-09-19

## Purpose
Permanent resume point for SP2L / XAUUSD Strategy A. Source meaning outranks backtest performance; unresolved geometry remains unresolved.

## Current branch
- `research/sp2l-live-mt5-telegram-2026-09-19`

## Gate state
- Frozen Geometry: **BLOCKED**
- Parameter robustness: **POSITIVE**
- Parameter Stability: **INCONCLUSIVE — NO PASS / NO FAIL**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Production/live authorization: **BLOCKED**
- Live Trading: **DISABLED**
- Nexora dry-run: **PASS**
- Canonicalization firewall: **NO LEAKAGE IDENTIFIED**

## Source-resolution status
Executable source-confirmation fields remain **0/7**:
- Entry: PARTIAL
- Invalidation/SL: PARTIAL
- Limit refresh: PARTIAL
- Trigger: PARTIAL
- 2X: PARTIAL
- AB=CD: PARTIAL
- P-Gap: **UNRESOLVED**

Completed audits:
- F14 AB=CD: PARTIAL / UNRESOLVED
- F11 pending lifecycle: PARTIAL / UNRESOLVED
- F10 SL/invalidation: PARTIAL / UNRESOLVED
- F12 trigger: PARTIAL / UNRESOLVED
- F08 swing selection: PARTIAL / UNRESOLVED
- F13 2X lifecycle: PARTIAL / UNRESOLVED
- F16 Round Level: PARTIAL / UNRESOLVED

## P-Gap closure attempt
New audit:
`docs/research/SP2L_PGAP_SOURCE_EVIDENCE_CLOSURE_ATTEMPT_2026-09-19.md`

Result: **P-Gap remains UNRESOLVED for canonical executable geometry.**

The current author-hosted SP2L page confirms that P-Gap is a defining feature of a valid spike, but does not expose exact OHLC/indexing/threshold/mirror semantics. The public author course outline also confirms dedicated gap-training material exists, but its public outline does not expose the SP2L formula.

The archived legacy author-attributed bullish candidate remains non-canonical. No normalization, bearish mirror, threshold, wick/body rule, or indexing formula was promoted.

Further P-Gap closure now requires explicit source evidence such as a worked calculation, unambiguous labeled source frame, or direct author documentation containing the missing fields.

## Non-negotiable boundaries
Do not invent:
- P-Gap indexing/boundary/threshold/mirror.
- AB=CD A/B/C/D anchors/tolerance or `fill=C`.
- Exact SL price/buffer/breach semantics.
- Pending-order deletion/refresh predicate.
- Trigger precedence/fill semantics.
- 2X sizing/lifecycle semantics.
- Round Level interval/formula/use.
- Strict Leg1=Leg2 equality.

No backtest may resolve source ambiguity.

## Research evidence
81-combination robustness matrix remains research-only:
- Baseline: 158 signals; 103W / 51L / 4 ambiguous; 66.883% decisive WR; +52R; PF 2.02.
- Matrix: 81/81 positive Total R; 80/81 above 60% decisive WR; mean 65.733%; median 65.972%; min 59.794%; max 70.968%.
- Stability: INCONCLUSIVE; temporal consistency mixed.
No parameter promotion.

## Fresh Holdout
Frozen boundary: **2026-09-19 00:00 UTC**.
Latest: `HOLDOUT_DATA_UNAVAILABLE`; 0 eligible post-boundary XAUUSD.ecn M1 bars. No pre-boundary substitution.

## Nexora
Existing guarded infrastructure remains unchanged:
- `LIVE_TRADING_ENABLE=false`
- gateway does not calculate Strategy A geometry
- explicit APPROVED external signal required
- guards and dry-run verification remain active
- no real order / no production Strategy A signal
- future VIP Windows client remains roadmap-only.

## Next action
Stop repeatedly normalizing P-Gap from generic gap theory. Continue source-resolution on the remaining closable blockers (F8/F10/F11/F12/F14/F13/F16), while P-Gap stays quarantined as unresolved. No backtest or live activation until Frozen Geometry passes.

## Snapshot history
- `d233ab8e4e89ff7d49d4c305e16433dbaa4d8903` — prior official snapshot.
- `4b1546d12b5dd6364fc24710cc7f72212cae42f5` — prior snapshot including F13/F16.
- This update registers the P-Gap closure boundary and the resulting research pivot.