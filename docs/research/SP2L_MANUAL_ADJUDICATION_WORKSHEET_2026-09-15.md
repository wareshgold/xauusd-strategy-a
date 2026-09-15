# SP2L Manual Adjudication Worksheet — 2026-09-15

## Status

`HUMAN_REVIEW_REQUIRED`

This worksheet operationalizes the existing evidence package for human review. It does **not** adjudicate candidates, freeze geometry, or authorize execution.

## Rule

For each candidate, record exactly one outcome:

- `SOURCE_DISCRIMINATED` only when the cited Tier-1/Tier-2 source uniquely and reproducibly determines the executable dimension(s), with no invented formula, threshold, buffer, indexing, fill, or symmetry.
- `REMAINS_BLOCKED` otherwise, preserving the unresolved hypotheses.

Backtest performance, optimization, generic technical-analysis conventions, and implementation convenience are not admissible adjudicators.

## Candidate review matrix

| Candidate | Dimension(s) | Source evidence | Human discriminator question | Default pending state |
|---|---|---|---|---|
| C01-PGAP-003 | `p_gap` | 00:36:30 / frame 65700: `Valid BO = P-Gap` | Does the source uniquely identify the candle/price boundary, rather than only P-Gap's semantic role? | `REMAINS_BLOCKED` until proven otherwise |
| C02-ENTRY-SL-003 | `entry_anchor`, `structural_invalidation` | 00:39:40–00:40:20 / frames 71400–72600: Buy Limit, lower SL, reference level, Delete | Are exact entry and invalidation candle/price boundaries explicitly source-identifiable? | `REMAINS_BLOCKED` until proven otherwise |
| C03-ABCD-MAG-003 | `abcd_anchors`, `abcd_tolerance`, `leg2_start` | 00:36:30–00:37:00 / frames 65700–66600: `AB=CD`; candle-level Leg-2 magnitude equality | Are A/B/C/D and Leg-2 start explicitly identified, and is tolerance exact? | `REMAINS_BLOCKED` until proven otherwise |
| C04-TARGETS-003 | `targets_2x` | 00:42:30 / frame 76500 plus 00:58:04–00:59:08: TP1/TP2/2X examples | Does the source provide a reproducible formula/anchor for targets and 2X? | `REMAINS_BLOCKED` until proven otherwise |
| C05-BEARISH-MIRROR-003 | `bearish_mirror` | 01:02:41–01:04:32: bearish trigger/continuation examples | Which bearish rules are explicit, and which would require inferred bullish symmetry? | `REMAINS_BLOCKED` until proven otherwise |
| C06-PENDING-REFRESH-003 | `pending_refresh` | 00:40:20 / frame 72600: Delete; later Buy Limit lifecycle discussion | Is there an explicit reproducible delete/replace/retain condition? | `REMAINS_BLOCKED` until proven otherwise |
| C07-TRIGGER-FAMILY-003 | `trigger_classifier` | 00:35:10–00:36:31: three spike cases / 1-2-3 candle family | Are cases exhaustive and are exact candle conditions explicitly defined? | `REMAINS_BLOCKED` until proven otherwise |
| C08-CORRECTION-INVALIDATION-003 | `structural_invalidation`, `entry_anchor` | 00:38:38–00:39:48: correction, Buy Limit, return-to-level invalidation | Which exact source-visible candle/price is the invalidation level, and is it the entry anchor? | `REMAINS_BLOCKED` until proven otherwise |

## Human adjudication record

For every candidate, create a `ManualAdjudication` record containing:

1. candidate ID
2. human adjudicator reference
3. outcome
4. whether a source discriminator was confirmed
5. whether reproducibility was confirmed
6. whether invention was required
7. rationale
8. remaining hypotheses when blocked

The repository's adjudication contract rejects a `SOURCE_DISCRIMINATED` result when the discriminator or reproducibility is not confirmed or when invention is required.

## Current gate interpretation

The evidence package is ready for human adjudication, but this worksheet intentionally defaults every candidate to blocked. The source material currently narrows several hypotheses without uniquely resolving the executable geometry.

No candidate in this worksheet is canonical. No geometry dimension is frozen. No BUY/SELL output is authorized.

## Exit criteria

The project may advance a dimension only after a human adjudicator records a valid source-discriminated result. All ten geometry dimensions must reach the repository's required manual-adjudication state before `READY_FOR_FREEZE_REVIEW` can be considered.
