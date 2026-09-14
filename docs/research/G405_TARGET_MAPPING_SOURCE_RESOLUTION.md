# G405 — TP1/TP2 Target Mapping Source Resolution

## Purpose

G405 addresses the seventh source-critical blocker recorded by G400: the mapping from the source-described target structure (including TP1/TP2 where applicable) to executable target prices.

## Source-first constraint

The source confirms second-leg continuation and an AB=CD relationship, but executable target geometry must not be inferred from common trading conventions or backtest performance. In particular, G405 does not assume that an AB=CD projection is the executable take-profit, that TP1/TP2 are fixed risk multiples, or that a geometric endpoint equals an executable order price.

## Research dimensions

G405 keeps the following dimensions explicitly unresolved:

1. target reference: second-leg endpoint vs AB=CD projected endpoint vs another source-defined structural reference;
2. target level: single endpoint vs source-defined TP1/TP2 structure;
3. target count: one vs two executable targets;
4. price field: endpoint field vs source-defined candle high/low/body field;
5. leg relation: explicit AB=CD translation vs approximate Leg2≈Leg1 interpretation;
6. executable mapping: geometric target equal to executable TP vs source-defined offset/mapping.

## Minimal-pair discrimination

The fixture set must distinguish:

- second-leg endpoint from AB=CD projection;
- single-target from TP1/TP2 mapping;
- geometric projection from risk-multiple targets;
- high/low from body price fields;
- exact AB=CD from approximate leg equality;
- geometric target from executable take-profit;
- bullish from bearish mirror behavior.

These are research discriminators only. No candidate is canonical.

## Gate status

**UNRESOLVED / RESEARCH-ONLY**

`G405_STATUS` exposes null canonical fields. This is intentional and fail-closed.

G405 does not clear G400 and does not authorize historical optimization, live signals, or production deployment.

## Promotion rule

Only authoritative source wording, source visual evidence, or a traceable source-derived auditable artifact can resolve a target-mapping dimension. Common price-action conventions, implementation convenience, and profitable backtests are insufficient evidence.
