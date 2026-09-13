# Phase 48 — Source / Geometry Freeze Readiness Audit

**Status:** NOT READY FOR FREEZE
**Gate:** SOURCE RESOLUTION INCOMPLETE
**Scope:** research-only; no production promotion

## Objective

Audit the current SP2L V2 semantic geometry against the source-first boundary before any deterministic geometry is frozen. This phase does **not** choose geometry from historical profitability and does not optimize thresholds.

## Evidence used

- `docs/research/PHASE_32_SP2L_V2_SEMANTIC_STATE_AND_FIXTURES.md`
- `src/domain/research/sp2l-v2/Sp2lSemanticState.ts`

Phase 32 explicitly established the semantic lifecycle and preserved unresolved geometry rather than inventing numeric definitions. In particular, the Leg 1 endpoint, Leg 2 projection origin, and Leg 2 equality tolerance remain unresolved.

## Geometry readiness matrix

| ID | Component | Status | Freeze decision |
|---|---|---|---|
| G1 | First structural high/low | CANDIDATE | Do not freeze |
| G2 | Pending-limit price | CANDIDATE | Do not freeze |
| G3 | Structural stop | CANDIDATE | Do not freeze |
| G4 | Leg 1 endpoint | TBD | Do not freeze |
| G5 | Leg 2 projection origin | TBD | Do not freeze |
| G6 | AB=CD / equality tolerance | TBD | Do not freeze |
| G7 | Fill / intrabar semantics | CANDIDATE | Do not freeze |

### G1 — First structural high/low

The semantic state has an explicit `firstStructuralReference` field and supports `SOURCE_CONFIRMED`, `CANDIDATE`, or `TBD`. The current evidence establishes the concept but not a frozen source geometry rule for selecting the exact high/low anchor.

**Decision: CANDIDATE.**

### G2 — Pending-limit price

The lifecycle requires an explicit pending-limit price and explicitly rejects a missing entry price. This protects the distinction between a pending limit and a close-reclaim fallback. The exact source-confirmed construction of the pending price is not frozen by the evidence audited here.

**Decision: CANDIDATE.**

### G3 — Structural stop

The lifecycle requires an explicit structural stop before a pending order exists. The source-aligned concept is therefore represented, but the exact source anchor/placement geometry is not yet frozen.

**Decision: CANDIDATE.**

### G4 — Leg 1 endpoint

Phase 32 explicitly records that the Leg 1 endpoint remains `TBD` until the source is complete.

**Decision: TBD.**

### G5 — Leg 2 projection origin

Phase 32 explicitly records that the Leg 2 projection origin remains `TBD` until the source is complete. The semantic model intentionally permits several candidate concepts without selecting one as canonical.

**Decision: TBD.**

### G6 — AB=CD / equality tolerance

AB=CD is a source-aligned relationship, but no numeric equality tolerance is established in the audited evidence. The semantic model therefore leaves the tolerance unset instead of fitting one to historical results.

**Decision: TBD.**

### G7 — Fill / intrabar semantics

The model requires explicit same-candle policy and supports `SL_FIRST`, `TP_FIRST`, and `AMBIGUOUS`. The audited source evidence does not establish a canonical intrabar ordering policy.

**Decision: CANDIDATE.**

## Freeze decision

**NOT READY FOR FREEZE.**

All seven geometry items are critical to a deterministic production interpretation. At least G4, G5, and G6 are explicitly unresolved. G1–G3 and G7 have deterministic semantic containers but are not source-confirmed enough to promote to canonical geometry.

No P-Gap formula, A/B/C/D anchor, AB=CD tolerance, fill price equivalence, or intrabar ordering rule is invented in this phase.

## Historical-results firewall

Phases 42–47 may inform research prioritization, but their profitability results cannot be used to decide what the source means. In particular, the positive counterfactual results do not justify freezing a geometric interpretation.

## Protected boundaries

- Production Strategy A remains untouched.
- Fresh Holdout remains locked.
- No VAL/Fresh optimization.
- No threshold mining.
- No P-Gap formula invention.
- No generic FVG substitution.
- No A/B/C/D anchor invention.
- No pending-limit-to-market-reclaim substitution.
- No source meaning selected from backtest performance.

## Next gate

The next work should remain **SOURCE RESOLUTION**: resolve G1–G7 from authoritative source material and source visuals, one geometry question at a time, then discriminate competing interpretations with synthetic fixtures before historical evaluation.
