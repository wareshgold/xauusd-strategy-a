# G357 — Official SP2L Page vs Original Lesson Reconciliation

**Date:** 2026-09-12  
**Gate:** SOURCE RESOLUTION  
**Issue:** #89  
**Status:** PASS for conflict classification; canonical executable geometry remains unresolved

## 1. Sources compared

### A. Original SP2L lesson

Preserved in `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt` and the associated visual audit package.

Relevant source-confirmed/supporting observations include:

- SP2L is presented as Spike → 2Leg / AB=CD.
- After the spike, correction is explicitly described.
- The presenter says the order can be placed manually or as a pre-defined limit order during the correction.
- The lesson explicitly discusses placing the limit order after the initial three-candle structure.
- Structural invalidation is described: if price returns through the invalidation area, the scenario is cancelled.
- TP1/TP2 and R1/R2 are explicitly used.
- Leg 1 / Leg 2 and AB=CD are explicitly discussed.

### B. Official Poursamadi SP2L webpage

The official page adds a concise public description:

- after the spike, wait for the corrective candle to reach the previous candle low/high;
- entry is in the direction of the spike;
- SL is placed behind the candle from which the spike originated;
- default TP is 1:1;
- a secondary/add-on entry may be placed at 50% of the entry-to-stop distance;
- high-volume sessions are described as more favorable, not as a hard universal gate;
- the page explicitly advises backtesting and defining exact entry conditions before live use.

## 2. Claim classification

| Claim | Original lesson | Official page | G357 classification |
|---|---|---|---|
| Spike → correction → continuation | Explicit | Explicit | **SOURCE-CONFIRMED** |
| P-GAP required for valid spike | Explicit | Explicit | **SOURCE-CONFIRMED** |
| Entry direction follows spike | Explicit | Explicit | **SOURCE-CONFIRMED** |
| Correction reaches prior candle low/high | Lesson contains correction/trigger examples; exact universal formulation is less explicit | Explicit | **SOURCE-SUPPORTED, BUT EXACT UNIVERSAL TRIGGER FORMULATION REQUIRES CARE** |
| Manual or pending-limit entry during correction | Explicit | Public page simplifies the description | **SOURCE-CONFIRMED FOR LESSON; PAGE IS A SIMPLIFICATION** |
| SL behind spike-origin candle | Lesson discusses structural invalidation and stop distance; exact universal candle rule is not frozen | Explicit | **SOURCE-SUPPORTED / EXECUTABLE FORM STILL REQUIRES RECONCILIATION** |
| Secondary entry at 50% of entry-to-SL distance | Not established in preserved lesson evidence | Explicit | **SOURCE-CONFIRMED AS OFFICIAL-PAGE CLAIM; NOT YET CANONICAL STRATEGY RULE** |
| Default TP 1:1 | Public page says default 1:1 | Lesson also discusses R1/R2, TP1/TP2 and larger reward choices | **CONFLICT / SCOPE-DEPENDENT; DO NOT COLLAPSE** |
| TP1/TP2 and R1/R2 | Explicit | Page simplifies to default TP 1:1 | **SOURCE-CONFIRMED LESSON SEMANTICS** |
| AB=CD / Leg2≈Leg1 | Explicit | Not central on public page | **SOURCE-CONFIRMED LESSON GEOMETRIC CONCEPT** |
| Session preference | Mentioned as context | High-volume/NY described as favorable | **CONTEXTUAL, NOT HARD GATE** |

## 3. Important reconciliation

The official page should not be treated as a replacement for the original lesson. It is a public condensed description. In particular, its `default TP 1:1` statement does not erase the original lesson's explicit TP1/TP2, R1/R2, 2X/3X reward-selection, and AB=CD / second-leg discussion.

Likewise, the page's `corrective candle reaches previous candle low/high` statement can be preserved as a source-supported trigger description, but it does not by itself establish the exact executable pending-limit price, the exact fill semantics, or the exact A/B/C/D anchor mapping used by the longer lesson.

The 50% secondary-entry statement is genuinely new authoritative evidence relative to the preserved lesson package. It must therefore be tracked as a separate source-supported rule candidate rather than silently backfilled into historical research or production code.

## 4. Canonical rule freeze status

The following remain blocked:

- exact P-GAP executable formula;
- P-GAP wick/body/open/close convention;
- minimum gap size and tolerance;
- exact A/B/C/D anchor selectors;
- whether the primary pending-limit price is a structural point, candle field, geometric projection, or another source-defined location;
- exact executable SL field/offset semantics;
- exact TP1/TP2 numeric mapping;
- exact interaction between default 1:1 public-page TP and lesson AB=CD/R1/R2 outcomes;
- whether the 50% secondary entry is mandatory, optional, or conditional in the full methodology.

## 5. Gate decision

**G357 = PASS — OFFICIAL PAGE / LESSON CLAIMS RECONCILED AT THE SEMANTIC LEVEL.**

The reconciliation does **not** justify a geometry freeze. Where the public page is more specific than the preserved lesson, the claim is retained as authoritative source evidence but its executable semantics remain separate until the source provides enough detail to implement it without invention.

No historical optimization, production/live changes, or canonical rule promotion are made by this audit.
