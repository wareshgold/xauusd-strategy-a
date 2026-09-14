# G415 — Entry-Level Dynamic-Order Reconciliation

Date: 2026-09-14
Parent: G414
Status: SOURCE-CONSTRAINED / ENTRY GEOMETRY NOT FROZEN

## Purpose

Resolve the strongest remaining source evidence about Strategy A pending-limit placement and distinguish a fixed geometric entry level from the source's demonstrated dynamic order adjustment.

This is a source-resolution artifact only. It does not define an executable entry formula.

## Primary transcript evidence

At 38:38 the source describes the bullish correction as coming below the first low and says an order can be placed there manually or as a pre-defined limit. At 39:11 the speaker says the limit can be placed during the first three candles rather than waiting for another candle. At 39:26 he explicitly describes the Buy Limit and says the stop distance is known before activation; if price returns to the invalidating area, the scenario is cancelled. At 39:48–40:07 he explains that a subsequent candle can justify deleting the old order and placing a new one, but in the illustrated case he instead drags the existing order upward because the distance change is not large enough to materially harm money management.

The later worked example at 1:04:19 adds a stronger observation: the speaker says he places the order and repeatedly drags it downward until it is activated. The same passage then identifies the first leg as extending from a deeper structural point to the later endpoint, not simply from the order-fill price.

## Source-constrained conclusions

### Confirmed

1. Entry mechanism is a pending Buy Limit / Sell Limit concept, not a market-close replacement.
2. In the bullish example, the initial correction is described relative to the first low.
3. The order may be prepared before the correction candle completes.
4. The order may be modified or replaced as subsequent candle structure changes.
5. In the worked example, the order price is explicitly moved until activation.
6. The first-leg measurement is not proven to equal entry-to-leg-end distance; the transcript describes a deeper structural origin for Leg 1.

### Not confirmed

- exact OHLC field for the initial limit;
- exact numerical offset from the first low;
- whether the limit is always on the first-low boundary or can be inside/outside it;
- deterministic rule for when to move versus replace an order;
- maximum number of modifications;
- exact activation/fill semantics under touch or overshoot;
- exact relationship between the eventual fill price and geometric C.

## Important anti-inference result

The source evidence is now sufficient to reject a simplistic canonical rule of:

`entryPrice = C = fixed first-low value`

as an unsupported interpretation.

This rejection is not a claim that the entry cannot equal a first-low price in a particular example. It means the transcript demonstrates order placement and subsequent movement, so a fixed universal equality cannot be promoted without the corresponding visual rule.

Likewise, the later deep-leg example prevents us from defining Leg 1 solely from the entry price merely because that would make AB=CD easy to calculate.

## Visual resolution still required

The following source windows remain necessary for exact geometry:

- 38:18–40:16: identify the horizontal level initially used for Buy Limit and the structural reference used for cancellation/update.
- 1:04:00–1:04:42: identify the successive order positions and the exact candle/swing from which the displayed Leg 1 is measured.

If the visuals do not uniquely identify the price field, the field remains unresolved.

## Gate impact

`G415 = PASS — SOURCE CONSTRAINT STRENGTHENED`

`UNRES-ENTRY-PRICE = OPEN / NARROWED`

`UNRES-ENTRY-TIMING = PARTIALLY RESOLVED / DYNAMIC ORDER UPDATE SEMANTICS OPEN`

`UNRES-ABCD-ANCHORS = OPEN / DEEP STRUCTURAL ORIGIN EVIDENCE STRENGTHENED`

`G400 = BLOCKED`

`FROZEN_GEOMETRY = NOT AUTHORIZED`

`DEV = NOT AUTHORIZED`

`VALIDATION = PROTECTED`

`PRODUCTION = BLOCKED`

## Next action

Perform targeted visual frame reconciliation for the two windows above. Do not implement a fixed entry formula until the visual evidence identifies the source-defined level and update semantics.
