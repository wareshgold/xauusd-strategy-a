# SP2L Batch 8 — Source Evidence Record — 2026-09-16

## Scope

Source-first discrimination for F8 (swing selection), F9 (entry vs leg-2 start), F10 (invalidation/SL), and F11 (pending-order replacement). No profitability-based geometry selection and no production rule promotion.

## Evidence reviewed

1. Primary-author page by Mohammad Ali Poursamadi describes SP2L as Spike → Second Leg → Entry Level. It states that in an uptrend the corrective candle waits to reach the low of the previous candle, while in a downtrend it waits to reach the high of the previous candle. It then states that once the Second Leg is triggered, entry is taken in the spike direction. The same page states SL is placed behind the candle from which the spike originated. Source: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

2. TradingFinder's TradingView description reports HLs in bullish spikes and LHs in bearish spikes as potential entry levels, with entry activated when price returns to retest that level. It also describes SL around the candle where the spike originated. This is secondary implementation evidence and is not treated as primary-source confirmation. Source: https://www.tradingview.com/script/Qiv9aTi0-SP2L-Pour-Samadi-Indicator-TradingFinder-Spike-2-Legs-PA/

## Findings

### F8 — Swing selection
Status: **CONCEPT PARTIALLY DISCRIMINATED / EXACT SELECTION ALGORITHM UNRESOLVED**.

The secondary description explicitly uses HL/LH structures and treats each as a potential entry level. The primary-author page describes the corrective candle reaching the previous candle's low/high, but does not specify a deterministic algorithm for choosing the "first important" swing versus an evolving/latest swing when multiple candidates exist. Therefore F8 remains unresolved at algorithm level.

### F9 — Entry vs Leg-2 start
Status: **SOURCE-CONFIRMED SEPARATION / EXACT ENTRY ACTIVATION SEMANTICS PARTIALLY RESOLVED**.

The primary-author page distinguishes the Second Leg trigger from the subsequent Entry Level and states that entry follows once the Second Leg is triggered. This supports retaining separate leg-2 trigger/start and entry concepts. It does not provide a complete executable timestamp/price rule for every candle-path case. No Entry=C assumption is introduced.

### F10 — Invalidation vs Stop-Loss
Status: **SOURCE-CONFIRMED ORIGIN REFERENCE / EXACT PRICE SEMANTICS UNRESOLVED**.

The primary-author page explicitly places SL behind the candle from which the spike originated. This discriminates against treating an arbitrary later swing as the canonical SL reference. However, the exact wick/body boundary, buffer, and invalidation timing are not specified in the accessible primary text. Therefore exact SL geometry remains unresolved.

### F11 — Pending-order replacement
Status: **UNRESOLVED**.

The reviewed source material establishes entry/retest concepts but does not provide a deterministic rule for when an unfilled pending order is replaced, refreshed, cancelled, or retained after a new HL/LH or new setup appears. No replacement threshold or state machine is introduced.

## Gate consequence

F9 is now source-confirmed at the concept/separation level, and F10 has a source-confirmed origin reference. F8 and F11 remain unresolved at executable-rule level. Frozen Geometry remains BLOCKED because unresolved canonical geometry still exists, and no profitability test is permitted to resolve it.

## Non-negotiables preserved

- No invented swing-selection algorithm.
- No invented Entry=C rule.
- No invented SL buffer, wick/body convention, or replacement threshold.
- No profitability-based geometry selection.
- No production BUY/SELL generation.
- The 125R observation remains untouched.
