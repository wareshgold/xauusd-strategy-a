# SP2L P-Gap Source Ceiling Checkpoint — 2026-09-26

## Purpose

Record the current evidence boundary after the targeted primary-transcript and archived source-visual passes. This checkpoint separates the **source-discriminated geometric primitive** from the still-unresolved **complete P-Gap qualification rule**.

## Source-confirmed / source-discriminated

1. P-Gap and Pressure Gap (گپ فشار) are the same SP2L source concept.
2. P-Gap is distinct from E-Gap.
3. The primary SP2L material describes P-Gap using a non-overlap/separation relationship between a candle high and the following candle low in the illustrated bullish case.
4. The preserved source reconstruction therefore supports the adjacent-candle geometric primitive:
   - bullish: `High[i] < Low[i+1]`
   - equality is excluded because the source describes non-overlap.
5. The opposite-side expression is geometrically consistent:
   - bearish: `Low[i] > High[i+1]`
   - this remains a mirror unless independently demonstrated in primary source.
6. The source demonstrates multiple temporal orderings in which P-Gap appears, including breakout-before-gap and higher-lows-before-gap constructions.
7. The source does not bind the P-Gap concept to the legacy fixed `[-4,-3,-2,-1]` detector window.

## Still unresolved

- Which source-defined candle roles must qualify the adjacent-candle gap as **P-Gap** rather than a generic gap.
- Deterministic early/strong pressure/trend context.
- Exact breakout/follow-through relationship.
- Precedence across the demonstrated temporal orderings.
- Minimum numeric gap threshold beyond strict non-overlap.
- Universal bearish primary-source confirmation.
- Complete deterministic P-Gap classifier across all source variants.

## Rejected canonical shortcuts

The following remain non-canonical:

- `Low[t] > High[t-2]` as a universal SP2L P-Gap formula.
- `low[1] > high[3] + 1`.
- Any fixed `p_gap_price` selected from backtest performance.
- Any fixed SP2L candle index inferred from the current author-replica implementation.
- Any pressure/trend threshold inferred from the qualitative “10–30 candles” description.
- Any wick/body/tolerance rule inferred from chart pixels.

## Deterministic research primitive

The only geometry that can currently be isolated without inventing source meaning is:

```
GAP_BULL(i) = High[i] < Low[i+1]
GAP_BEAR(i) = Low[i] > High[i+1]
```

This is a **geometric primitive**, not a complete P-Gap detector.

Existing synthetic fixture evidence already validates strict non-overlap versus overlap/equality and confirms that the primitive is independent of the legacy fixed index window.

## Source-resolution stopping rule

Do not run further backtests, parameter sweeps, or implementation comparisons to decide the unresolved P-Gap qualification.

One further source pass is justified only if it can locate genuinely new primary evidence that explicitly binds:

1. the two candle roles;
2. the pressure/trend qualification;
3. the ordering/precedence;
4. and the P-Gap classification boundary.

If that evidence is not found, the project records a **source ceiling** for executable P-Gap geometry rather than continuing repetitive forensic passes.

## Gate

- P-Gap semantic identity: SOURCE-CONFIRMED
- Adjacent non-overlap primitive: SOURCE-DISCRIMINATED
- Complete P-Gap classifier: UNRESOLVED
- Frozen SP2L Geometry: BLOCKED
- Untouched Validation: LOCKED
- Fresh Holdout: LOCKED
- Production/live canonical BUY/SELL: DISABLED

No detector or live rule is promoted by this checkpoint.
