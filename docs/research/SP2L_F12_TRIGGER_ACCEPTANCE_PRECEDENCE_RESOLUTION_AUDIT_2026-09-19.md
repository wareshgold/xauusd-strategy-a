# SP2L F12 — Trigger Acceptance / Precedence Resolution Audit — 2026-09-19

## Purpose

Resolve F12 using only archived source evidence. The target is not to invent a single trigger rule, but to determine whether the source uniquely specifies trigger acceptance, activation, and precedence among the described variants.

## Evidence reviewed

- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `docs/research/SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `docs/research/SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`
- Existing F11/F14/P-Gap source-resolution register.

## 1. Second-Leg trigger concept

The author-associated source gives a directional trigger concept:

- bullish/upward case: wait for the corrective candle to reach the low of the previous candle;
- bearish/downward case: wait for the corrective candle to reach the high of the previous candle;
- after the Second Leg is triggered, entry is taken in the spike direction.

**Status:** SOURCE-CONFIRMED at the conceptual trigger level.

This is materially stronger than an assumption based only on chart indexing.

## 2. The source also describes a trigger family

The primary transcript describes structures involving one, two, or three candles and a Limit-entry sequence. It also references confirmation variants involving a bar signal and a key-bar signal.

This means the source does not establish one universal executable trigger algorithm applicable to every teaching example.

**Status:** Trigger family = SOURCE-SUPPORTED.

## 3. What is actually determined

The strongest source-aligned sequence currently supportable is:

`valid Spike / P-Gap context`
→ `correction / Second-Leg structure`
→ `corrective price reaches the referenced previous-candle level`
→ `Second Leg is triggered`
→ `entry in spike direction`

This sequence is source-aligned.

## 4. What is NOT uniquely determined

The archived source does not uniquely resolve:

### A. Touch semantics

“Reach” does not uniquely establish whether the trigger occurs on:

- exact price touch;
- wick penetration;
- body penetration;
- candle close beyond/at the level.

### B. Candle indexing

The source describes a previous-candle reference but does not provide a source-complete universal index mapping that resolves every 1/2/3-candle construction.

### C. Trigger precedence

The source mentions multiple forms/variants, including 1/2/3-candle structures and bar/key-bar confirmations.

It does not establish a deterministic precedence rule such as:

`3-candle > 2-candle > 1-candle`

or

`Key-Bar > Bar > direct level touch`.

No such ordering is promoted.

### D. Limit order versus confirmation trigger

The source permits a predefined Limit order inside the initial three-candle structure without waiting for another candle.

Therefore the existence of a later trigger/confirmation example does not prove that every setup must wait for a later candle.

The source supports multiple execution presentations, but does not provide a universal classifier selecting one presentation.

### E. Fill / activation semantics

The source does not specify whether a pending Limit is considered activated at broker touch, Bid/Ask crossing, candle close, or another platform event.

## 5. Relationship to P-Gap

The source explicitly associates a valid breakout with P-Gap and distinguishes P-Gap from E-Gap.

However, because the exact P-Gap formula itself remains unresolved, F12 cannot use a guessed P-Gap implementation as a deterministic prerequisite.

Thus:

- P-Gap validity concept: SOURCE-CONFIRMED.
- Exact P-Gap executable predicate: UNRESOLVED.
- Trigger sequence after valid P-Gap: SOURCE-CONFIRMED at concept level.
- Full executable classifier: UNRESOLVED.

## 6. Deterministic acceptance test

| F12 requirement | Source status |
|---|---|
| Second-Leg trigger is part of SP2L | SOURCE-CONFIRMED |
| Bullish trigger references previous-candle low | SOURCE-CONFIRMED |
| Bearish trigger references previous-candle high | SOURCE-CONFIRMED |
| Entry follows trigger in spike direction | SOURCE-CONFIRMED |
| 1/2/3-candle structures are source-described | SOURCE-CONFIRMED |
| Bar/Key-Bar confirmation variants are source-described | SOURCE-CONFIRMED |
| Exact candle-index classifier | UNRESOLVED |
| Exact touch/wick/close activation | UNRESOLVED |
| Variant precedence | UNRESOLVED |
| Universal pending-order vs later-confirmation choice | UNRESOLVED |
| Broker Bid/Ask/fill semantics | UNRESOLVED |

## Deliberate non-inferences

This audit does NOT promote:

- a fixed 3-candle trigger;
- a fixed 1-candle trigger;
- Bar or Key-Bar as mandatory;
- a precedence hierarchy among trigger variants;
- candle-close confirmation;
- wick-touch confirmation;
- a guessed candle index;
- a broker-specific fill event;
- a guessed P-Gap formula.

Backtest performance is not used to choose among these interpretations.

## F12 result

**PARTIAL / UNRESOLVED**

The source now supports a deterministic **conceptual trigger chain**, including the directional previous-candle reference, but it does not uniquely specify the complete executable acceptance classifier or precedence among trigger variants.

## Gate impact

- F12: **PARTIAL / UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- No canonical trigger implementation is promoted.
- No new backtest/optimization is justified.
- Live trading remains disabled.

## Next priority

The highest-severity unresolved geometry remains **P-Gap exact OHLC construction**, because P-Gap is explicitly tied to valid breakout qualification and is a prerequisite to a complete source-frozen setup detector.

Next source-resolution work should therefore focus on **P-Gap formula/candle-boundary discrimination**, not parameter tuning.
