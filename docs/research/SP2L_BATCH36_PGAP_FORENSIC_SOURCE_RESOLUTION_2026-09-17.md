# SP2L Batch 36 — P-Gap Forensic Source Resolution — 2026-09-17

## Purpose

Resolve the remaining P-Gap question without inventing geometry: determine whether the available author/primary material exposes an exact P-Gap construction, candle indexing, direction mirror, threshold, or wick/body semantics that can become canonical for SP2L.

This pass follows the source-first rule: source meaning outranks implementation convenience and backtest performance. No formula is promoted unless the source itself supports it.

## Sources inspected

### 1. Primary SP2L training artifact supplied by the user

Video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Targeted forensic window: approximately **30:00–33:00** (1800–1980s), with finer 5-second sampling and single-frame inspection around 1905–1930s.

Observed primary-artifact evidence:

- The training deck explicitly labels the concept **`P-GAP`**.
- The handwritten material associates P-GAP with **`Gap`** and a continuation/context annotation.
- The chart examples repeatedly distinguish candle sequences visually and mark candidate gap/continuation regions.
- Around 38:00 elsewhere in the artifact, `Valid BO = P-Gap` is explicitly displayed; this establishes that P-Gap is used as a validity condition in the SP2L teaching sequence.
- The inspected P-Gap teaching frames do **not** expose a readable numeric formula, explicit candle-index notation, a minimum gap threshold, wick-vs-body rule, or a complete bullish/bearish mirror formula.

Therefore the primary artifact confirms the P-Gap concept and its role, but does not freeze an executable numeric construction.

### 2. Author-attributed legacy educational material surfaced via secondary hosting

A searchable copy of material attributed to Mohammad Ali Poursamadi contains the following explicit construction statement in its gap section:

> `به فاصله بین سقف 2 کندل قبل و کف کندل حاضر دقت کنید که اگر فاصله داشت گپ ایجاد شده است`

The same material identifies four gap categories and explicitly maps `P_GAP` to **Pressure gap**.

A second indexed copy reproduces the same definition and terminology. This is materially stronger than a generic third-party trading explanation because the material is attributed to the same author, but it is still **secondary-hosted legacy material**, not the current SP2L page itself and not a directly retrieved author-hosted SP2L specification.

The evidence supports the following candidate construction for the illustrated bullish orientation:

- compare the **high of the candle two bars before** with the **low of the current candle**;
- if a positive price distance exists between those boundaries, a gap exists.

However, the source text does not, in the located excerpt, establish all of the following for the current SP2L implementation:

- whether this exact construction is the P-Gap definition used in the current SP2L training video;
- the exact indexing convention in a machine-readable sense;
- the bearish mirror construction;
- whether the relevant boundaries are wick highs/lows or body/open/close values in every case;
- whether a zero-width boundary counts as a gap;
- any minimum numeric threshold or tolerance;
- whether P-Gap is required on a specific spike candle or any candle pair within the spike;
- whether the P-Gap is a validity condition only or also determines entry/order geometry.

## Forensic conclusion

The pass found a **source-aligned candidate construction**, but not a source-complete canonical SP2L formula.

The correct status is therefore:

**P-Gap concept: SOURCE-CONFIRMED.**

**Legacy author-attributed candidate construction: IDENTIFIED.**

**Current-SP2L exact formula/indexing/mirror/threshold semantics: UNRESOLVED.**

The candidate must not be normalized into an implementation such as `High[2] - Low[0] > 0` as a canonical rule. Such notation would be a research normalization, not source language.

## Geometry gate impact

F12 can be strengthened from:

`P-Gap validity + second-leg trigger concept source-confirmed / exact executable taxonomy unresolved`

to:

`P-Gap validity source-confirmed / legacy author-attributed candidate construction identified / current SP2L executable construction unresolved`.

This does **not** unlock Frozen Geometry.

The following remain blocked:

1. exact P-Gap candle indexing;
2. bullish/bearish mirror;
3. wick/body boundary semantics;
4. minimum threshold/tolerance;
5. exact relation of the P-Gap to the qualifying spike candle(s);
6. trigger/fill semantics after the P-Gap is established.

## Canonical-rule decision

**No canonical P-Gap formula is frozen in Batch 36.**

No backtest variant is selected. No production decision logic is changed. No BUY/SELL generation is introduced.

## Gate status

- Source Resolution: **PARTIAL PASS — candidate construction materially strengthened**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

## Next source-resolution target

The highest-value unresolved source question is now the **directional/mirror and exact indexing semantics of P-Gap in the current SP2L training material**. The next pass should target any source frame, transcript, note, or worked example that explicitly shows the bearish counterpart or labels the exact three-candle relationship. Only if that evidence appears should the candidate be promoted toward canonical geometry.
