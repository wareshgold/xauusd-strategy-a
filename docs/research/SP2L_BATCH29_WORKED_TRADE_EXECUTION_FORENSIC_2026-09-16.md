# SP2L Batch 29 — Worked-Trade Execution Forensic Pass — 2026-09-16

## Purpose

Inspect the worked-trade/account sequence in the primary SP2L training artifact at approximately **65:00–67:30** for source evidence about execution, SL/TP attachment, multiple orders, and fill semantics.

Source meaning remains higher priority than implementation convenience or backtest performance.

## Primary-artifact observations

### ~65:00–66:00 — worked trade sequence

The artifact shows worked XAUUSD trade/account screenshots with multiple SELL positions and associated chart levels. The screenshots demonstrate that the teaching sequence includes concrete order examples rather than only schematic geometry.

The visible records include sell-side prices and corresponding SL/TP values. This is evidence that entry, stop and target values are operationally discussed in the worked example.

### ~66:30 — readable worked-order table

One readable table contains examples including approximately:

- SELL price **3229.08**, S/L **3237.73**, T/P **3213.37** (another frame renders the target as 3213.30);
- SELL price **3223.84**, S/L **3235.50**, T/P **3213.37**;
- SELL price **3228.88**, S/L **3235.50**, T/P **3213.37**;
- additional SELL examples around **3232.41** with S/L **3237.80** and no visible TP value.

These are observations from the worked screenshots. Small differences between frames are retained rather than normalized into a rule.

### Multiple orders

The worked example visibly contains multiple sell orders with different entry prices and, in some cases, different stop prices while sharing a target region.

This confirms that the teaching artifact can contain multiple simultaneously represented positions/orders.

It does **not** establish a canonical rule for:

- whether these are sequential entries, multiple fills, manual scaling, or separate demonstrations;
- how many positions are allowed;
- how pending orders interact;
- precedence between candidate levels;
- sizing or allocation between positions.

### Apparent execution outcome

The screenshots include execution-price/current-price fields and completed-looking TP/SL associations in the account table. This provides worked-example evidence that orders can reach an executed state and have attached management levels.

However, a screenshot/table does not expose the event-level condition that caused an order to fill. Therefore it cannot source-completely establish whether fill occurs on touch, intrabar penetration, bar close, broker execution, or another mechanism.

## F9 result — activation/fill semantics

The worked trade sequence strengthens the fact that **an entry can become an executed position**, but it does not reveal the deterministic event that transitions a pending Buy/Sell Limit into a fill.

Therefore:

**F9 = EXECUTED-TRADE EXAMPLE CONFIRMED / EXACT ACTIVATION AND FILL SEMANTICS UNRESOLVED.**

## F11 result — order lifecycle

Multiple executed orders and management fields are visible, but the screenshots do not provide a complete event sequence for `created → active → filled → deleted/replaced/expired`.

Therefore:

**F11 = MULTIPLE-ORDER EXECUTION EVIDENCE STRENGTHENED / LIFECYCLE TRANSITIONS AND PRECEDENCE UNRESOLVED.**

## F10 result — SL semantics

The worked examples visibly associate individual entries with SL values. This strengthens that stop placement is part of the operational trade example.

It does not establish whether the stop is based on the spike-origin candle high/low, structural invalidation, fixed risk distance, or another exact boundary rule.

Therefore:

**F10 = ENTRY+SL ASSOCIATION CONFIRMED / EXACT SL CONSTRUCTION AND INVALIDATION EVENT UNRESOLVED.**

## F13 result — 2X

The account/chart sequence includes `2x` annotations in the broader worked-trade material. This supports the existence of a distinct 2X concept in execution teaching.

The screenshots do not provide enough information to derive a canonical numerical 2X formula, sizing rule, or fill semantics. The visually suggested position of a 2X level must not be converted into a 50% formula without source evidence.

Therefore:

**F13 = EXECUTION-LEVEL 2X CONCEPT STRENGTHENED / EXACT PRICE, SIZING AND EXECUTION FORMULA UNRESOLVED.**

## What this pass does NOT authorize

Do not infer from the worked screenshots:

- a broker-style fill rule;
- touch/intrabar/bar-close activation;
- a canonical Buy Limit or Sell Limit price formula;
- a maximum number of simultaneous positions;
- position sizing or scaling formula;
- 2X = 50% of Entry-to-SL;
- canonical SL boundary;
- TP1/TP2 execution semantics;
- pending-order expiry/replacement/deletion rules.

## Gate impact

- Source Resolution: **PARTIAL PASS — worked execution evidence strengthened**
- F9: **executed-trade example confirmed / fill semantics unresolved**
- F10: **entry+SL association confirmed / exact construction unresolved**
- F11: **multiple-order evidence strengthened / lifecycle unresolved**
- F13: **2X execution concept strengthened / exact formula unresolved**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

No production implementation, canonical geometry, backtest variant, or validation dataset was changed.
