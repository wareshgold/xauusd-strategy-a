# SP2L Source-Resolution Stop Condition — 2026-09-14

## Purpose

Define a finite stopping condition for the current source-resolution pass without forcing unresolved geometry into a canonical implementation.

## Governing rule

Source meaning outranks backtest performance. A dimension may advance toward canonical review only when Tier-1/2 evidence uniquely discriminates the executable rule. If authoritative evidence does not discriminate, the correct result is `SOURCE-DOES-NOT-DISCRIMINATE` or `BLOCKED`.

## Current blocker matrix

| Dimension | Current source result | Executable status |
|---|---|---|
| P-Gap | Pressure/P-Gap semantic established | BLOCKED at exact OHLC/candle-index level |
| Entry | Pending Limit; distinct from Leg-2 start and invalidation; demonstrated relevant-HL evidence | BLOCKED at universal exact anchor |
| SL / invalidation | Spike-origin/base structural semantics; distinct from Entry and risk sizing | BLOCKED at exact OHLC boundary |
| Pending refresh | Refresh/replacement is source-supported | BLOCKED at deterministic retain/replace condition |
| Trigger | 1/2/3-candle family established | BLOCKED at final classifier |
| 2X / TP1 / TP2 | reward-management concepts established | SOURCE-DOES-NOT-DISCRIMINATE at executable formula level |
| AB=CD | Leg-2 magnitude approximately matches Leg 1 | SOURCE-DOES-NOT-DISCRIMINATE at anchors/tolerance |
| Bearish mirror | insufficient evidence for complete deterministic mirror | BLOCKED |

## Research stop condition

The current pass is considered source-resolution complete **for the presently available evidence** when:

1. every remaining executable dimension above has an explicit status;
2. each unresolved candidate has a documented negative-control reason;
3. no unresolved dimension is selected by profitability, optimization, or historical validation;
4. no invented formula, tolerance, threshold, buffer, candle index, OHLC field, fill rule, or sign-flip rule is introduced;
5. synthetic fixtures F8–F15 remain the discrimination boundary;
6. any newly discovered Tier-1/2 evidence is handled as a new evidence pass rather than silently changing the frozen research record;
7. Frozen Geometry remains BLOCKED unless and until the required executable dimensions are uniquely source-discriminated and manually approved by Ali.

## What this stop condition does NOT mean

This is not a strategy freeze, not canonicalization, not validation readiness, not Fresh Holdout authorization, and not production authorization.

It also does not claim that the source has been exhausted globally. It records that the current repository evidence has reached a justified unresolved boundary.

## Next permitted work

- Targeted search for genuinely new authoritative source evidence.
- Evidence-led updates to individual blocker records when such evidence exists.
- Research tooling and strategy-agnostic infrastructure may continue if it does not encode Strategy A geometry.
- Canonicalization remains a manual approval decision by Ali.

## Prohibited work while blockers remain

- implementing Strategy A geometry in the deterministic engine;
- choosing among candidates by backtest results;
- entering untouched validation or Fresh Holdout;
- deriving production BUY/SELL rules from unresolved hypotheses;
- treating synthetic fixture values as historical evidence.

## Gate state

- SOURCE RESOLUTION: **AT JUSTIFIED CURRENT-EVIDENCE BOUNDARY / NEW-EVIDENCE ONLY**
- SYNTHETIC FIXTURES F8–F15: **DEFINED / ADJUDICATED TO CURRENT EVIDENCE**
- FROZEN GEOMETRY: **BLOCKED**
- DEV: **LOCKED for Strategy A geometry**
- UNTOUCHED VALIDATION: **LOCKED**
- ROBUSTNESS/STABILITY: **LOCKED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **LOCKED**
