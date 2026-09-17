# SP2L Batch 36 — Source Resolution Matrix Addendum — 2026-09-17

## F12 update

### Previous status

`AUTHOR-ASSOCIATED P-GAP VALIDITY + SECOND-LEG TRIGGER CONCEPT + PRIMARY-ARTIFACT BO ORDERING CONFIRMED / EXACT EXECUTABLE TAXONOMY UNRESOLVED`

### Batch 36 evidence

A dedicated forensic pass inspected the primary SP2L training artifact around the P-Gap teaching segment (~30:00–33:00), including fine sampling around ~31:45–32:10. The artifact explicitly labels **P-GAP** and associates it with **Gap/Continuation**, but does not expose a readable numeric formula, exact candle indexing, threshold, wick/body rule, or complete bearish mirror.

Separately, a secondary-hosted legacy educational document attributed to Mohammad Ali Poursamadi was located with an explicit gap construction statement:

`به فاصله بین سقف 2 کندل قبل و کف کندل حاضر دقت کنید که اگر فاصله داشت گپ ایجاد شده است`

The same material identifies `P_GAP` as **Pressure gap**. This yields a concrete author-attributed candidate for the bullish orientation: the gap is observed between the high of the candle two bars earlier and the low of the current candle when a positive distance exists.

This is stronger than the prior concept-only evidence, but it is not yet sufficient to establish that the current SP2L training system uses exactly this construction in all cases.

### Current source status

**F12 — P-Gap:** `SOURCE-CONFIRMED CONCEPT / LEGACY AUTHOR-ATTRIBUTED CANDIDATE CONSTRUCTION IDENTIFIED / CURRENT SP2L INDEXING, MIRROR, BOUNDARY AND THRESHOLD SEMANTICS UNRESOLVED`

### Canonical executable rule?

**No.**

Do not convert the candidate into a canonical machine formula merely by normalization such as `High[2] - Low[0] > 0`.

### Freeze impact

**BLOCKED.**

### Remaining source questions

- current-SP2L candle indexing;
- bearish mirror;
- wick vs body boundaries;
- zero-gap equality handling;
- minimum threshold/tolerance;
- which spike candle(s) must contain the P-Gap;
- relationship between P-Gap validity and trigger/fill semantics.

## Gate

Source Resolution remains **PARTIAL PASS**.

Frozen Geometry remains **BLOCKED**.

No backtest or production rule was changed.
