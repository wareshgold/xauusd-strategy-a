# SP2L P0 Counterexample Discrimination — 2026-09-21

## Result
14 P0 counterexamples were classified without using performance to select geometry.

### F08 Swing
- Structural turn vs fixed pivot: **source discriminates the meaning** toward structural turning areas, but not a deterministic pivot algorithm.
- Wick vs body: **not source-discriminated**.
- Asymmetric/fixed window: **not source-discriminated**.

### F10 Stop
- Spike-origin mapping: **source discriminates the semantic owner** (the candle from which the spike originated), but exact multi-candle mapping remains unresolved.
- Wick vs body: **not source-discriminated**.
- Buffer: **not source-discriminated**.
- Touch vs breach vs close: **not source-discriminated**.

## Promotion decision
No counterexample permits executable canonical promotion. The useful reduction is semantic only:
- F08 should not be modeled as a fixed pivot by assumption.
- F10 should remain tied to spike-origin semantics, without inventing the OHLC field or invalidation event.

**P0 remains unresolved. Frozen Geometry remains BLOCKED.**
