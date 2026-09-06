# Research Checkpoint — 2026-09-06 — Phase 9 Temporal Interaction CLOSED

## Phase 9 Status

```
PHASE_9_STATUS=CLOSED
TEMPORAL_EDGE=REJECTED
TEMPORAL_INTERACTION=NOT_ESTABLISHED
RECLAIM_LONDON_ASSOCIATION=FEATURE_ONLY_NO_TEMPORAL_STRUCTURE
FRESH=LOCKED
NO_OPT
NO_RULE
PRODUCTION_UNCHANGED
```

## Branch

`research/ny-sell-preentry-temporal-replication`

## Summary

Phase 9 was a descriptive temporal interaction audit for existing SELL-side trades. It determined whether the observed SELL-side feature associations and performance differences show reproducible time-of-day structure.

**Result: No stable SELL time-of-day edge was demonstrated.**

## Integrity

| Metric | Value |
|--------|-------|
| Pre-holdout universe | 210 |
| DEV | 128 |
| VAL | 82 |
| SELL+NEW_YORK | 29 (DEV=15, VAL=14) |
| SELL+LONDON | 58 (DEV=37, VAL=21) |
| Replay failures | 0 |
| Tests | 30/30 passed |
| Deterministic rerun | PASS |

## Key Findings

### Layer 2 — Continuous Time-of-Day

- **SELL+NY:** Spearman(triggerUTCMinutes, rMultiple) = -0.21 overall, -0.47 DEV, -0.04 VAL. Weak negative association driven by DEV but not replicating in VAL.
- **SELL+LONDON:** Spearman(triggerUTCMinutes, rMultiple) = -0.02 overall, -0.12 DEV, +0.21 VAL. Effectively zero. No time-of-day structure in outcomes.

### Layer 3 — Poorsamadi Windows

- SELL+NY trades concentrate in oceania_early (N=5), early_0300_0400 (N=12), transition_0230_0300 (N=5). Most windows empty.
- SELL+LONDON trades concentrate in us_open_1300_1530 (N=16, avgR=+3.04), late_1800_2100 (N=17, avgR=-0.07), late_2100_2400 (N=13, avgR=-0.27).
- No Poorsamadi window has N≥10 in both DEV and VAL for either SELL segment.

### Layer 4 — Feature × Time (Corrected)

**Methodological correction applied:** Layer 4 measures feature→outcome association within chronological and Poorsamadi subsets. It is NOT a formal feature×time interaction test. With SELL+NY N=29 and SELL+LONDON N=58, no defensible formal temporal interaction test was performed. Layer 2 continuous time-of-day diagnostics are the primary evidence regarding temporal structure.

### Classifications

| Feature × Session | Classification |
|-------------------|---------------|
| triggerReclaimToRange × SELL+LONDON | REPRODUCIBLE_FEATURE_ASSOCIATION_NO_TEMPORAL_STRUCTURE |
| triggerReclaimToCorrection × SELL+LONDON | REPRODUCIBLE_FEATURE_ASSOCIATION_NO_TEMPORAL_STRUCTURE |
| triggerReclaimToRange × SELL+NY | UNSTABLE_OUT_OF_SAMPLE |
| triggerReclaimToCorrection × SELL+NY | UNSTABLE_OUT_OF_SAMPLE |
| bodyParticipation × SELL+NY | DESCRIPTIVE_FEATURE_ASSOCIATION |
| bodyParticipation × SELL+LONDON | UNSTABLE_OUT_OF_SAMPLE |
| correctionBars × SELL+NY | NO_CLEAR_FEATURE_STRUCTURE |
| correctionBars × SELL+LONDON | DRIVEN_BY_EXCEPTIONAL |
| pathEfficiency × SELL+NY | DRIVEN_BY_EXCEPTIONAL |
| pathEfficiency × SELL+LONDON | DRIVEN_BY_EXCEPTIONAL |
| correctionToSpike × SELL+NY | UNSTABLE_OUT_OF_SAMPLE |
| correctionToSpike × SELL+LONDON | DESCRIPTIVE_FEATURE_ASSOCIATION |
| triggerBodyToRange × SELL+NY | DRIVEN_BY_EXCEPTIONAL |
| triggerBodyToRange × SELL+LONDON | DESCRIPTIVE_FEATURE_ASSOCIATION |

### Reclaim Features — London Finding

The SELL+LONDON reclaim features (triggerReclaimToRange, triggerReclaimToCorrection) show:
- Positive Spearman in both DEV and VAL (consistent direction)
- No sign change after removing exceptional winners
- **But no temporal component:** Layer 2 shows effectively zero time-of-day association

**Correct interpretation:** The reclaim features have a reproducible feature→outcome association that is time-invariant within SELL+LONDON. The association holds regardless of when during the London session the trade occurs. This is NOT temporal evidence.

## Methodological Lesson

The critical methodological correction in Phase 9 was recognizing that computing Spearman(feature, rMultiple) within time subsets is NOT the same as measuring a feature×time interaction. The former is a feature→outcome association measured on a subset; the latter would require comparing how the feature→outcome relationship varies across time periods.

At the current sample sizes (N=29 for SELL+NY, N=58 for SELL+LONDON), no defensible formal temporal interaction test can be performed. The honest conclusion is INSUFFICIENT_SAMPLE / INCONCLUSIVE for temporal interaction, while the feature→outcome associations remain descriptive findings.

## What Was NOT Done

- No time windows were optimized
- No thresholds were selected
- No trading rules were created
- No Fresh holdout was accessed
- No production logic was modified
- No detector semantics were changed
- No Poorsamadi windows were invented or merged

## Files Created

| File | Purpose |
|------|---------|
| `scripts/analyze-sell-temporal-interaction.mjs` | Temporal interaction analyzer |
| `data/reports/strategy-a-sell-temporal-interaction/5m.json` | Report with corrected classifications |

## Prior Research State (Accumulated)

| Phase | Topic | Result |
|-------|-------|--------|
| 1-6 | NY SELL pre-entry anatomy, temporal replication, outcome attribution, reclaim sensitivity, reclaim regime | Descriptive / Rejected |
| 7 | Trigger process / entry timing | REJECTED |
| 7b | Feature generalization across segments | SELL-generalizes for reclaim features; BUY has no signal |
| 8 | Timezone / session mapping audit | VERIFIED: UTC, LONDON 07:00-16:00, NEW_YORK 16:00-22:00 |
| 9 | Time-window interaction | REJECTED: no temporal structure |

## Recommended Next Research Axis

The pre-entry feature research for canonical SELL trades has been extensively explored:

- Feature values have been characterized (V3 geometry)
- Feature×outcome associations have been tested (generalization)
- Temporal structure has been tested (Phase 9)
- The trigger process has been tested (Phase 7)

**Remaining research directions:**

1. **Exit management / post-entry dynamics** — the T1 extreme-state research found robust but un-actionable information; a different angle may yield results
2. **Non-NY-SELL universe exploration** — BUY segments and OUTSIDE sessions have not been deeply researched
3. **Feature combination / conditional analysis** — whether combining multiple features (e.g., reclaim + correctionBars) produces stronger associations than individual features
4. **Fresh holdout evaluation** — if any finding is deemed sufficiently validated, the next step would be Fresh holdout testing (not opened in this checkpoint)

No direction is recommended over another at this checkpoint. The choice depends on the research program's strategic priorities.
