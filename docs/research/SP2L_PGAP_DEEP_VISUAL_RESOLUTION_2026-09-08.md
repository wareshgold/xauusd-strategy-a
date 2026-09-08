# SP2L P-Gap Deep Visual Resolution — 2026-09-08

## Scope
Research-only deep inspection of the authoritative teaching frames around 34:00–37:00. No production rule is frozen.

## New visual observations

1. The slide explicitly labels the accepted constructions `Valid BO = P-Gap`.
2. One construction is explicitly rejected with a red X; three constructions are presented as accepted-looking variants.
3. The accepted variants are not a single fixed candle-index pattern: the breakout/gap presentation occurs at different positions relative to the preceding staircase-like candles.
4. The blue/grey highlighted P-Gap regions are illustrative shaded zones. They do not terminate cleanly on a uniquely identifiable pair of OHLC extremes in the source image.
5. The shaded regions can overlap the breakout candle body/wick area; therefore the visual rectangle cannot safely be interpreted as an executable empty-price interval.
6. Earlier annotations mark candle-level lows/highs and breakout-related levels, but they do not establish a universal wick/body boundary convention for P-Gap.
7. The later AB=CD slide is adjacent to the P-Gap teaching material, but does not add a machine-readable A/B/C/D anchor mapping.

## Source-safe semantic lock

The strongest deterministic meaning currently supported is:

`valid breakout / Spike context + source-defined P-Gap occurrence`

P-Gap is therefore a breakout-associated concept, not an arbitrary visible gap and not a generic three-candle imbalance imported from another methodology.

## Candidate formulas still under discrimination

### PG-WICK
A gap/non-overlap defined by candle full ranges/wicks.

Status: **STRONG CANDIDATE**, not frozen.

### PG-BODY
A gap/non-overlap defined by candle bodies.

Status: **UNRESOLVED**.

### PG-MIXED
A source-specific mixed body/wick boundary.

Status: **UNRESOLVED**.

### PG-GENERIC-3C
A generic three-candle imbalance/FVG detector.

Status: **REJECTED AS CANONICAL** because source does not establish that equivalence.

## Boundary semantics still unresolved

- exact candle pair;
- exact timing of P-Gap relative to breakout candle;
- wick vs body vs mixed boundary;
- equality/touch behavior;
- minimum gap magnitude;
- whether the highlighted rectangle represents the actual gap interval or only an explanatory marker.

No numeric threshold is introduced.

## Synthetic discrimination update

The next fixture family should use minimal candle sequences where:

1. wick ranges are separated but bodies overlap;
2. bodies are separated but wicks overlap;
3. both are separated;
4. boundaries exactly touch;
5. the same gap occurs without a valid breakout context;
6. breakout occurs before the gap versus higher-lows-first gap presentation.

Expected use: source evidence, not historical profitability, selects the surviving geometry.

## Gate decision

**P-Gap semantic resolution: PARTIAL.**

The source now supports a stronger semantic lock around `breakout-associated non-overlap`, but the executable P-Gap formula remains unresolved.

- SOURCE RESOLUTION: progressing
- SYNTHETIC FIXTURES: expanded/next discriminator defined
- FROZEN GEOMETRY: BLOCKED
- DEV: locked
- VAL: untouched
- FRESH HOLDOUT: locked
- PRODUCTION: unchanged

## Explicit non-assumptions

Do not implement any of the following as canonical:

- generic FVG / three-candle imbalance;
- body-only P-Gap;
- wick-only P-Gap as frozen fact;
- a fixed candle index;
- a numeric minimum gap chosen by backtest;
- P-Gap boundary = Entry;
- P-Gap boundary = SL;
- P-Gap boundary = classical harmonic C.
