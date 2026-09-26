# SP2L Source Inventory — 2026-09-26

## Purpose

Repository-side inventory before the next source-resolution pass. This checkpoint is documentation-only and does not promote any executable geometry.

## Branch audited

- Branch: `research/sp2l-f13-forensic-repro-2026-09-26`
- HEAD: `00b7f7fb01e1439c8b4baac727f5d3d6f508ea44`
- Scope: repository tree and archived source-resolution records.

## Source evidence found

The repository already contains substantial source-resolution work, including:

- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `docs/research/SP2L_BATCH26_PGAP_SOURCE_RESOLUTION_2026-09-16.md`
- `docs/research/SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`
- `docs/research/SP2L_BATCH36_PGAP_FORENSIC_SOURCE_RESOLUTION_2026-09-17.md`
- `docs/research/SP2L_PGAP_FINAL_SOURCE_BOUNDARY_AUDIT_2026-09-19.md`
- `docs/research/SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md`
- `docs/research/SP2L_F10_INVALIDATION_SL_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- `docs/research/SP2L_F10_SL_CASE_STUDY_2026-09-21.md`
- `docs/research/SP2L_F14_ABCD_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- `docs/research/SP2L_SOURCE_RESOLUTION_CLOSURE_REPORT_2026-09-20.md`
- `research/fixtures/sp2l_source_discrimination_entry_sl_2x_trigger_abcd_v1.ts`

The repository therefore does **not** have a missing source-inventory problem. It has a remaining **primary-source discrimination problem**.

## What the archive resolves

Source-confirmed at concept/relationship level:

- SP2L = Spike → 2 Leg.
- P-Gap is pressure gap and is distinct from E-Gap/common gap.
- P-Gap participates in valid-breakout/spike qualification.
- Correction and second-leg concepts are source-confirmed.
- Bullish/bearish trigger references are source-described.
- SL is behind the candle from which the spike originated.
- AB=CD / Leg2 approximately equal to Leg1 is source-confirmed as a concept.
- 2X is a later/optional second position; archived author-associated evidence also records a 50%-of-entry-to-SL relation, but complete lifecycle semantics remain unresolved.

## What remains executable-geometry unresolved

- P-Gap exact candle indexing.
- P-Gap exact OHLC boundary fields.
- P-Gap bearish mirror.
- P-Gap zero/minimum threshold or tolerance.
- Exact relation of P-Gap to qualifying spike candle(s).
- Exact SL price field and spread/buffer treatment.
- Trigger precedence and activation event.
- Pending-order deletion/refresh predicate.
- Exact AB=CD A/B/C/D anchors and tolerance.
- Complete 2X anchor, sizing, and lifecycle.
- Bearish source geometry where not explicitly demonstrated.

## Important evidence conflict to preserve

The current primary-video visual audit reports an approximately half-target-distance 2X concept, while the archived author-associated page audit records a 50%-of-entry-to-SL relation. These are not to be silently reconciled. Until direct primary evidence uniquely connects them, both remain evidence records with unresolved executable semantics.

Likewise, the legacy author-attributed generic-gap construction involving the high of two candles before and the low of the current candle remains a candidate only. It must not be promoted to the SP2L P-Gap formula.

## Next source-resolution action

Use the two local source videos for a targeted visual re-audit of the highest-value unresolved fields:

1. Primary SP2L video:
   - P-Gap examples around 31:00–36:45.
   - correction/entry/SL around 38:00–41:30.
   - 2X around 22:00–22:50 and 38:00–42:00.
   - AB=CD / leg endpoints around 36:00–37:15 and later worked examples.
   - bearish examples around 1:02:40–1:04:30.

2. Gap course video:
   - pressure-gap examples around 22:00–25:00.
   - generic gap construction around 17:00–20:00.
   - any frame that explicitly labels candle endpoints/indexing or a bearish mirror.

The required output is a frame-level evidence table, not a formula guess.

## Gate impact

- Source Resolution: PARTIAL.
- Frozen Geometry: BLOCKED.
- No detector change.
- No backtest/optimization.
- No canonical BUY/SELL rule.
