# SP2L Batch 27 — Primary Trigger / Order-Lifecycle Forensic Pass — 2026-09-16

## Purpose

Inspect the primary SP2L training artifact around the dense teaching sequence at approximately **38:00–41:00** to determine whether the source is sufficient to resolve F12 (trigger taxonomy), F9/F10 (activation/price semantics), or F11 (pending-order lifecycle).

Source meaning remains higher priority than implementation convenience or backtest performance.

## Primary-artifact sequence

### ~38:00 — breakout validation

The primary artifact explicitly displays:

`Valid BO = P-Gap`

This confirms that P-Gap is directly associated with validity of the breakout concept in this teaching sequence.

It does not expose the exact candle-close/touch/intrabar rule or a complete trigger taxonomy.

### ~38:30 — multiple structural reference points

Several local lower points are visibly marked on the bullish sequence.

This strengthens the observation that multiple candidate structural points may be visually relevant before an order level is selected.

It does not identify a deterministic first-important-low/latest-low selection algorithm.

### ~39:00–39:15 — BO and Buy Limit introduced in the same sequence

The slide shows a bullish candle sequence with multiple horizontal reference levels. `BO` is handwritten beside the sequence and `Buy Limit` is introduced as an order concept.

The evidence supports the teaching sequence:

**breakout / BO → Buy Limit**

but does not establish whether the BO is a bar-close event, a wick break, a P-Gap classification, or another confirmation condition.

### ~39:30–39:55 — explicit Buy Limit level

A horizontal level is explicitly labeled `Buy Limit` and remains associated with the candle sequence. The line is drawn across the chart rather than tied to an explicitly stated OHLC field in the visible artifact.

Important negative finding: the visible geometry does **not** provide enough source evidence to prove that the Buy Limit equals:

- a specific marked low;
- candle open/close/high/low;
- the breakout level itself;
- a retracement percentage;
- a P-Gap boundary;
- or another deterministic formula.

Therefore exact entry/limit price construction remains unresolved.

### ~40:00 — order line persists

The horizontal order line remains present as the sequence advances. This is direct evidence that a pending-order level is maintained after it is drawn.

It does not establish a timeout or exact activation window.

### ~40:05–40:20 — `delete` annotation

The next frames explicitly contain the handwritten `delete` annotation associated with the order-management sequence. The order line is still visible in the teaching diagram.

This establishes that deletion/cancellation of the pending order is part of the taught management behavior.

It does **not** establish the deletion condition. The source does not visibly specify whether deletion occurs because of:

- a new structural level;
- invalidation;
- a later breakout;
- time expiry;
- a missed fill;
- a replacement/refresh event;
- manual discretion;
- or another condition.

Accordingly, F11 remains unresolved.

### ~40:25–41:00 — money-management annotations

The later frames add `money` and numbered management annotations while continuing to show the order-management diagram. These frames do not expose a deterministic pending-order replacement or fill rule.

No canonical sizing or execution semantics are inferred from these annotations.

## F12 trigger taxonomy result

The primary artifact now provides a strong sequence-level observation:

**Valid BO / P-Gap → Buy Limit**

However, the artifact still does not uniquely distinguish among candidate trigger semantics such as touch, wick break, close confirmation, following-bar confirmation, or multi-candle confirmation.

Therefore:

**F12 = PRIMARY-ARTIFACT TRIGGER CONCEPT CONFIRMED / EXACT TRIGGER TAXONOMY UNRESOLVED.**

## F9 entry/activation result

The artifact clearly distinguishes a pending `Buy Limit` level from the later order-management sequence. This supports the existence of a pending entry concept.

It does not reveal the exact activation/fill condition or prove the Buy Limit price formula.

Therefore:

**F9 = PRIMARY-ARTIFACT PENDING-ENTRY CONCEPT CONFIRMED / ACTIVATION SEMANTICS UNRESOLVED.**

## F10 price/invalidation result

The diagram visually contains a separate lower risk/SL reference in the same teaching sequence, but the visible artifact does not provide a source-complete rule for the exact SL boundary or invalidation event.

Therefore:

**F10 = SOURCE-CONFIRMED ORIGIN/RISK-SEPARATION CONCEPT / EXACT PRICE AND INVALIDATION SEMANTICS UNRESOLVED.**

## F11 order lifecycle result

`Buy Limit` and `delete` are directly visible in the same primary teaching sequence.

This confirms that order placement and deletion are taught behaviors. It does not establish the state machine required for deterministic replay:

`created → active → filled / deleted / replaced / expired`

No replacement, cancellation trigger, expiry interval, or multiple-order precedence rule is source-complete in the inspected frames.

Therefore:

**F11 = PRIMARY-ARTIFACT ORDER-LIFECYCLE CONCEPT CONFIRMED / DELETE CONDITION AND REPLACEMENT RULE UNRESOLVED.**

## What this pass does NOT authorize

Do not promote any of the following to canonical geometry:

- Buy Limit = marked low;
- Buy Limit = breakout level;
- Buy Limit = P-Gap boundary;
- trigger = candle close;
- trigger = wick touch/break;
- trigger = next-candle confirmation;
- delete = structural invalidation;
- delete = timeout;
- delete = replacement by latest level;
- any specific fill semantics.

Backtest performance must not be used to select among these interpretations.

## Gate impact

- Source Resolution: **PARTIAL PASS — trigger/order-management evidence strengthened**
- F12: **concept confirmed / taxonomy unresolved**
- F9: **pending-entry concept confirmed / activation unresolved**
- F10: **price/invalidation unresolved**
- F11: **order lifecycle concept confirmed / deletion/replacement unresolved**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

No production implementation or backtest variant was changed.
