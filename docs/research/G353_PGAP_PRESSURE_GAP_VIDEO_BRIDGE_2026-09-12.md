# G353 — P-Gap / Pressure-Gap Video Source Bridge Audit

Date: 2026-09-12  
Gate: SOURCE RESOLUTION  
Parent: G352  
Canonical status: **P-GAP SEMANTICS STRENGTHENED; EXECUTABLE GEOMETRY NOT FROZEN**

## 1. Source provenance

New source asset supplied for this audit:

- File: `gap پورصمدی دوره جامع.mp4`
- Duration: `1955.793560 s` (~32:35.79)
- SHA-256: `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`
- Resolution: 854×480
- Frame rate: 30 fps
- Audio: AAC
- No embedded subtitle stream was found.

This source is a Poursamadi PriceAction lesson titled `PriceAction (Gaps)` and is audited here as source material, not as a generic trading reference.

## 2. Multi-topic evidence audit

### A. Generic Gap geometry

At approximately `15:40–18:40`, the source repeatedly displays the statement:

`به فاصله بین سقف ۲ کندل قبل و کف کندل حاضر دقت کنید اگر فاصله داشت گپ ایجاد شد`

Meaning at source level: look at the distance between the high of the candle two candles earlier and the low of the current candle; if a gap/distance exists, a gap is present.

This is stronger geometric evidence than the previous SP2L audit had for the generic term `Gap`. The corresponding chart is visually marked with blue regions around the gap locations.

Source evidence status:
- Generic Gap uses a relationship involving the high of the candle two bars earlier and the low of the current candle: **SOURCE-CONFIRMED for the displayed bullish example**.
- The visual examples also contain bearish gap regions, but this audit does not promote a mathematically mirrored bearish formula unless explicitly stated by the source.
- This does **not** by itself define P-Gap or E-Gap.

### B. Breakout Gap

At approximately `20:00–22:00`, the source states:

`زمانیکه یک گپ در ابتدای یک حرکت ایجاد می شود. آن یک بریک اوت گپ است`

Meaning: when a gap is created at the beginning of a movement, it is a Breakout Gap.

The displayed example is labelled `بریک اوت گپ صعودی` (bullish Breakout Gap), and the source also references the current candle closing at the previous high in the example.

Status: **SOURCE-CONFIRMED semantic classification.** Exact executable endpoint/threshold beyond the generic gap observation is not frozen.

### C. Pressure Gap = P-GAP bridge

At approximately `22:20–24:40`, the source presents `گپ فشار` (Pressure Gap). The slide text states that after roughly `10 to 30 candles` in a trend, pressure temporarily stops and then a bullish trend bar appears, increasing the probability of the start/continuation of the trend.

The source's taxonomy slide at approximately `31:30–32:00` lists the gap types as:

- `بریک اوت` — Breakout
- `فشار` — Pressure
- `خستگی` — Exhaustion
- `معمولی` — Common

This is a major bridge to SP2L because the SP2L transcript at `31:43` explicitly says the setup contains `P-GAP` and immediately glosses it as `گپ فشار` (Pressure Gap). The SP2L transcript also says P-GAP and E-GAP are different concepts and that the gap types differ by their formation location/context. Therefore:

`P-GAP ↔ Pressure Gap (گپ فشار)` = **SOURCE-CONFIRMED semantic identity** across the two Poursamadi lessons.

However, the Pressure Gap lesson's `10–30 candles` is presented as contextual description of when pressure stops in the trend; it must not be promoted into a universal P-Gap candle-count rule for Strategy A without checking the full examples and scope. The source does not establish a fixed minimum gap size, overlap tolerance, or wick/body endpoint rule here.

### D. Exhaustion Gap = E-GAP bridge

At approximately `25:00–26:40`, the source presents `گپ خستگی` (Exhaustion Gap). The slide states that buying pressure continues for 10 or more candles, a good context for a large pullback forms near resistance, and price will reverse after the gap.

This is consistent with the SP2L transcript's use of `E-GAP` as a distinct, later/riskier gap context. Therefore:

`E-GAP ↔ Exhaustion Gap (گپ خستگی)` = **SOURCE-CONFIRMED semantic bridge**, subject to exact scope/context reconciliation.

The `10 or more candles` wording is source evidence about the displayed exhaustion-gap context; it is not yet a universal executable E-Gap threshold for Strategy A.

### E. Common Gap

At approximately `28:20–28:40`, the source states that every trend bar is treated as a gap in the displayed explanation, that most such gaps do not have useful predictive/follow-through value, and that they commonly occur in trading ranges.

The taxonomy slide later labels this category `معمولی` (Common).

Status: **SOURCE-CONFIRMED semantic classification.** Exact algorithmic classification remains unresolved.

### F. Risk/reward guidance in the Gap lesson

At approximately `10:30–11:40`, a source slide states that if, after a gap, the trader is in a situation where the probability of the prediction being correct is about 60%, scalping with reward 1:1 is allowed; after a breakout where direction is still uncertain, reward 1:2 should be used.

This is important new source evidence because it demonstrates that 1:1 and 1:2 can be used as contextual reward guidance in the broader Poursamadi material. It does **not** establish a single universal TP rule for SP2L, and it does not override the SP2L lesson's TP1/TP2/R1/R2 language. Therefore no TP geometry is frozen from this evidence.

