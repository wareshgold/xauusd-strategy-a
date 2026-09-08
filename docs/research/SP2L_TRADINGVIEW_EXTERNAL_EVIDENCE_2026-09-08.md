# SP2L TradingView External Evidence — 2026-09-08

## Status

Research-only external evidence. This document does **not** freeze any Strategy A geometry and does not authorize production use.

## Source

TradingView publication:
`SP2L Pour Samadi Indicator [TradingFinder] Spike 2 Legs PA`

The publication is a **protected/closed-source script**, so its implementation cannot be inspected. The page is third-party material, not the raw instructor source.

## Why it is useful

The page provides an independent implementation-adjacent description of SP2L that can be used to generate hypotheses for source-resolution work, especially around P-Gap/gap semantics and candle-level entry structure.

## Evidence extracted from the TradingView page

The page states that:

- a Spike is a sharp move and is associated with imbalance/inefficiency;
- the described implementation treats FVG as a consequence of the spike;
- bullish entries are associated with prior candle lows / higher-low structure;
- bearish entries are associated with prior candle highs / lower-high structure;
- SL is placed below/above the candle where the spike originated;
- TP examples include 1:1 and 1:2;
- the script exposes a configurable gap filter and multiple gap categories.

The publication also says the script is protected/closed-source, therefore these descriptions cannot reveal the exact P-Gap algorithm.

## Critical comparison with the authoritative source

### Supports the existing source-resolution work

1. **Candle-level structure is plausible.**
   The TradingView description uses prior candle lows/highs as entry references, which is consistent with the authoritative-source transcript and official material already recorded in this repository.

2. **Spike-origin structural invalidation is plausible.**
   The TradingView description places SL around the spike-origin candle, consistent with the source video semantics.

3. **Gap/imbalance is materially associated with the Spike.**
   This is directionally consistent with the authoritative source's `Valid BO = P-Gap` wording.

### Does NOT resolve P-Gap

The TradingView page uses the terms `FVG`, `imbalance`, and `gap`, but it does not publish the protected script's exact calculation. It therefore does **not** establish any of the following as canonical Strategy A rules:

- generic three-candle FVG;
- previous High → next Low formula;
- body-top → body-bottom formula;
- wick-to-wick formula;
- equality/touch convention;
- minimum gap threshold;
- exact candle timing;
- gap boundary used as entry price.

The page's existence of configurable `Gap Type` values (`All Gaps`, `Significant`, `Structural`, `Major`) further demonstrates that the third-party implementation has its own classification layer, but does not reveal which category, if any, corresponds to the instructor's P-Gap.

## Important contradiction / caution

The TradingView page describes entries in terms of HL/LH retests and FVG terminology. The authoritative source material in this project explicitly warns against importing generic market-structure terminology and distinguishes its candle-level method from classical internet AB/CD treatment.

Therefore:

> TradingView evidence may be used as a **candidate interpretation / discriminating hypothesis**, but it cannot override the authoritative source.

In particular, `P-Gap = FVG` remains **UNRESOLVED**.

## Research consequences

The external source increases the value of the following synthetic discriminators:

- bullish prior-low / bearish prior-high entry reference;
- wick-range gap vs body-range gap;
- three-candle FVG-like construction vs source-defined breakout-associated P-Gap;
- gap formation before/at/after breakout;
- gap classification that is visually present but not an executable entry boundary.

It does **not** justify implementing the third-party algorithm.

## Gate decision

- SOURCE RESOLUTION: progressing
- P-Gap exact formula: **UNRESOLVED**
- Entry semantic: strong source-aligned candidate
- SL semantic: strong source-aligned candidate
- Frozen Geometry: **BLOCKED**
- DEV: locked
- VAL: untouched
- Fresh Holdout: untouched
- Production: unchanged

## Next action

Use the external description only to construct targeted synthetic cases, then return to the authoritative video/source frames to determine whether any of those candidates are actually visible in the source. If the source cannot discriminate the candidates, preserve the uncertainty rather than selecting the third-party implementation.

## External references

- TradingView: `https://www.tradingview.com/script/Qiv9aTi0-SP2L-Pour-Samadi-Indicator-TradingFinder-Spike-2-Legs-PA/`
- TradingFinder MT5 description: `https://tradingfinder.com/products/indicators/mt5/sp2l-poursamadi-strategy-free-download/`

These are secondary sources and are not part of the authoritative Strategy A evidence hierarchy.
