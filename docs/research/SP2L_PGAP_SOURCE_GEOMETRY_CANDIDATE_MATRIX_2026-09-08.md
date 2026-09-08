# SP2L P-Gap Source Geometry Candidate Matrix

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Status:** `NARROWED — NOT FROZEN`

## Purpose

This record narrows the executable P-Gap hypothesis using the recovered primary transcript and direct inspection of the uploaded source video. It deliberately stops short of inventing a final formula.

## 1. Primary-source evidence

### 31:43–32:12 — P-Gap is a distinct gap type

The instructor explicitly says the breakout candle has a P-Gap / pressure gap and distinguishes P-Gap from E-Gap and Common-Gap. He states that not every visible gap should be treated as the same gap type and that the location of formation matters.

**Decision:** `P_GAP != generic_visible_gap` is source-confirmed.

### 34:14–34:35 — P-Gap marks breakout location

The instructor says P-Gap can be used as an easy visual marker for where the breakout occurred. He then describes a construction where the referenced high and low do not overlap and a gap occurs together with breakout + follow-through. A second construction creates the gap on the next candle.

**Decision:** source supports a gap/non-overlap relationship tied to breakout, with more than one temporal construction.

### 34:44–35:37 — multiple temporal constructions are one SP2L Spike

The source treats these as conceptually equivalent for the current strategy:

1. breakout first, then continuation/higher lows, then P-Gap;
2. higher lows first, then P-Gap;
3. a third three-candle construction in which the next candle fails to extend upward and then moves down.

**Decision:** do not require one fixed candle index for P-Gap inside the Spike sequence.

### 50:09–50:56 — P-Gap is associated with the early / valid trend, E-Gap with later extension

The instructor contrasts an early, clean trend opportunity with a later extended condition and says the former gives P-Gap rather than E-Gap. After multiple successive pushes, he describes the later condition as likely E-Gap and says it is riskier.

**Decision:** P-Gap has a source-supported *context/location* component in addition to gap geometry. Exact numeric definition of “early” is unresolved.

## 2. Narrowed geometric candidate

The strongest source-aligned candidate is now:

> **P-Gap = a price-range non-overlap between relevant adjacent candles, occurring in the breakout / early-trend construction that the source classifies as a valid Spike.**

For a bullish candidate, the visual/transcript language is consistent with a prior/relevant candle high being below the next relevant candle low. For a bearish candidate, the polarity is reversed.

This is materially narrower than a generic three-candle imbalance detector.

## 3. What is NOT yet proven

The source still does not uniquely prove:

- whether the relevant boundaries are wick High/Low or candle-body Open/Close;
- whether the two candles must be consecutive in every variant;
- whether the P-Gap is measured on the breakout candle pair or may be one candle later in the second construction;
- whether equality/touch counts as overlap;
- any minimum gap size or tick tolerance;
- a numeric definition of the “early-trend” location condition;
- whether all three Spike constructions share exactly the same gap predicate.

Therefore this document does **not** authorize replacing the unresolved `SourceConfirmedGap` input with an executable formula.

## 4. Candidate formulas to discriminate with source evidence

| Candidate | Definition | Source support | Canonical? |
|---|---|---|---|
| PG-1 | Adjacent candle wick-range non-overlap at breakout | Strong | NO — timing/variant details open |
| PG-2 | Adjacent candle body-range non-overlap at breakout | Weak/visual only | NO |
| PG-3 | Generic three-candle imbalance | Not source-confirmed | REJECTED as canonical |
| PG-4 | Any visible gap anywhere in Spike | Contradicted by P-Gap/E-Gap distinction | REJECTED |
| PG-5 | Adjacent wick non-overlap + source-defined early/breakout context | Strongest composite hypothesis | CANDIDATE ONLY |

## 5. Synthetic discriminators added to research plan

The fixture suite must distinguish:

- wick-only separation with overlapping bodies;
- body-only separation without wick separation;
- exact touch/equality;
- adjacent-candle gap on breakout candle;
- gap appearing one candle later;
- gap after several continuation pushes (E-Gap candidate);
- generic three-candle imbalance with no breakout context;
- breakout + follow-through without any gap;
- channel-like overlap despite a sharp directional move.

A fixture may only become a canonical expected result if the source evidence resolves the corresponding ambiguity.

## 6. Frame-by-frame boundary inspection result — 2026-09-08

Direct inspection of the source video at approximately `34:10–35:40` and the supporting entry drawings at `38:20–40:20` was completed.

The P-Gap slide visibly labels the concept `Valid BO = P-Gap` and uses translucent shaded rectangles around the breakout area. The rectangles establish **contextual placement**, but their pixel boundaries are schematic and do not uniquely identify wick High/Low versus body Open/Close versus another candle-level boundary.

The entry drawings separately show a horizontal Limit level and structural SL/invalidation handling. They do not establish a numeric P-Gap boundary or prove that the Limit is the same geometric point as a P-Gap edge.

**New negative result:** the primary visual source is insufficient to promote wick-to-wick into a frozen executable formula. This is a deliberate resolution outcome, not a reason to fit the rule to historical performance.

See `docs/research/SP2L_PGAP_BOUNDARY_RESOLUTION_2026-09-08.md` for the detailed frame inspection record.

## 7. Gate decision

**P-Gap semantic role:** `SOURCE-CONFIRMED`  
**P-Gap non-overlap relationship:** `STRONG SOURCE EVIDENCE`  
**P-Gap executable formula:** `UNRESOLVED`  
**Generic 3-candle imbalance as P-Gap:** `REJECTED`  
**Production change:** `NONE`

## Primary-source references

- `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt` (SHA `47f867385338738a23b2d06dc48e67b852127243`)
- Source video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Official SP2L page: `https://poursamadi.com/sp2l-strategy/`
