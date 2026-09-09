# SP2L G38 — Targeted Frame Annotation

Date: 2026-09-09

## Purpose

Use the highest-information source frames to discriminate executable geometry without selecting an interpretation by profitability.

## Frame set

| Area | Source interval | Observation | Remaining ambiguity | Result |
|---|---|---|---|---|
| P-Gap | 34:10–35:35 | P-Gap is repeatedly associated with valid BO; more than one construction is demonstrated | exact OHLC boundaries, overlap rule, candle indexing | UNRESOLVED |
| AB=CD | 36:15–37:10 | Explicit AB=CD annotation; 1M/5M context shown | A/B/C/D OHLC anchor convention and tolerance | UNRESOLVED |
| Entry | 38:18–39:45 | Buy Limit is placed during correction; Entry is separate from SL and not simply the original Spike extreme | exact structural pivot and wick/body anchor | UNRESOLVED |
| Pending update | 39:26–40:16 | Pending order can be deleted/replaced when structure materially changes risk relationship | exact quantitative replacement threshold | UNRESOLVED |
| TP / 2X | 41:30–42:37 | BUY/SL/2X/TP1/TP2 concepts are explicitly annotated | exact 2X formula and executable TP projection | UNRESOLVED |
| Trigger / Leg2 | 53:16–54:36 | one/two/three candle trigger family; pullback toward Leg2 start; Buy Limit can create another opportunity | trigger acceptance/timing and Leg2 projection | UNRESOLVED |
| Bearish | 55:00–57:30 | direct bearish examples show SL above and Entry below in continuation structures | exact bearish OHLC anchors | SEMANTIC PASS / GEOMETRY PARTIAL |

## High-confidence negative findings

1. Generic three-candle FVG is not a source-approved substitute for P-Gap.
2. Market close-reclaim is not equivalent to the source's pending-limit mechanism.
3. Risk percentage is a sizing input, not the definition of structural invalidation.
4. No wick/body/tolerance/buffer/replacement threshold is promoted without explicit source evidence.

## Source visual evidence

The 45:00–55:00 contact sheet reinforces the separation of Entry, SL, 2X and TP concepts and shows multiple live-chart examples, but the annotations do not expose a unique OHLC formula for the unresolved blockers.

## Decision

**G38 result: SOURCE-RESOLUTION PARTIAL PASS; FROZEN GEOMETRY BLOCKED.**

The frame evidence reduces semantic uncertainty but does not establish source-unique executable geometry. The correct next move is not optimization. Continue targeted extraction only where a specific candidate can be falsified, otherwise proceed with strategy-neutral infrastructure and preserve the blockers explicitly.
