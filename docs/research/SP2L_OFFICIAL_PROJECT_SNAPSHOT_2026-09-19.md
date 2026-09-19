# SP2L Official Project Snapshot — 2026-09-19

## Purpose
Permanent resume point for the SP2L / XAUUSD Strategy A project. Source meaning outranks backtest performance; unresolved geometry remains unresolved.

## Current branch
- Branch: `research/sp2l-live-mt5-telegram-2026-09-19`

## Current gate state
- Frozen Geometry: **BLOCKED**
- Parameter robustness evidence: **POSITIVE**
- Parameter Stability Gate: **INCONCLUSIVE — NO PASS / NO FAIL**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Production/live trading authorization: **BLOCKED**
- Live Trading: **DISABLED**
- Nexora runtime dry-run verification: **PASS**
- Canonicalization firewall: **NO LEAKAGE IDENTIFIED**

Workflow:
`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

## Latest source-resolution status
Executable source-confirmation fields remain **0/7**:
- Entry: PARTIAL
- Invalidation/SL: PARTIAL
- Limit refresh: PARTIAL
- Trigger: PARTIAL
- 2X: PARTIAL
- AB=CD: PARTIAL
- P-Gap: UNRESOLVED

Recent completed audits:
- F14 AB=CD anchors/tolerance: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F14_ABCD_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- F11 pending-order lifecycle: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F11_PENDING_ORDER_LIFECYCLE_RESOLUTION_AUDIT_2026-09-19.md`
- F10 invalidation/SL anchor: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F10_INVALIDATION_SL_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- F12 trigger acceptance/precedence: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F12_TRIGGER_ACCEPTANCE_PRECEDENCE_RESOLUTION_AUDIT_2026-09-19.md`
- P-Gap final boundary: **UNRESOLVED**
  - `docs/research/SP2L_PGAP_FINAL_SOURCE_BOUNDARY_AUDIT_2026-09-19.md`
- F08 relevant swing selection: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F08_RELEVANT_SWING_SOURCE_RESOLUTION_AUDIT_2026-09-19.md`
- F13 2X lifecycle: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F13_2X_LIFECYCLE_SOURCE_RESOLUTION_AUDIT_2026-09-19.md`
  - Source-confirmed concept: secondary entry at 50% of entry-to-SL distance; full lifecycle, sizing, activation, fill, and reference-state semantics remain unresolved.
- F16 Round Level: **PARTIAL / UNRESOLVED**
  - `docs/research/SP2L_F16_ROUND_LEVEL_SOURCE_RESOLUTION_AUDIT_2026-09-19.md`
  - Source-confirmed concept and examples (250/500/1000 points); universal interval and exact algorithm/use remain unresolved.

## Non-negotiable source boundaries
Do not invent:
- P-Gap indexing, boundary semantics, threshold, or bearish mirror.
- AB=CD A/B/C/D anchors, pivot algorithm, tolerance, or `fill=C`.
- Exact SL wick/body/OHLC anchor, buffer, or breach/fill semantics.
- Pending-order deletion/refresh predicate.
- Trigger precedence or touch/wick/close activation semantics.
- 2X sizing, mandatory/optional policy, lifecycle, or fill semantics.
- Round Level interval, rounding formula, or role in setup generation.
- Leg1=Leg2 equality as a strict executable rule.

No unresolved source ambiguity may be resolved by backtest performance.

## Parameter robustness / stability
81-combination bounded matrix remains research evidence only:
- Baseline: 158 signals; 103W / 51L / 4 ambiguous; 66.883% decisive WR; +52R; PF 2.02.
- Matrix: 81/81 positive Total R; 80/81 above 60% decisive WR; mean 65.733%; median 65.972%; min 59.794%; max 70.968%.
- Parameter Stability: **INCONCLUSIVE — NO PASS / NO FAIL**; temporal consistency remains mixed.
No parameter promotion.

## Fresh Holdout
Frozen boundary: **2026-09-19 00:00 UTC**.
Latest status: `HOLDOUT_DATA_UNAVAILABLE`; 0 eligible post-boundary XAUUSD.ecn M1 bars. Do not substitute pre-boundary data.

## Nexora infrastructure
Existing guarded MT5/Telegram runtime remains in place and is not rebuilt:
- `LIVE_TRADING_ENABLE=false`
- gateway does not calculate Strategy A geometry
- explicit external APPROVED signal required
- duplicate/open-position guards active
- dry-run checkpoint PASS
- no real order / no production Strategy A signal

Future Windows VIP client remains roadmap-only and non-operational.

## Next research priority
Continue **source-resolution**, not backtesting:
1. Seek source evidence that can close the remaining executable blockers, especially P-Gap exact boundary/indexing, F10/F8 structural anchor, F11 lifecycle, F12 activation, F14 anchors/tolerance.
2. If no new source evidence exists, preserve blockers and improve audit/fixture coverage without promoting geometry.
3. Fresh Holdout may run only when eligible post-boundary data exists and only against the frozen configuration.
4. Production remains OFF until Frozen Geometry passes.

## Official snapshot history
- `d233ab8e4e89ff7d49d4c305e16433dbaa4d8903` — prior official project snapshot.
- This snapshot extends the resume point with the completed F13 and F16 source-resolution audits.
