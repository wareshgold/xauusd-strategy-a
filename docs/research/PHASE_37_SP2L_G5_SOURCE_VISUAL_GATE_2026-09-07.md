# Phase 37 — SP2L G5 Source-Visual Gate

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research-only — no production Strategy A changes

## Objective

Complete the next G5 step without converting an unavailable visual coordinate into an invented deterministic rule.

The current repository evidence already resolves the semantic ordering:

```text
PARENT LEG 1
    -> DEEP / INTERVENING CORRECTION
    -> PARENT LEG 2
```

The remaining question is the executable OHLC coordinate of the Leg 2 projection origin `C`.

## Source audit performed

The preserved source register identifies the original Pour Samadi SP2L video and the relevant worked-example windows around 1:03:03–1:04:32. The repository also preserves the exact user-confirmed 37:22 source image for the separate LEVEL BREAK + GAP lesson.

A fresh source-index/web audit was performed against the published Pour Samadi Telegram channel and the referenced SP2L video metadata. The public index confirms the 1:09:16 SP2L recording and its lesson sequence, but it does not expose the chart pixels/OHLC coordinate needed to identify the exact `C` point in the worked example.

Therefore no new source-visual evidence is sufficient to choose among the remaining executable candidates.

## G5 decision

### G5-A — semantic origin

**SOURCE-CONFIRMED.**

Leg 2 originates from the deep/intervening correction of the intended parent leg scenario.

### G5-B — executable OHLC coordinate

**UNRESOLVED / TBD.**

The exact machine-readable `C` price cannot currently be recovered from the preserved transcript text or publicly indexed source metadata.

The remaining candidates are intentionally preserved as candidates:

1. `STRUCTURAL_HL_LH`
2. `OTHER_VISUAL_POINT`
3. `CORRECTION_EXTREME` only if a future source visual explicitly identifies the extreme as `C`

The following are explicitly **not canonical**:

- `ACTUAL_FILL` — execution event, not automatically geometric `C`;
- `PENDING_LIMIT` — execution instruction, not automatically geometric `C`.

## Why we stop here

Choosing a candidate because it produces better historical performance would violate the research authority hierarchy. Choosing a candidate because it is easiest to code would manufacture source semantics. Choosing an OHLC field merely because the phrase “deep correction” sounds like an extreme would also add an unsupported rule.

Accordingly, G5 is now frozen at the strongest evidence-supported boundary rather than guessed.

## Gate status

```text
G4 Leg1 endpoints:      SEMANTIC RESOLVED / EXECUTABLE TBD
G5 Leg2 origin:         SEMANTIC RESOLVED / EXECUTABLE TBD
G6 Leg2 equality:       BLOCKED
G7 execution semantics: RESEARCH-RESOLVED / DEPENDENT ON G4/G5
Fresh Holdout:          LOCKED
Production SP2L:        BLOCKED
```

## Next admissible work

Until new source-visual evidence becomes available, the project may continue with:

- source-shaped semantic fixtures;
- explicit state-machine invariants;
- deterministic geometry measurement helpers that accept explicit A/B/C points;
- research tooling that reports candidate geometry without selecting it;
- source-evidence audits and provenance tracking.

The project must **not**:

- select G4/G5 endpoints from DEV/VAL results;
- fit an equality tolerance;
- introduce ATR/percentage/tick/point thresholds to repair the missing geometry;
- unlock Fresh Holdout;
- modify production Strategy A semantics;
- promote `fillPrice`, `pendingEntryPrice`, or `correction.low/high` to `C` without source evidence.

## Provenance

Primary repository evidence:

- `docs/research/SP2L_SOURCE_EVIDENCE_REGISTER_2026-09-07.md`
- `docs/research/PHASE_35_SP2L_G5_SOURCE_EVIDENCE_2026-09-07.md`
- `docs/research/PHASE_36_SP2L_G5_CANDIDATE_DISCRIMINATION_MATRIX_2026-09-07.md`
- `docs/strategy/STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`

Primary external source metadata:

- Pour Samadi Telegram channel: `https://t.me/s/PORSAMADIPACKIG`
- SP2L video: `https://youtu.be/7HEC5mO3d3U`

This phase records a research boundary, not a strategy rule.
