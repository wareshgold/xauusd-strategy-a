# SP2L Batch 7 — Source Evidence Record — F8–F11 — 2026-09-16

## Scope

Source-first discrimination for F8 (swing selection), F9 (Entry vs Leg-2 start), F10 (structural invalidation vs risk stop), and F11 (pending-order replacement/update). No profitability-based selection and no geometry freeze are made by this record.

## Evidence reviewed

1. Mohammad Ali Poursamadi SP2L overview (public author-attributed page) describes the Second Leg as the corrective move and states that, in an uptrend, the corrective candle reaches the low of the previous candle, while in a downtrend it reaches the high of the previous candle. It separately states that the SL is placed behind the candle from which the spike originated. The page also describes a secondary entry at 50% of the distance from entry to stop-loss.

2. TradingFinder's public SP2L indicator description states that bullish candles form Higher Lows and each HL is a potential Buy Entry, while bearish candles form Lower Highs and each LH is a potential Sell Entry; the entry activates when price returns to retest that level. It describes SL below/above the candle where the spike originated. This is secondary evidence and does not uniquely specify a deterministic swing-selection algorithm.

3. A public TradingFinder video-summary page reports that if the entry level moves due to subsequent higher highs/lows, the entry is adjusted accordingly, and that a secondary 50% retracement entry may exist. This is secondary indexed evidence; it is not sufficient by itself to establish an exact replacement threshold or state machine.

## Findings

### F8 — Swing selection / first important Low/High
Status: **CONCEPT DISCRIMINATED / EXACT SWING-SELECTION ALGORITHM UNRESOLVED**.

Evidence supports using prior/formed HL levels for bullish entries and LH levels for bearish entries, and the author-attributed overview explicitly references the previous candle's low/high in the Second Leg. However, the accessible source text does not uniquely define whether the canonical algorithm selects the first qualifying swing, latest qualifying swing, evolving swing, or another exact rule. No canonical swing-selection algorithm is promoted.

### F9 — Entry vs Start-of-Leg-2
Status: **SEPARATION SUPPORTED / EXACT ENTRY TIMING UNRESOLVED**.

The source material distinguishes the corrective/Second-Leg event from the later entry activation/retest concept. Therefore Entry and the start of Leg 2 must not be collapsed into the same field. The exact executable trigger timing, including whether entry is at a retest, breakout, or another condition in the canonical source, remains unresolved from accessible primary evidence.

### F10 — Structural invalidation vs risk-budget stop
Status: **SOURCE DIRECTION DISCRIMINATED / EXACT SL PRICE SEMANTICS UNRESOLVED**.

The author-attributed overview and secondary descriptions consistently place the SL behind the candle/origin from which the spike started. This supports an origin-based structural reference rather than an invented numeric risk-budget stop. However, the exact OHLC point, wick/body treatment, buffer, and any threshold semantics are not sufficiently specified. No exact SL formula is promoted.

### F11 — Pending-order replacement / update
Status: **UPDATE CONCEPT SUPPORTED BY SECONDARY EVIDENCE / EXACT REPLACEMENT RULE UNRESOLVED**.

Secondary indexed material reports that the entry level can be adjusted when subsequent higher highs/lows move the level. This supports the existence of an update/replacement concept, but it does not establish the exact replacement trigger, cancellation semantics, ordering, or threshold. No numeric replacement rule or state machine is promoted.

## Gate consequence

F8–F11 do not provide enough uniquely executable source evidence to freeze geometry. F9 can now be treated as a source-supported field separation. F10 has a source-supported origin-based direction but remains numerically unresolved. F11 has secondary support for update behavior but remains operationally unresolved. F8 remains algorithmically unresolved.

Source Resolution: PARTIAL PASS
Frozen Geometry: BLOCKED
Untouched Validation: LOCKED
Robustness/Stability: LOCKED
Fresh Holdout: LOCKED
Production: OFF

## Non-negotiables preserved

- No profitability-based geometry selection.
- No invented P-Gap, AB=CD, 2X, trigger, swing, SL, or order-replacement formulas.
- No production BUY/SELL generation.
- The 125R observation remains untouched.
