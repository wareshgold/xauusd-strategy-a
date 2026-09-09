# SP2L Source Resolution Blocker Matrix V1 — 2026-09-09

## Purpose

Consolidate the research state through F15 and define the minimum remaining source questions blocking Frozen Geometry. This is a source-first artifact: profitability, optimization, and backtest results are not evidence of source meaning.

## Current gate status

| Gate | Status | Meaning |
|---|---|---|
| SOURCE RESOLUTION | PARTIAL PASS | Core semantics materially resolved; executable geometry still has blockers |
| SYNTHETIC FIXTURES | PASS / ONGOING | Competing interpretations are represented without forcing unresolved choices |
| FROZEN GEOMETRY | BLOCKED | No production-grade formula/anchor set is authorized |
| DEV | LOCKED | Must not begin canonical implementation |
| UNTOUCHED VALIDATION | LOCKED | Holdout remains untouched |
| ROBUSTNESS / STABILITY | LOCKED | Not meaningful before frozen rules |
| FRESH HOLDOUT | LOCKED | Not meaningful before frozen rules |
| PRODUCTION | LOCKED | No live BUY/SELL engine authorized |

## Consolidated evidence decisions

| Area | Current source conclusion | Status | Blocking severity |
|---|---|---|---|
| SP2L identity | Spike → 2 Leg | CONFIRMED | None |
| Context/range | Market context/range is taught | CONFIRMED SEMANTIC | Medium: exact algorithm not frozen |
| Spike | Directional price-action structure | CONFIRMED SEMANTIC | High: exact variant taxonomy remains source-dependent |
| Breakout/follow-through | Required source concepts | CONFIRMED SEMANTIC | High: exact detection boundaries unresolved |
| P-Gap | Associated with valid breakout; distinct from generic E-Gap/Common-Gap | CONFIRMED CONCEPT | **CRITICAL** |
| P-Gap geometry | Multiple source constructions shown | UNRESOLVED | **CRITICAL** |
| Correction | Entry phase after first leg/spike | CONFIRMED SEMANTIC | High: exact boundary unresolved |
| Relevant Low/High | First/relevant structural reference; evolving HL/LH is visually supported | CANDIDATE | **CRITICAL** |
| Entry price | Pending Limit at relevant structural reference | CANDIDATE | **CRITICAL** |
| Entry vs Leg2 start | Distinct references | CONFIRMED | None |
| Structural invalidation | Separate from Entry | CONFIRMED SEMANTIC | High |
| SL anchor | Structural invalidation, but OHLC anchor unresolved | UNRESOLVED | **CRITICAL** |
| Wick vs body | Not uniquely source-labelled | UNRESOLVED | **CRITICAL** |
| Stop buffer/spread | Not source-confirmed | UNRESOLVED | High |
| Pending replacement | Allowed when distance materially changes | CONFIRMED SEMANTIC | High: threshold unresolved |
| Trigger | 1/2/3 candle family + confirmation/key-bar examples | CONFIRMED FAMILY | **CRITICAL** |
| Trigger acceptance | Exact candle logic/timing unresolved | UNRESOLVED | **CRITICAL** |
| 2X | Source concept / second-position management | CONFIRMED CONCEPT | High: exact formula unresolved |
| TP1/TP2 | TP1 preferred by teacher; TP2 to be backtested | CONFIRMED PREFERENCE | High: exact target algorithm unresolved |
| Leg2 | Continuation following correction | CONFIRMED SEMANTIC | High: exact projection anchor unresolved |
| AB=CD | Leg2 magnitude related to Leg1 | CONFIRMED RELATIONSHIP | **CRITICAL** |
| A/B/C/D anchors | No unique source-labelled OHLC anchors | UNRESOLVED | **CRITICAL** |
| AB=CD tolerance | No source tolerance identified | UNRESOLVED | **CRITICAL** |
| Bearish mirror | Abstract directional mirror representable; source-specific geometry not proven | PARTIAL | High |
| Session filter | New York/good hours discussed, but canonical filter not frozen | UNRESOLVED | Medium |

## F02–F15 research state

The exact early fixture numbering is preserved in repository history; the consolidated state is:

