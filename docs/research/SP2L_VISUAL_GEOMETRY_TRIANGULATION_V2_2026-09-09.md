# SP2L Visual Geometry Triangulation V2 — 2026-09-09

## Source frames inspected

Directly inspected source-video frames around:
- 36:50–37:10: `AB=CD` and `Valid BO = P-Gap` slide.
- 38:54–39:26: bullish sequence with explicit `Buy Limit`, Low markers and the structural lower boundary.
- 39:48–40:16: pending-order deletion/replacement discussion.

## Finding 1 — AB=CD is not a generic Fibonacci recipe

The slide writes `AB=CD` directly above the source candle sequence. The transcript at 36:31–36:46 says the classical internet treatment takes A/B/C and applies Fibonacci, while this strategy works down at candle level.

Decision: source confirms an equal-leg relationship but does not yet expose a unique algorithm for selecting the exact candle OHLC anchors A, B, C and D.

## Finding 2 — Entry level is visually tied to the correction structure

The 38:54 frame shows a bullish candle sequence with a horizontal execution level and explicit handwritten `Buy Limit`. The source transcript immediately around 38:38–39:26 says correction means moving below the first Low and that a manual or pre-set Limit can be placed there.

The visual is sufficient to reject:
- market-close reclaim as the canonical execution event;
- a requirement to wait for an extra confirmation candle.

The visual is not sufficient to freeze:
- exact price equality to a particular wick/body extreme;
- tick buffer;
- spread adjustment;
- a universal candle index across all Spike variants.

Decision: pending-limit semantics are frozen; exact executable price remains blocked.

## Finding 3 — Structural invalidation is separate from entry

The diagram contains a lower structural boundary beneath the entry structure. The transcript at 39:26 says a return to the illustrated level invalidates the scenario and explains that this makes the original scenario no longer valid.

Decision: entry and SL/invalidation must remain separate fields. Do not infer `SL = Entry - fixed distance` or another numerical relation without source evidence.

## Finding 4 — P-Gap is breakout validation, not a universal three-candle formula

The 36:50-area slide explicitly states `Valid BO = P-Gap`. The 34:55–36:05 transcript describes three accepted Spike constructions with different temporal orderings of higher lows, gap, and the next bearish candle.

Decision: a production detector cannot currently use a single fixed candle index or generic three-candle FVG formula. The research engine must represent P-Gap as a source-variant state until the boundary rule is resolved.

## Finding 5 — 2X remains a separate management event

The transcript describes 2X as a second position and separately describes TP1/TP2. The source examples therefore support a multi-event execution model rather than one monolithic entry/target rule.

Decision: base SP2L signal and optional 2X management remain independently versioned.

## Resolution matrix

| Question | Result |
|---|---|
| Is SP2L = Spike → 2Leg? | YES |
| Is AB=CD source-confirmed? | YES |
| Is valid breakout associated with P-Gap? | YES |
| Is P-Gap generic FVG? | NO — not source-confirmed |
| Is correction tied to the first/relevant Low/High? | YES, strong |
| Is execution a pending Limit? | YES |
| Can execution be replaced by market close-reclaim? | NO |
| Exact Limit price | UNRESOLVED |
| Exact SL price | UNRESOLVED |
| Exact A/B/C/D anchors | UNRESOLVED |
| AB=CD tolerance | UNRESOLVED |
| 2X exists | YES |
| 2X exact formula | UNRESOLVED |

## Gate decision

**SOURCE RESOLUTION: ADVANCED BUT NOT COMPLETE**

The source now supports a strong semantic contract and a narrow execution contract. Geometry Freeze remains blocked only on the exact executable mappings required for a reproducible OHLC engine: P-Gap boundaries, exact Entry price, exact SL convention, A/B/C/D anchors, and any required AB=CD tolerance.

No historical optimization is authorized to decide these items.

**Next research operation:** construct source-shaped synthetic candles for the seven discrimination fixtures, then compare each candidate against the source frames/transcript. Only candidates surviving source evidence may enter a frozen geometry specification.
