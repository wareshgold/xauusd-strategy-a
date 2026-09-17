# SP2L Batch 37 — P-Gap Mirror / Indexing Negative Resolution — 2026-09-17

## Purpose

Close the next source-resolution question after Batch36: determine whether the available primary/current SP2L and author-associated material exposes a bearish P-Gap mirror or exact three-candle indexing that can be frozen without inference.

## Sources inspected

### 1. Primary SP2L training artifact

The supplied training video was inspected around the dedicated P-Gap teaching segment (~30:00–33:00), including fine frames around ~31:45–32:10.

Observed:

- `P-GAP` is explicitly handwritten on the SP2L teaching slide.
- `Gap` is explicitly associated with the P-Gap annotation.
- `Continuation` is also annotated in the same teaching sequence.
- The examples are primarily presented as bullish candle sequences in the inspected segment.
- No readable bearish P-Gap formula, explicit three-candle index notation, or numerical threshold/tolerance is exposed in the inspected frames.

The later primary sequence also explicitly shows `Valid BO = P-Gap`, confirming P-Gap's role as a validity condition, but does not add the missing mirror/indexing semantics.

### 2. Current author-associated SP2L page

The current author-associated page explicitly states that a valid SP2L spike requires a P-Gap and that a sharp movement without a gap is not valid. It separately states the up/down second-leg mirror:

- uptrend: corrective candle reaches the low of the previous candle;
- downtrend: corrective candle reaches the high of the previous candle.

This confirms that SP2L has explicit directional mirroring for the second-leg trigger, but the page does **not** provide an equivalent bearish P-Gap construction or exact P-Gap candle indexing.

### 3. Author-attributed legacy material surfaced via secondary hosting

The legacy material contains the explicit bullish-oriented gap statement previously recorded in Batch36:

`به فاصله بین سقف 2 کندل قبل و کف کندل حاضر دقت کنید که اگر فاصله داشت گپ ایجاد شده است`

It also identifies `P_GAP` as Pressure gap.

Additional search of the same indexed material did not expose a source-complete bearish counterpart that can be tied unambiguously to the current SP2L training system.

## Resolution

The source search **did not resolve**:

1. exact current-SP2L candle indexing;
2. bearish P-Gap mirror;
3. wick vs body boundary semantics;
4. zero-width gap handling;
5. minimum gap threshold/tolerance;
6. which spike candle(s) must contain the P-Gap.

The legacy bullish candidate therefore remains a **candidate only**.

Do not promote it into canonical code by normalization such as `High[2] - Low[0] > 0`.

## F12 status

**SOURCE-CONFIRMED P-Gap CONCEPT + LEGACY AUTHOR-ATTRIBUTED BULLISH CANDIDATE / CURRENT-SP2L INDEXING AND BEARISH MIRROR UNRESOLVED.**

## Gate impact

- Source Resolution: **PARTIAL PASS**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

No canonical formula, backtest variant, or production decision logic was changed.

## Next source-resolution target

P-Gap should remain explicitly unresolved rather than repeatedly normalized from generic gap theory. The next highest-value forensic targets are the remaining source-critical geometry questions, especially **AB=CD anchors/tolerance (F14)** and **first-important swing selection (F8)**, while retaining the P-Gap candidate as a non-canonical hypothesis until direct source evidence closes the mirror/indexing gap.
