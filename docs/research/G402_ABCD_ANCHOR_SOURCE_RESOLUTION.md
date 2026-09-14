# G402 — AB=CD Anchor Source Resolution

## Purpose

G402 is the next source-resolution gate after G401. It addresses the unresolved executable geometry behind the source-confirmed AB=CD relationship.

## Source-first boundary

The source supports an AB=CD relationship and the existence of Leg 1 / Leg 2 structure. It does **not** currently provide sufficient evidence in the frozen repository state to promote exact A, B, C, or D candle/price anchors, wick/body semantics, or an equality tolerance into canonical executable rules.

Therefore G402 deliberately keeps all competing interpretations research-only.

## Dimensions under resolution

1. A anchor
2. B anchor
3. C anchor
4. D anchor
5. price field (high/low/body/open/close or source-specific field)
6. wick/body semantics
7. AB=CD equality tolerance

The pending-order fill is retained as a negative-control hypothesis only; it is not assumed to be geometric C.

## Minimal-pair program

- ABCD-MP-01 — A-anchor-only divergence
- ABCD-MP-02 — B-anchor-only divergence
- ABCD-MP-03 — C-anchor vs fill divergence
- ABCD-MP-04 — wick vs body divergence
- ABCD-MP-05 — price-field divergence
- ABCD-MP-06 — D-endpoint divergence
- ABCD-MP-07 — tolerance divergence

These fixtures are intended to expose which source evidence actually distinguishes competing readings. They are not optimization parameters.

## Promotion rule

A candidate may become canonical only when authoritative source wording, source visual evidence, or a traceable source artifact resolves the dimension. Backtest profitability, implementation convenience, generic price-action convention, or a visually plausible fit is insufficient.

## Current status

**UNRESOLVED / SOURCE-EVIDENCE-REQUIRED**

G402 does not clear G400. It does not authorize executable AB=CD geometry, historical optimization, live signals, or production promotion.
