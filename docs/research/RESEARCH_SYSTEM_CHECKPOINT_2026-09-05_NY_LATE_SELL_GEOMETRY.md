# XAUUSD Strategy A — Research System Checkpoint
## 2026-09-05 — NY Late SELL Path Geometry

## Current branch
`research/strategy-a-poorsamadi-geometry`

## Purpose
This checkpoint records the complete research state after the corrected NY-Late SELL path/geometry analysis. It is research-only. Production Strategy A rules remain unchanged and the fresh holdout remains locked.

## Research discipline
- Strategy decisions remain deterministic and rule-based.
- No production rule is promoted from exploratory evidence.
- DEV is used for discovery; VAL is chronological out-of-sample validation.
- Fresh holdout is excluded until a hypothesis is explicitly frozen and replicated once.
- No threshold hunting on VAL or fresh holdout.
- No hindsight leakage.
- Canonical Strategy A reconstruction must match the baseline candidate exactly.
- Preserve existing reports and local changes; do not blindly reset/delete.
- AI must not arbitrarily generate BUY/SELL decisions.

## Canonical data / timezone model
- Canonical historical data remains UTC.
- Dataset integrity audit passed: 1m and 5m datasets had no duplicates, invalid OHLC, non-chronological rows, or detected gaps.
- Iran timezone is display/context only.
- Session research uses DST-aware IANA zones:
  - London: `Europe/London`
  - New York: `America/New_York`
- Research London→NY window: London local >= 08:00 and New York local < 17:00.
- NY Late research cell: London local >= 08:00 AND New York local 14:00–17:00.
- Do NOT change canonical baseline fixed session parameters merely to reflect the research timezone correction.

## Strategy/source semantic model
Integrated source-consistent path remains:
`TIME / SESSION → LOCATION / LEVEL → RANGE / CONTEXT → BREAKOUT → FOLLOW-THROUGH / PRESSURE → SPIKE FAMILY → STRUCTURAL LOW/HIGH → CORRECTION → PENDING LIMIT / ENTRY → STRUCTURAL STOP → LEG2 ≈ LEG1 → TP1 → OPTIONAL 2X / MANAGEMENT`

Source-established points:
- SP2L = SPIKE-2LEG; Leg2 is expected approximately equal to Leg1.
- Breakout should close beyond the prior level and show follow-through.
- P-GAP is conceptually distinct from generic/exhaustion/morning gaps; exact numeric geometry remains TBD.
- Source demonstrates pending/limit entry when correction starts at a structural level; current baseline close-reclaim trigger is known to conflict with the source and remains unchanged for research integrity.
- Structural invalidation likely depends on price reach/touch rather than close-only; exact production rule remains TBD.

## Prior T1 MAE research
Objective: incremental post-entry MAE information.
- T1 was robustly informative in DEV and VAL.
- T2|T1 and T3|T1,T2 were not robustly incrementally informative.
- 5m bins3 T1 CMI: DEV 0.1753 (p=.002), VAL 0.2202 (p=.002).
- Extreme T1 state showed strong fresh-holdout degradation, but state-transition analysis showed the extreme state was mostly same-bar SL / already-determined outcome.
- Therefore T1 is not an actionable post-entry rule. The correct research target is pre-entry prediction of future T1 extreme state.
- No T1-derived production rule was promoted.

## Corrected London→NY session research
Simple DST-aware London 08:00 → NY 17:00 filter did NOT create a stable edge.

5m corrected-window universe:
- Overall N=266; DEV=159; VAL=107.
- DEV ALL AvgR +0.2335, PF 1.334.
- VAL ALL AvgR -0.0987, PF 0.868.
- DEV SELL +0.8709 PF 2.341; VAL SELL +0.0361 PF 1.051.

Therefore simple session filtering is not a production candidate.

## Corrected intraday attribution V2
Four DST-aware windows inside London→NY:
- london_pre_ny_open
- ny_open
- ny_mid
- ny_late

Key current lead:
### 5m NY Late SELL
- DEV N=9 in the structural reconstruction / 15 total path universe.
- Intraday attribution showed NY Late SELL as the strongest current research lead:
  - DEV AvgR +1.4742R, PF 3.948
  - VAL AvgR +1.1362R, PF 2.894
- This was directionally and economically stable across DEV and VAL.
- This is NOT yet a production rule because sample size is small and causal structure has not been established.

1m NY Late SELL was negative and unstable and is deprioritized:
- Structural subset N=31; DEV AvgR -0.8271; VAL -0.6203.

## NY Late SELL structural attribution
Analyzer: `scripts/analyze-ny-late-sell-structure-v1.mjs`

5m NY Late SELL structural universe:
- N=15; DEV=9; VAL=6.
- DEV AvgR +1.4814R, PF 3.6665.
- VAL AvgR +1.6813R, PF 4.3626.

Observed structural predicates:
- EMA aligned: all 15; therefore EMA is not an independent explanation in this cell.
- P-GAP: 0; current detector provides no usable attribution here.
- Structure >=0.7: DEV N=6 AvgR +1.1238 PF 3.2476; VAL N=5 AvgR +2.2175 PF 6.5439.
- Overlap >=0.7: DEV N=2 AvgR +4.8529; VAL N=2 AvgR +5.3682 PF 11.7363. Too small for inference.
- Round level: DEV N=5 AvgR +0.9179 PF 2.1474; VAL N=2 AvgR +0.6757. Too small for inference.
- Delay <=1: DEV N=8 AvgR +1.7916 PF 4.5831; VAL N=3 AvgR +3.2454 PF 5.8682. Interesting but VAL N=3 is too small for promotion.
- Correction depth <=0.5: DEV N=8 AvgR +1.6278 PF 3.6045; VAL N=6 AvgR +1.6813 PF 4.3626. This is the most consistently populated positive geometry observation so far.
- Fast + shallow: DEV N=7 AvgR +2.0032 PF 4.5056; VAL N=3 AvgR +3.2454 PF 5.8682.
- Clean + fast + shallow: DEV N=4 AvgR +1.8582; VAL N=3 AvgR +3.2454. Too small.
- Less-clean structure did not support a robust structural-only explanation: DEV N=3 positive but VAL N=1 was -1R.

