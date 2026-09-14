# SP2L Geometry Freeze Readiness — 2026-09-14

## Purpose

Establish the next research gate after the Replay/Backtest Audit closure. This record evaluates whether Strategy A / SP2L geometry is sufficiently source-resolved to enter **FROZEN GEOMETRY**.

This is a source-resolution record only. It does not canonicalize any unresolved rule and does not authorize DEV, validation, Fresh Holdout, or production.

## Governing rule

`Evidence → Review → Manual Approval → Canonical`

Backtest profitability, parameter stability, or implementation convenience must never select source meaning.

## Source basis

Current repository evidence includes:

- `SP2L_SOURCE_GEOMETRY_DECISION_MATRIX_V2_2026-09-09.md`
- `SP2L_VISUAL_GEOMETRY_TRIANGULATION_V3_2026-09-09.md`
- `PHASE_33_G4_LEG1_SOURCE_RESOLUTION.md`
- authoritative SP2L source video/transcript evidence recorded by the research documents.

The current source matrix explicitly states that source resolution is partial, synthetic fixtures are required, and frozen geometry remains blocked.

## Readiness matrix

| Geometry item | Current evidence state | Freeze status | Required next evidence |
|---|---|---|---|
| SP2L identity / Spike → 2 Leg | Source-supported | READY FOR MANUAL REVIEW | Preserve source wording and variant scope |
| Breakout + follow-through | Source-supported | READY FOR MANUAL REVIEW | Confirm across source examples |
| P-Gap relevance to valid breakout | Source-supported concept | BLOCKED | Resolve exact OHLC/index/equality construction from source |
| P-Gap exact formula | Unresolved | BLOCKED | Source discrimination; no generic imbalance substitution |
| Entry as pending Limit | Source-supported | READY FOR MANUAL REVIEW | Preserve pending-limit model |
| Entry anchor | Dynamic/relevant-low candidate in demonstrated bullish variant | BLOCKED | F8/F9 discrimination across source variants |
| Entry vs Leg-2 start | Must remain distinct | BLOCKED | F9 source discrimination |
| Structural invalidation exists separately from Entry | Source-supported | READY FOR MANUAL REVIEW | Resolve exact OHLC anchor |
| Stop OHLC anchor / wick-body semantics | Unresolved | BLOCKED | F10 discrimination |
| Pending-order refresh | Qualitatively source-supported | BLOCKED | F11; no invented replacement threshold |
| Trigger family | 1/2/3-candle family source-supported | BLOCKED | F12 acceptance taxonomy |
| Leg-2 magnitude ≈ Leg-1 magnitude | Source-supported | READY FOR MANUAL REVIEW | Preserve as magnitude relationship only |
| A/B/C/D anchors | Unresolved | BLOCKED | F14 discrimination |
| AB=CD tolerance | Unresolved | BLOCKED | Source evidence; no numerical tolerance invention |
| 2X concept | Source-supported concept | BLOCKED | F13 formula discrimination |
| TP1 / TP2 exact formula | Unresolved | BLOCKED | Source evidence and F13/F14 as applicable |
| Bearish mirror | Incomplete direct confirmation | BLOCKED | F15 source visual confirmation |
| Session/time filter | Unresolved | BLOCKED | Source-confirmed evidence only |

## Synthetic fixture gate

The next implementation task is **not** historical optimization. It is a deterministic synthetic fixture suite whose sole purpose is to discriminate competing source interpretations.

Required fixture set:

- **F8:** evolving higher-low / pending-limit refresh.
- **F9:** Entry vs Leg-2 start with deliberately separated prices.
- **F10:** structural invalidation vs risk-budget stop; wick/body and base/opposite-swing alternatives.
- **F11:** pending-order update lifecycle without inventing a replacement threshold.
- **F12:** 1-, 2-, and 3-candle trigger variants.
- **F13:** 2X competing interpretations.
- **F14:** competing A/B/C anchors for AB=CD.
- **F15:** mirrored bearish constructions.

All fixture prices are synthetic and **non-canonical**. A fixture result may eliminate an interpretation only when source evidence supports that elimination; fixture behavior itself cannot establish source meaning.

## Freeze decision rule

Do **not** enter FROZEN GEOMETRY unless all required production geometry has:

1. source evidence sufficient to define its meaning;
2. no unresolved competing interpretation that materially changes the deterministic decision;
3. explicit input/output semantics;
4. deterministic edge-case behavior;
5. fixture coverage for the resolved interpretation;
6. documented provenance;
7. explicit manual approval by Ali.

If any condition fails, status remains **BLOCKED** or **HYPOTHESIS**.

## Current gate decision

**SOURCE RESOLUTION: PARTIAL PASS**

**SYNTHETIC FIXTURES: REQUIRED / NEXT**

**FROZEN GEOMETRY: BLOCKED**

**DEV: LOCKED**

**UNTOUCHED VALIDATION: LOCKED**

**ROBUSTNESS / STABILITY: LOCKED**

**FRESH HOLDOUT: LOCKED**

**PRODUCTION: LOCKED**

## Explicit non-decisions

This record does not decide:

- P-Gap formula;
- A/B/C/D anchors;
- AB=CD tolerance;
- exact entry-price formula;
- exact stop-price formula or buffer;
- pending-order replacement threshold;
- exact trigger taxonomy;
- 2X formula;
- TP1/TP2 formula;
- session filter.

No common price-action concept may be substituted for any of these without source evidence.

## Next action

Build the **F8–F15 source-discrimination fixture pack** as research-only synthetic fixtures, then update the evidence ledger with `CANONICAL`, `HYPOTHESIS`, `BLOCKED`, or `REJECTED` statuses. Do not wire unresolved geometry into the deterministic production engine.
