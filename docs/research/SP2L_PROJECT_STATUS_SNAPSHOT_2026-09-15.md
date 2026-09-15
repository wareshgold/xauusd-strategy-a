# SP2L Project Status Snapshot — 2026-09-15

## Purpose

This is the formal continuity snapshot for the SP2L / XAUUSD Strategy A project. Its purpose is to prevent context loss, repeated work, and research loops across future sessions.

## Executive state

```text
SOURCE ARTIFACT
  ↓
SOURCE EVIDENCE / FRAME AUDIT                 COMPLETE
  ↓
EVIDENCE CANDIDATES C01–C08                  COMPLETE
  ↓
HUMAN MANUAL ADJUDICATION (#175)              ACTIVE BLOCKER
  ↓
FROZEN GEOMETRY READINESS (#179)              PREPARED
  ↓
SEPARATE CANONICAL FREEZE DECISION (#180)    PREPARED
  ↓
DETERMINISTIC ENGINE / DEV                    PAUSED UNTIL FREEZE
  ↓
UNTOUCHED VALIDATION                           PAUSED
  ↓
ROBUSTNESS / STABILITY                         PAUSED
  ↓
FRESH HOLDOUT                                 PAUSED
  ↓
PRODUCTION / BUY-SELL                         LOCKED
```

## Source artifact is now registered

- Video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Source ID: `7HEC5mO3d3U`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- FPS: `30`
- Duration: `4155.6667 s`
- Deterministic frame address: `round(t * 30)`
- Persistent evidence record: `docs/research/SP2L_SOURCE_VIDEO_FRAME_AUDIT_2026-09-15.md`

The source-video frame audit is the persistent reference for routine continuity. Do not repeatedly request the video unless a future adjudication requires a new pixel-level inspection that is not represented in the audit.

## What has been established

### Source semantics supported by evidence

- SP2L is presented as Spike → 2 Leg.
- Valid breakout is explicitly associated with P-Gap in the source examples.
- Multiple spike constructions are presented; the source uses a numbered 1/2/3 construction family.
- The source presents AB=CD at candle/example level and associates the second leg with the first-leg magnitude.
- Correction and corrective Buy Limit placement are explicitly discussed/shown.
- SL is shown separately from the entry level.
- Pending-order deletion/update behavior is explicitly demonstrated.
- TP1/TP2 and a 2X/second-position concept are explicitly shown.
- Bearish continuation examples exist.

### What is NOT yet canonically resolved

All ten executable geometry dimensions remain blocked until source-discriminating evidence is manually adjudicated:

1. `p_gap`
2. `entry_anchor`
3. `leg2_start`
4. `structural_invalidation`
5. `pending_refresh`
6. `trigger_classifier`
7. `abcd_anchors`
8. `abcd_tolerance`
9. `targets_2x`
10. `bearish_mirror`

The current source-video audit narrows these hypotheses but does not itself promote them to executable rules.

## Governance gates already prepared

- Evidence Candidate Intake: implemented and CI-verified green.
- Synthetic Fixture Contract: implemented and source-safe.
- Source-Safe Replay Harness: implemented as observation-only and execution-disabled.
- Human Manual Adjudication Gate: implemented.
- Human Adjudication Worksheet: implemented and CI-verified green.
- Frozen Geometry Readiness Gate: prepared and CI-verified green on its latest verified PR state.
- Canonical Geometry Freeze Decision Contract: prepared; separate decision gate.
- Human Adjudication Execution Runbook: prepared.
- Research-vs-MT5 Data Architecture Contract: prepared as non-canonical engineering architecture.

## Active work items

### #175 — Human manual adjudication

This is the current real research blocker.

Required sequence:

1. C01 P-Gap
2. C02 Entry anchor
3. C08 Correction / invalidation
4. C03 Leg-2 / AB=CD
5. C04 TP1 / TP2 / 2X
6. C05 Bearish mirror
7. C06 Pending refresh
8. C07 Trigger classifier

Each must receive exactly one allowed human outcome:

- `SOURCE_DISCRIMINATED`
- `REMAINS_BLOCKED`

AI may prepare evidence briefs and provenance. AI must not decide the source meaning on behalf of the human adjudicator.

### #179 — Frozen Geometry Readiness

Consumes valid human adjudication records. It must remain `BLOCKED` unless all ten dimensions have valid source-discriminated, reproducible, no-invention adjudications.

### #180 — Separate canonical freeze decision

A separate decision is required after readiness. There is no partial canonical freeze. If any executable dimension remains unresolved, the canonical freeze remains blocked.

## Engineering / data-plane position

Research data and production MT5 data are intentionally separated.

```text
RESEARCH
provider/raw market data
    → immutable source dataset
    → deterministic replay / statistical validation

PRODUCTION
MT5 / broker feed
    → provider-neutral Strategy A engine
    → MT5 EA/runtime
```

Twelve Data XAU/USD remains the initial research data candidate already documented by the project. MT5 Strategy Tester is a later implementation/runtime validation layer; it must not be used to resolve source ambiguity.

## Explicitly paused

Do not advance these stages until canonical geometry is explicitly frozen:

- executable Strategy A signal specification;
- P-Gap implementation;
- entry/fill implementation;
- AB=CD anchor/tolerance implementation;
- pending-order refresh implementation;
- target/2X formula implementation;
- bearish mirror implementation;
- production BUY/SELL generation;
- optimization used to choose among source hypotheses.

## Loop-prevention rules

Future sessions MUST follow these rules:

1. **Do not restart source hunting** unless a genuinely new Tier-1/Tier-2 discriminator appears.
2. **Do not create duplicate evidence-intake / fixture / adjudication infrastructure** when the existing contracts already cover the need.
3. **Do not use backtest performance to resolve source meaning.**
4. **Do not infer missing formulas, thresholds, buffers, candle indexes, fills, or symmetry.**
5. **Do not partially freeze geometry.**
6. **Do not start deterministic Strategy A execution development before the separate canonical freeze decision.**
7. **Do not claim CI green unless the exact current commit/run has been verified.**
8. **Do not merge research PRs automatically.**
9. When context is lost, read this snapshot and the source-video frame audit first, then continue from the active gate instead of recreating prior steps.
10. The active gate is human adjudication, not another engineering PR.

## Next concrete actions

### Immediate

- Human adjudicate C01–C08 using the persistent evidence audit + existing candidate package.
- Record the exact source evidence and rationale in the Manual Adjudication contract.

### After adjudication

- Run Frozen Geometry Readiness (#179).
- If and only if all ten dimensions are source-discriminated and reproducible, execute the separate canonical freeze decision (#180).
- Only after explicit freeze: resume deterministic engine integration.

### Statistical validation after freeze

Follow the fixed sequence:

`FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

A high development win rate is not sufficient evidence of a robust edge. Stability across time/regimes and untouched/fresh holdout performance are required before production authorization.

## Current bottom line

**The project is not blocked by missing infrastructure. It is blocked by human source adjudication of the remaining ten executable geometry dimensions.**

The correct next move is therefore to adjudicate C01–C08 from the recorded source evidence, not to invent geometry, rerun generic backtests, or create another round of infrastructure PRs.
