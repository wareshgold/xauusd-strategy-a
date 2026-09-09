# SP2L G40 — Source Closure Decision

Date: 2026-09-09

## Gate

SOURCE RESOLUTION closure decision / entry criteria for Frozen Geometry.

## Decision

The current authoritative source evidence establishes the semantic SP2L model but does not uniquely determine the executable OHLC geometry required for a canonical Strategy A detector.

Therefore Strategy A v1 remains **SOURCE-UNRESOLVED at executable geometry** and **FROZEN GEOMETRY BLOCKED**.

No blocker is resolved by historical profitability, optimization, or parameter selection.

## B1–B6 disposition

| Blocker | v1 disposition | Reopening evidence required |
|---|---|---|
| B1 P-Gap | SOURCE-UNRESOLVED-V1 | Authoritative source frame/text that uniquely defines participating candles and exact OHLC/range separation, including overlap/non-overlap semantics |
| B2 Entry | SOURCE-UNRESOLVED-V1 | Authoritative example or explicit rule that uniquely maps correction structure to the pending Limit price/anchor |
| B3 SL | SOURCE-UNRESOLVED-V1 | Authoritative rule/example uniquely defining structural invalidation boundary and wick/body treatment |
| B4 Trigger | SOURCE-UNRESOLVED-V1 | Authoritative rule defining accepted 1/2/3-candle/key-bar trigger conditions, timing and precedence |
| B5 AB=CD | SOURCE-UNRESOLVED-V1 | Authoritative definition of A/B/C/D anchors and equality/tolerance semantics |
| B6 Leg2/TP | SOURCE-UNRESOLVED-V1 | Authoritative rule defining Leg2 projection from Leg1 and executable TP1/TP2 placement |

## Additional unresolved item

Pending-order delete/replace behavior remains qualitative: the source supports replacement when the structural/risk relationship changes materially, but no deterministic numeric threshold is source-confirmed.

## What is frozen semantically

1. Context/range is relevant.
2. Directional structure uses Higher Lows / Lower Highs as the directional mirror.
3. Valid breakout includes follow-through and is associated with P-Gap.
4. P-Gap is first-class source terminology and is not replaced by generic three-candle FVG.
5. Correction follows the first directional leg/spike structure.
6. Entry is a pending Limit; market close-reclaim is not an equivalent implementation.
7. Entry and structural invalidation are distinct concepts.
8. Risk percentage controls sizing, not the structural definition of the stop.
9. Leg1 → Leg2 continuation and AB=CD magnitude relationship are source-confirmed.
10. TP1 is preferred in the demonstrated practical discussion; TP2 is a larger research/backtest candidate.
11. 2X is source-confirmed as a concept, while its exact executable formula remains unresolved.
12. Bearish directional mirroring is semantically supported; exact bearish OHLC geometry remains unresolved.

## Frozen-geometry entry checklist

Frozen Geometry may open only when every production-critical item below is source-unique or explicitly versioned as a source-defined alternative:

- [ ] P-Gap exact candle indexing and OHLC formula
- [ ] Breakout/follow-through timing relative to P-Gap
- [ ] Entry structural anchor and exact price mapping
- [ ] Structural SL/invalidation boundary and OHLC treatment
- [ ] Trigger acceptance, timing and precedence
- [ ] Leg1 measurement anchors
- [ ] AB=CD A/B/C/D anchors and tolerance
- [ ] Leg2 projection and TP1/TP2 executable placement
- [ ] Pending-order replacement/cancellation rule
- [ ] Bearish mirror geometry
- [ ] Intrabar execution semantics for any remaining ambiguity
- [ ] Provenance from source frame/text to deterministic rule
- [ ] Synthetic fixture coverage for every frozen rule
- [ ] Independent review that no heuristic or performance-derived choice entered the canonical spec

## Production boundary

Until the checklist passes, production Strategy A BUY/SELL detection is prohibited. Candidate geometry may exist only in explicitly research-labeled modules and must return UNRESOLVED where source uniqueness is absent.

## Next gate

Proceed with strategy-neutral data/execution readiness and source acquisition only. Reopen Frozen Geometry immediately if new authoritative source evidence becomes available that can satisfy one or more blocker criteria.
