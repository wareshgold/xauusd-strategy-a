# SP2L P0 Source Discrimination — 2026-09-21

## F08 Swing
The source visual evidence supports the concept of a structural directional leg between visible turning areas. It does **not** establish a deterministic pivot algorithm, fixed window, wick/body endpoint, or numerical swing threshold. Therefore the structural interpretation is source-supported while the executable field remains unresolved.

## F10 Stop
The source meaning is explicit at the semantic level: the stop is placed behind the candle from which the spike originated. This does not by itself select wick vs body, add a numeric buffer, define the exact origin-candle mapping, or define touch/breach/close invalidation.

## P0 gate
F08 and F10 are now source-discriminated at the meaning level with explicit unresolved fields. No implementation choice is promoted and no backtest result may resolve the remaining fields.

**Result: P0 source discrimination PASS; Frozen Geometry remains BLOCKED.**


## Counterexample checkpoint — 2026-09-21
The 14 P0 counterexamples were classified. Source discriminates structural-turn meaning over an assumed fixed pivot for F08, and spike-origin semantic ownership for F10. Wick/body, buffer, invalidation event, exact pivot/window, and multi-candle origin mapping remain unresolved. No canonical promotion.
