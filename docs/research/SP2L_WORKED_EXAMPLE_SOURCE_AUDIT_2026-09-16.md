# SP2L Worked-Example Source Audit — 2026-09-16

## Purpose

This audit isolates what the recovered primary transcript actually determines from the worked examples. It is a source-resolution artifact only. It does not freeze executable geometry.

## Evidence hierarchy

`Primary transcript meaning > visual interpretation > discrimination fixtures > backtest performance`.

No implementation parameter is promoted unless the source uniquely determines it.

## Worked example A — F09/F10/F11: bullish correction and pending Buy Limit

### Source window

- 38:18–38:38: bullish structure is described as successive higher lows; the next candle begins correction by moving below the first low.
- 38:53–39:11: breakout/follow-through structure is described and the Buy Limit can be placed within the initial three-candle structure.
- 39:26: return to the referenced level invalidates the scenario.
- 39:48–40:07: after a new candle, the pending order may be deleted/replaced; if the new distance to SL is materially large, a new order/new sizing is used, while a smaller distance is retained/moved upward.

### Deterministic conclusions

1. Entry is a pending Limit concept in the demonstrated sequence.
2. Entry and structural invalidation are distinct.
3. The actionable reference can evolve as the structure develops.
4. Refresh/replacement behavior is conditional on changed stop distance.

### Still not uniquely determined

- Exact Entry OHLC point.
- Exact SL OHLC point.
- Wick/body semantics.
- Exact numerical definition of “large” versus “not large” distance.
- Exact fill semantics.

### Canonical status

`UNRESOLVED` for exact executable geometry.

## Worked example B — F13: 2X

### Source window

- 22:43: teacher states that when price reaches half the target, he enters the 2X position.
- 38:05: first pullback entry is followed by a later 2X entry.
- 41:26–41:53: 2X is optional; later entry has a larger reward multiple over its own entry-to-target distance. Equal nominal dollar risk is used in the example.
- 57:14: another example reports 2X alongside a 4% gain versus 2% risk.

### Deterministic conclusions

1. 2X is an optional second-position concept.
2. The source explicitly associates one demonstrated 2X entry with approximately half-target progression.
3. The later entry can have a different R outcome because its entry-to-target distance differs.

### Still not uniquely determined

- Universal price equation for the 2X entry.
- Whether half-target is always measured from initial Entry, a structural anchor, or another source-defined reference.
- Universal sizing rule.
- Universal stop/fill semantics.

### Canonical status

`UNRESOLVED` for exact executable 2X geometry.

## Worked example C — F14: AB=CD / 2Leg

### Source window

- 36:15: SPIKE-2LEG is explicitly associated with the 2Leg / AB=CD concept.
- 36:59–37:08: after a Spike and correction, the expected second leg matches the first leg in magnitude; target is associated with completion of Leg 2.
- 37:57: the equal-size expectation is repeated.
- 1:02:41–1:03:19: a larger worked leg hierarchy contains an embedded 2Leg and distinguishes a larger Leg 1 / Leg 2 relationship from a nested internal 2Leg.

### Deterministic conclusions

1. Leg 2 is a continuation objective after correction.
2. The source expresses AB=CD through a Leg-2 magnitude relationship to Leg 1.
3. Leg hierarchy can be nested; an internal 2Leg does not automatically define the outer pair.

### Still not uniquely determined

- Exact A/B/C/D endpoints.
- Wick versus body versus structural-pivot measurement.
- Whether Entry is C.
- Numeric equality tolerance.
- Exact target-fill semantics.

### Canonical status

`UNRESOLVED` for exact AB=CD geometry.

## Worked example D — F12: trigger family

### Source window

- 33:37–33:51: three-candle trend construction is discussed without making four candles mandatory.
- 40:42–41:03: confirmation variants are discussed, including bar and key-bar.
- 53:16: one-, two-, and three-candle constructions are explicitly described as producing the Limit trigger.

### Deterministic conclusions

1. A three-candle-only canonical trigger is contradicted by the source.
2. The source contains a trigger family.
3. Bar/key-bar are source-described confirmation variants.

### Still not uniquely determined

- Classifier rules.
- Precedence when multiple variants coexist.
- Whether a specific variant is required for a specific Spike subtype.
- Exact acceptance/failure algorithm.

### Canonical status

`UNRESOLVED` for a single executable trigger classifier.

## Cross-example conclusion

The worked examples now provide enough evidence to freeze **source semantics**, but not enough to freeze the remaining exact executable geometry.

### Safe frozen semantic layer

- SP2L means Spike → 2Leg.
- Spike is read at candle level and includes directional structure, breakout/follow-through context.
- Correction is the entry phase.
- Pending Limit is part of the demonstrated execution model.
- Structural invalidation is separate from risk budget.
- Pending-order references may evolve as new candles form.
- 2X is an optional later position; half-target association is source-confirmed for a demonstrated example.
- Leg 2 is expected to match Leg 1 in magnitude in the demonstrated SP2L concept.
- Triggering is a family including 1/2/3-candle structures and bar/key-bar variants.

### Not frozen

- P-Gap equation.
- Exact Entry anchor.
- Exact SL anchor, wick/body semantics, and buffer.
- Refresh threshold.
- Trigger classifier/precedence.
- 2X universal formula/sizing/stop/fill.
- A/B/C/D anchors and AB=CD tolerance.
- Production BUY/SELL logic.

## Gate

Source Resolution: `PARTIAL — strengthened by worked-example audit`.

Frozen Geometry: `BLOCKED`.

Synthetic Fixtures: `ADVANCED / READY TO BE USED FOR ANY NEW SOURCE-DISCRIMINATED CLAIM`.

Untouched Validation: `LOCKED`.

Robustness/Stability: `LOCKED`.

Fresh Holdout: `LOCKED`.

Production: `OFF`.
