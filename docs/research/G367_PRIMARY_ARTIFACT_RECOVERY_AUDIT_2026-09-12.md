# G367 — Primary Artifact Recovery Audit

Date: 2026-09-12
Gate: SOURCE RESOLUTION
Status: RESEARCH ONLY

## Objective
Attempt recovery of primary educational artifacts that could resolve the remaining executable SP2L geometry without using third-party implementation behavior or backtest performance as evidence.

## Primary corpus inspected
- Full SP2L lesson/transcript preserved in `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`.
- Original SP2L video supplied for frame-level inspection.
- Poursamadi Gap lesson/video supplied for frame-level inspection.
- Official Poursamadi SP2L web material.
- Existing source-evidence manifests and audits G329–G366.

## Recovery findings
The existing primary corpus contains explicit semantic evidence for P-Gap/Pressure Gap, correction, pending-limit entry, invalidation, Leg 1/Leg 2, AB=CD, reward terminology, and the official-page 50% secondary-entry/default-1:1 claims.

No recovered primary artifact was found that explicitly labels all of the following in executable OHLC terms:
- P-Gap endpoints and candle indices;
- wick/body/open/close convention;
- minimum gap, overlap, or tolerance;
- deterministic A/B/C/D anchors;
- exact pending-limit price and fill semantics;
- exact SL boundary/offset;
- exact TP1/TP2/R1/R2 mapping to executable prices;
- mandatory/conditional status of 50% secondary entry.

## Evidence boundary
Repeated frame inspection cannot manufacture missing labels. Visual geometry may be consistent with multiple OHLC interpretations. The generic bullish gap relation shown in the Gap lesson remains scoped to the generic-gap teaching example and is not promoted to the P-Gap formula.

Third-party implementations may be retained as research leads only; they are not authoritative source evidence.

## Gate decision
SOURCE ARTIFACT RECOVERY: PASS (corpus recovery/inspection complete)
FROZEN_GEOMETRY: BLOCKED

## Consequence
Do not begin canonical backtesting or production implementation. Continue only with source acquisition if a new first-party artifact becomes available, or maintain an explicitly non-canonical hypothesis layer for research.