- **F8** — first/relevant Low vs evolving latest HL/LH: no universal winner; latest relevant HL/LH is a leading candidate for demonstrated variant.
- **F9** — Entry vs Leg-2 start: deliberately separated; canonical equality rejected.
- **F10** — structural SL/risk boundary: structural invalidation governs strategy; risk budget must not rewrite geometry; wick/body and exact anchor unresolved.
- **F11** — pending-order update: KEEP/DELETE/REPLACE represented; numerical replacement threshold intentionally not invented.
- **F12** — trigger family: 1/2/3-candle candidates retained; no single trigger promoted.
- **F13** — 2X: half-target and second-position interpretations retained; formula unresolved.
- **F14** — AB=CD: wick/body/structural-pivot/mixed anchor models represented; multiple models satisfy equality, so no canonical anchor selected.
- **F15** — bearish mirror: directional structural mirror passes as an abstraction; this does not source-prove all bearish geometry.

## Critical blockers

### B1 — P-Gap geometry

Need direct source evidence sufficient to identify the exact candle/price boundaries of P-Gap across the demonstrated valid constructions. A generic three-candle imbalance is explicitly not authorized as a substitute.

### B2 — Relevant structural Low/High and Entry anchor

Need enough source examples to determine whether Entry is consistently:

- the first relevant correction low/high;
- the latest completed HL/LH;
- another explicitly defined structural point;
- or a variant-specific rule.

No body/wick/Fibonacci proxy may be selected without evidence.

### B3 — Structural SL anchor

Need direct source geometry to resolve whether invalidation is based on wick extreme, candle body, structural pivot, or another source-defined level, plus whether any source-defined buffer exists.

### B4 — Trigger acceptance

Need source examples to distinguish 1-, 2-, and 3-candle trigger forms and identify what makes each valid, including the role of key bar/confirmation and exact timing relative to the pending Limit.

### B5 — AB=CD anchors and tolerance

Need source evidence that uniquely identifies A/B/C/D or explicitly establishes that the relationship is only approximate magnitude. If no unique anchor is source-supported, the implementation must retain a source-level magnitude relationship rather than inventing four OHLC points or a tolerance.

### B6 — Leg2 / TP1 geometry

Need source geometry linking Leg1, Leg2, TP1 and the entry/structural levels. The source establishes the concepts but not yet a complete executable formula.

### B7 — Pending replacement threshold

Need source evidence if the qualitative “materially different” rule has a numerical threshold. Until then, production must not invent one.

### B8 — Bearish direct evidence

Need at least one direct bearish source example that confirms the mirror at the level of actual Entry/SL/trigger geometry. Symmetry alone is not sufficient for production promotion.

## Minimum evidence package required for Frozen Geometry

Frozen Geometry should not be declared until the source package can answer, deterministically or explicitly as “source-level qualitative,” all of the following:

1. What exact event qualifies as a valid breakout?
2. What exact source-defined geometry qualifies as P-Gap?
3. What structural point is the pending Limit placed on?
4. When can that pending Limit be created, moved, deleted, or replaced?
5. What exact price invalidates the setup?
6. Is SL wick, body, pivot, or another source-defined level?
7. What candle sequence qualifies as a trigger?
8. What exact price relationship defines Leg1 and Leg2?
9. What does AB=CD mean operationally if A/B/C/D are not explicitly labelled?
10. What is the source-defined TP1 rule?
11. What is 2X operationally, and is it mandatory or optional?
12. Are bearish rules directly demonstrated or only inferred by mirror symmetry?
13. Is any session/time filter canonical or merely commentary?

## Research actions after blocker matrix

1. Perform targeted frame-by-frame triangulation of the remaining blocker questions, prioritizing B1–B6.
2. For every candidate interpretation, create or extend a synthetic fixture before considering historical data.
3. Update the source ledger with exact timestamp/frame evidence.
4. Freeze only those fields for which the source supports a unique deterministic interpretation.
5. Explicitly mark irreducible source ambiguity as `UNRESOLVED` rather than optimizing it.
6. Only after the blocker matrix reaches an acceptable resolution should the project move to Frozen Geometry.

## Non-negotiable boundary

**No backtest result can resolve a source-meaning blocker.**

If two interpretations are source-plausible and both can be implemented, the project must retain both as research candidates until direct source evidence discriminates them. If the source never discriminates them, the final specification must preserve that uncertainty rather than silently choosing the historically best-performing version.
