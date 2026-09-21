# SP2L F13 2X Source Reconciliation — 2026-09-21

## Scope

Targeted reconciliation of the F13 2X / secondary-entry evidence between the
archived primary training video records and the author-controlled written
source. Source meaning outranks implementation and backtest behavior.

## Sources reviewed

1. Primary training-video evidence:
   - `SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
   - `SP2L_BATCH17_UPLOADED_PRIMARY_VIDEO_EVIDENCE_F13_F14_2026-09-16.md`
   - `SP2L_RAW_VIDEO_FRAME_AUDIT_2026-09-20.md`
2. Author-controlled written source:
   - `SP2L_AUTHOR_SITE_SOURCE_RETRIEVAL_EVIDENCE_2026-09-21.md`
   - `SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`

## Reconciliation findings

### R-01 — 2X exists in the primary video

The primary artifact directly shows a 2X annotation and a dedicated diagram
with Buy, 2X, and SL levels. The archived visual evidence supports the
existence of an intermediate secondary-entry concept.

**Status: SOURCE-CONFIRMED concept.**

### R-02 — Primary-video numeric description differs from author-site wording

The archived transcript records the training video as describing the second
position at approximately **half of the target distance**.

The author-controlled written source describes the secondary entry as **50% of
the distance from Entry to Stop-Loss**.

These are not mathematically interchangeable without an independently
source-confirmed relationship between target distance, Entry, and Stop-Loss.
The video record also does not expose a unique executable price equation.

**Status: SOURCE CONFLICT / UNRESOLVED EXECUTABLE ANCHOR.**

### R-03 — Existing F13 fixture scope must remain evidence-layered

The current synthetic fixture gate tests the 50%-of-Entry-to-SL relationship
as a source-confirmed relationship from the author-controlled written source.
That is valid as a **source-candidate/relationship test**, but it must not be
interpreted as proof that the primary video uses the same numerical anchor.

No fixture result may select between:
- half target distance; and
- half Entry-to-SL distance.

The synthetic gate cannot resolve this source conflict.

### R-04 — Lifecycle remains unresolved

Neither source uniquely resolves:
- mandatory vs optional use in every setup;
- pending vs immediate/re-entry order semantics;
- activation/fill event;
- reference state if Entry or SL is refreshed;
- sizing;
- behavior when the initial entry does not fill;
- TP1/TP2 allocation;
- shared/separate invalidation;
- cancellation/replacement precedence.

### R-05 — Visual 2X ordering is not enough to define a formula

The primary frame showing Buy > 2X > SL establishes relative placement in the
illustrated bullish setup, but it does not supply price values or a measurable
ratio. Therefore the frame cannot discriminate the two numerical hypotheses.

## Canonical decision

**F13 remains PARTIAL / UNRESOLVED.**

Do NOT promote either numeric interpretation to universal canonical
execution geometry.

The author-site 50%-Entry-to-SL statement remains an author-controlled
source-confirmed relationship at its own wording level, while the primary
video's approximately-half-target-distance statement remains a distinct
source-supported relationship. The reconciliation gap is explicitly retained.

## Gate impact

- F13 concept: SOURCE-CONFIRMED.
- F13 numeric anchor: **UNRESOLVED due to source reconciliation gap**.
- F13 lifecycle: UNRESOLVED.
- Synthetic Fixture Gate: PASS (relationship harness only).
- Frozen Geometry: BLOCKED.
- Untouched Validation: LOCKED.
- Robustness/Stability: LOCKED.
- Fresh Holdout: BLOCKED.
- Production: DISABLED.
- Forward Test: UNTOUCHED.

## Required evidence for closure

A discriminating primary/author-controlled artifact must explicitly establish
which distance is intended for the 2X price construction, preferably with a
worked numeric example or a labeled price diagram that identifies Entry, SL,
Target, and 2X simultaneously.

Until that evidence exists, no implementation or backtest branch may choose
between the two anchors.