## Latest Path Geometry V1
Analyzer:
`scripts/analyze-ny-late-sell-path-geometry-v1.mjs`

The first execution exposed an analyzer bug: outcomes were stored in `features.r` while `stats()` read `row.r`, producing false zero statistics. This was fixed in commit:
`cf04ac5526a9bf46b93f0e8362e30810934cd739`

Corrected execution:
### 1m
- N=31; DEV=26; VAL=5.
- DEV AvgR -0.827128 PF 0.064986.
- VAL AvgR -0.620325 PF 0.224594.
- Geometry is broadly negative; no viable candidate.

### 5m
- N=15; DEV=9; VAL=6.
- DEV AvgR +1.481387 PF 3.666497.
- VAL AvgR +1.681291 PF 4.362582.

Fixed predeclared archetypes:
- fastCorrection: DEV N=2 AvgR +0.1736; VAL N=0.
- slowCorrection: DEV N=7 AvgR +1.8550 PF 3.5971; VAL N=6 AvgR +1.6813 PF 4.3626.
- shallowCorrection: DEV N=8 AvgR +1.6278 PF 3.6045; VAL N=6 AvgR +1.6813 PF 4.3626.
- deepCorrection: DEV N=1 +0.3102; VAL N=0.
- fastEntry: DEV N=8 +1.7916 PF 4.5831; VAL N=3 +3.2454 PF 5.8682.
- delayedEntry: DEV N=1 -1; VAL N=3 +0.1171 PF 1.3514.
- shortSpike: DEV/VAL N=0.
- longSpike: all 15.
- cleanStructure: DEV N=6 +1.1238 PF 3.2476; VAL N=5 +2.2175 PF 6.5439.
- lessCleanStructure: DEV N=3 +2.1965 PF 4.2948; VAL N=1 -1.
- cleanOverlap: DEV N=2 +4.8529; VAL N=2 +5.3682 PF 11.7363; too small.
- lessCleanOverlap: DEV N=7 +0.5181 PF 1.7253; VAL N=4 -0.1621 PF 0.6757.
- roundLevel: DEV N=5 +0.9179 PF 2.1474; VAL N=2 +0.6757.
- emaAligned: all 15.
- fastShallow: DEV N=7 +2.0032 PF 4.5056; VAL N=3 +3.2454 PF 5.8682.
- cleanFastShallow: DEV N=4 +1.8582 PF 4.7163; VAL N=3 +3.2454 PF 5.8682.

## Current interpretation
The strongest source-consistent working hypothesis is NOT a numeric rule yet. It is:

**5m NY-Late SELL setups following a valid bearish spike, with a relatively shallow correction and a prompt SELL re-entry after the structural high, may have positive expectancy.**

Important distinctions:
- `correctionDepth <= 0.5` is an exploratory archetype cutoff, not a promoted production threshold.
- `entryDelay <= 1` is an exploratory archetype cutoff, not a promoted production threshold.
- `fastShallow` and `cleanFastShallow` are descriptive combinations only.
- N is too small to claim causality or a final rule.
- The apparent edge may still be explained by time/direction selection or a few large winners.

## Known analyzer gap to fix next
Path Geometry V1 still has incomplete breakout geometry instrumentation:
- `breakoutExtension` is currently null.
- `addBreakoutGeometry()` is effectively unused.
- `meta.breakoutIndex` is not populated in the returned row.

Therefore the next analyzer revision should correctly capture and report:
1. breakout level / broken level;
2. breakout candle close and extension beyond level;
3. breakout→follow-through distance / timing;
4. spike size relative to preceding range;
5. spike duration;
6. structural high;
7. correction depth and duration;
8. entry distance from structural high;
9. entry delay;
10. stop distance / planned RR;
11. Leg1 size.

Then inspect the 15 5m cases row-by-row and compare DEV vs VAL. This remains descriptive path analysis, not threshold optimization.

## Fresh holdout status
**LOCKED.**
Do not inspect, optimize against, or test the fresh holdout until a specific hypothesis is explicitly frozen from DEV/VAL evidence.

## Production status
**UNCHANGED.**
No NY-Late filter, correction-depth rule, entry-delay rule, structure rule, or geometry rule has been promoted.

## Immediate next step
1. Fix/complete Path Geometry V2 breakout→spike→correction→entry instrumentation.
2. Run locally.
3. Inspect the 15 5m cases and DEV/VAL distributions.
4. Decide whether one source-consistent hypothesis is sufficiently predeclared to freeze.
5. Only then, if justified, perform a single fresh-holdout replication.

## Last relevant commits
- `4dfbd89255dd05550db4797f95e374a6fca2a8c8` — add NY Late SELL Path Geometry V1
- `cf04ac5526a9bf46b93f0e8362e30810934cd739` — fix NY Late SELL geometry outcome stats

## Canonical/earlier checkpoints retained
Earlier research checkpoints and reports remain authoritative for their respective stages. This document is an incremental checkpoint and does not replace the semantic source documents or canonical baseline.
