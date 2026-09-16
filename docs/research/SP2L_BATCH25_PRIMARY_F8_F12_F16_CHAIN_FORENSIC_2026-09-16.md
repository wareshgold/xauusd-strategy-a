# SP2L Batch 25 — Primary F8/F12/F16 Chain Forensic — 2026-09-16

## Purpose

Forensic pass over the primary SP2L training-video sequence to test whether the artifact uniquely defines the chain:

**structural level → valid BO / P-Gap → pending Buy Limit → execution**

and whether the adjacent Round Level teaching can be joined to that chain as an executable rule.

This is evidence work only. No canonical geometry or execution rule is selected.

## Primary-artifact observations

### F12 — Valid BO / P-Gap

Around frame **2280 (~38:00)** the primary slide explicitly states **“Valid BO = P-Gap”** beside a bullish candle sequence.

This confirms that Valid BO and P-Gap are taught as related concepts. The artifact does not expose a numeric P-Gap formula, minimum gap, wick/body convention, intrabar-vs-close rule, or a complete breakout-validation algorithm in this frame.

### F8 — Structural levels / local lows

Around frame **2310 (~38:30)** several local lower points are explicitly marked on the bullish sequence. Around frame **2340 (~39:00)** multiple horizontal reference levels are drawn and a **BO** annotation is present. A **Buy Limit** annotation is also introduced in the same teaching sequence.

This strengthens the observation that local structural points are used to derive horizontal reference/order levels. It does not identify which marked low is canonical, whether the first/lowest/latest level is selected, or whether every drawn level is an executable order level.

### F12/F11 — Buy Limit

Around frame **2370 (~39:30)** a horizontal level is explicitly labeled **“Buy Limit”** beneath/through the bullish continuation sequence. Around frame **2400 (~40:00)** the horizontal order line is extended while the candle sequence remains above it.

This is direct primary evidence for a pending Buy Limit teaching example. It does not establish the exact price source of the limit, the activation timestamp, touch-vs-break-vs-close semantics, fill semantics, cancellation/expiry, or replacement lifecycle.

### F11 — Order management

Around frames **2430–2460 (~40:30–41:00)** the teaching sequence contains order-management annotations including **delete**. This supports that pending-order lifecycle management is part of the source material.

It does not establish when an order must be deleted, whether it is replaced by a newer level, expiry duration, invalidation condition, or whether multiple pending orders may coexist.

### F16 — Round Level

Around frames **2640–2670 (~44:00–44:30)** the primary slide explicitly annotates **“Round level”** and shows price examples around the 3200/3250/3255 area. A following frame explicitly shows **“250 point”**, **“500 point”**, and **“1000”** annotations.

This confirms the teaching/context relevance of round-number levels and multiple spacing magnitudes. It does not identify the instrument-scale interpretation, rounding anchor, selected spacing, proximity threshold, or whether Round Level is a filter, score component, entry condition, or contextual annotation.

## Chain-identifiability result

The sequence provides strong evidence for the individual concepts:

1. Valid BO ↔ P-Gap is explicitly taught.
2. Local structural points and horizontal levels are used in the bullish example.
3. A horizontal level can be labeled Buy Limit.
4. Order management includes deletion.
5. Round Level is explicitly taught separately with multiple spacing examples.

However, the primary artifact does **not** uniquely establish that the Round Level is a required predecessor of the specific Buy Limit, nor does it uniquely map a particular local low to the Buy Limit price. It also does not expose the numeric P-Gap formula needed to deterministically connect breakout validation to order placement.

Therefore the complete chain remains:

**SOURCE-CONFIRMED CONCEPT CHAIN / EXACT EXECUTABLE MAPPING UNRESOLVED.**

## F8/F12/F16 non-canonical boundaries

The following remain intentionally unresolved:

- canonical swing/low selection;
- exact P-Gap formula and threshold;
- breakout confirmation timing and price semantics;
- exact Buy Limit price construction;
- relationship between Round Level and order level;
- pending-order activation/fill semantics;
- delete/cancel/replace/expiry rules;
- whether multiple candidate levels can coexist.

No backtest performance was used to select among these interpretations.

## Gate impact

**Source Resolution: PARTIAL PASS — individual concepts strengthened; executable chain remains unresolved.**

**Frozen Geometry: BLOCKED.**

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**