## 3. Reconciliation with SP2L transcript

The direct SP2L transcript says:

- `31:43`: the breakout candle contains P-GAP / `گپ فشار` and this differs from E-GAP.
- `32:03`: P-GAP, E-GAP, Common-GAP, and morning gap are described as four different things, with formation location making them different.
- `34:14–35:37`: P-GAP is used as a sign for distinguishing the relevant strong breakout/trend structure; two structurally different orders of higher-lows versus gap formation are treated as equivalent in the current strategy.
- `50:09–50:20`: an early, timely position is described as P-GAP rather than E-GAP; later target progression is associated with E-GAP risk.

This new Gap lesson therefore resolves an important semantic ambiguity that remained after G352:

> **P-GAP is not merely a generic gap label. In Poursamadi's terminology it corresponds to the Pressure Gap category, while E-GAP corresponds to Exhaustion Gap.**

The lesson also establishes a separate Breakout Gap category. Therefore `Breakout Gap` must not be silently substituted for `P-GAP` merely because both can occur near the beginning of directional movement.

## 4. Discrimination matrix

| Dimension | New Gap lesson | SP2L transcript | Status |
|---|---|---|---|
| Generic Gap geometry | High of 2 candles ago vs current low shown | Gap discussed | **Resolved for displayed generic example** |
| Breakout Gap | Gap at beginning of movement | Breakout + P-GAP can coexist in SP2L | **Distinct source category** |
| Pressure Gap | 10–30 candle trend context, pressure pause, trend bar, higher continuation/start probability | P-GAP explicitly glossed as `گپ فشار` | **P-GAP identity resolved semantically** |
| Exhaustion Gap | 10+ candles pressure, near resistance, large pullback context, reversal after gap | E-GAP explicitly distinct from P-GAP | **E-GAP identity resolved semantically** |
| Common Gap | Low predictive/follow-through value; often ranges | Common-GAP named separately | **Resolved semantically** |
| Morning gap | Separate category mentioned in SP2L | Mentioned as distinct | **Not part of core P-GAP definition** |
| P-Gap minimum size | Not stated | Not stated | **BLOCKED** |
| P-Gap overlap rule | Not stated | Not stated | **BLOCKED** |
| P-Gap exact OHLC endpoint rule | Generic Gap example exists, but no explicit statement that all P-Gap instances use exactly those fields | Not stated | **BLOCKED for executable P-Gap** |
| Wick/body convention | Not stated | Not stated | **BLOCKED** |
| P-Gap candle-count rule | 10–30 is contextual pressure-gap description | No universal count | **BLOCKED as universal threshold** |
| E-Gap executable threshold | 10+ contextual statement | Later/riskier context | **BLOCKED** |
| TP mapping | 1:1 / 1:2 contextual guidance | TP1/TP2/R1/R2/2X/3X | **Scope unresolved** |

## 5. Important source-first conclusion

G353 materially advances SOURCE RESOLUTION, but it does **not** authorize a complete P-Gap geometry freeze.

What can now be safely preserved:

1. `P-GAP` means the source's `Pressure Gap / گپ فشار` category.
2. `E-GAP` means the source's `Exhaustion Gap / گپ خستگی` category.
3. `Breakout Gap` is a separate named category and must not be equated with P-GAP.
4. `Common Gap` is a separate named category.
5. Gap classification depends materially on **formation location/context**, not only on the existence of a visual price gap.
6. The source supplies a concrete generic-gap geometric example involving the high two candles earlier and current low.

Still blocked for deterministic Strategy A:

- exact P-Gap executable endpoints in all directions;
- minimum size;
- overlap/tolerance;
- wick/body/open/close convention beyond the displayed generic example;
- universal 10–30 candle requirement;
- exact relationship between Pressure Gap occurrence and the SP2L breakout/FT event;
- exact P-Gap anchor for A/B/C/D geometry;
- TP1/TP2 mapping.

## 6. Gate decision

**G353 = PASS — SOURCE SEMANTICS FOR P-GAP/E-GAP SUBSTANTIALLY RESOLVED; EXECUTABLE P-GAP GEOMETRY STILL BLOCKED.**

```text
SOURCE_RESOLUTION_DISCOVERY = ADVANCED
P_GAP_SEMANTIC_IDENTITY = RESOLVED
E_GAP_SEMANTIC_IDENTITY = RESOLVED
BREAKOUT_GAP_DISTINCT = RESOLVED
GENERIC_GAP_DISPLAYED_GEOMETRY = PARTIALLY RESOLVED
P_GAP_EXECUTABLE_GEOMETRY = BLOCKED
FROZEN_GEOMETRY = BLOCKED
DEV = BLOCKED
VAL = PROTECTED
FRESH_HOLDOUT = LOCKED
PRODUCTION = BLOCKED
```

## 7. Next source-resolution work

The next high-value audit should cross-reference the new Gap lesson's actual chart examples with the SP2L frames around `31:43–37:57` and `49:47–50:56` to determine whether the Pressure Gap examples use the same displayed three-candle high/low geometry, and whether the source visually identifies the exact gap boundaries. This must be done by source evidence, not by assuming that the generic Gap formula applies universally to P-GAP.
