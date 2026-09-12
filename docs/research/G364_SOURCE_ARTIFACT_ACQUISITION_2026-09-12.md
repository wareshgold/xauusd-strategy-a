# G364 — Source Artifact Acquisition Audit

Date: 2026-09-12
Gate: SOURCE RESOLUTION
Status: **BLOCKED — primary-source geometry not yet resolved**

## Objective
Acquire or identify authoritative first-party evidence capable of resolving executable Strategy A geometry without inference from backtest performance or third-party implementations.

## Acquisition targets

| Dimension | Required primary-source evidence | Current result |
|---|---|---|
| P-Gap endpoints | Explicit candle indices and/or labeled OHLC endpoints | NOT FOUND |
| Gap field convention | Wick/body/open/close semantics | NOT FOUND |
| Gap tolerance | Minimum size, overlap, or tolerance | NOT FOUND |
| Pressure context | Exact universal candle-count rule | NOT FOUND |
| Breakout/FT/P-Gap | Deterministic ordering/eligibility | PARTIALLY SOURCE-SUPPORTED, NOT EXECUTABLE |
| A/B/C/D | Explicit labels or unambiguous definitions | NOT FOUND |
| Parent/nested scale | Deterministic selection rule | NOT FOUND |
| Pending limit | Exact price-placement rule | NOT FOUND |
| Fill semantics | Relationship between trigger, order, fill, and C | NOT FOUND |
| SL | Exact field/boundary/offset | SEMANTIC ONLY |
| TP1/TP2/R1/R2 | Exact executable mapping | NOT FOUND |
| Default 1:1 | Scope/reconciliation with lesson target structure | NOT RESOLVED |
| 50% secondary | Mandatory/conditional/optional scope | NOT RESOLVED |

## Primary-source search performed

### Official Poursamadi SP2L page
The official page confirms:
- valid Spike requires P-Gap;
- corrective candle reaches previous candle low/high depending on direction;
- secondary entry may be added at 50% of entry-to-SL distance;
- entry follows Spike direction;
- SL is behind the candle from which Spike originated;
- default TP is 1:1;
- exact entry conditions should be defined and backtested before live use.

These statements strengthen semantic rules but do not specify executable OHLC geometry. The page also explicitly contrasts SP2L with Pro BTB, so BTB entry rules must not be imported into SP2L.

### Official Poursamadi material already in project
The full SP2L lesson and Gap lesson remain the strongest visual/transcript sources. They establish P-Gap = Pressure Gap and the Spike → correction → pending-limit → Leg2/AB=CD chain, but do not label the missing executable endpoints sufficiently to freeze them.

### Other official Poursamadi pages
The official Pro BTB page contains detailed breakout/retest entry methods, but it explicitly describes Pro BTB as different from SP2L. Therefore its Buy Limit/Buy Stop/market rules are **not transferable** to Strategy A.

### Third-party implementations
Third-party SP2L implementations were treated only as provenance leads. They are not authoritative and cannot promote any geometry to canonical Strategy A. No implementation-specific formula is imported.

## Evidence classification

### Resolved enough for semantic layer
- SP2L = Spike → 2Leg / AB=CD.
- P-Gap = Pressure Gap.
- correction follows Spike.
- pending-limit entry is part of the lesson workflow.
- entry direction follows Spike.
- spike-origin SL concept exists.
- TP/reward terminology exists.

### Still blocked for deterministic implementation
No primary-source artifact located in this acquisition pass provides a complete machine-readable definition for P-Gap, A/B/C/D, exact limit placement/fill, exact SL boundary, or exact TP mapping.

## Important non-transfer rule
The official Pro BTB page describes a different strategy and explicitly distinguishes it from SP2L. Its six entry scenarios and broken-level mechanics must not be used to fill SP2L gaps.

## Gate decision

**G364 = PASS for acquisition audit / BLOCKED for geometry resolution.**

The search has not produced sufficient primary-source evidence to pass FROZEN_GEOMETRY. The correct next action is to acquire missing first-party artifacts if available (original course slides/PDFs, labeled screenshots, source lesson segments) rather than infer rules.
