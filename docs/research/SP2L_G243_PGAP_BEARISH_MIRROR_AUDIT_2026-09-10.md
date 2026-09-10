# SP2L G243 — Bearish P-Gap mirror and event-timing audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `BEARISH_MIRROR_NOT_SOURCE_FROZEN__TIMING_NOT_SOURCE_FROZEN`

## Objective

Independently audit the bearish P-Gap mirror and event timing before any canonical B1 freeze. This is a source-only investigation. No backtest result, optimization result, or fixture performance is used to choose the source meaning.

## Source material reviewed

Primary SP2L source video:

`/mnt/data/strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Key P-Gap frames reviewed in the source section around approximately 35:50–36:16, including the accepted/rejected panel and the subsequent numbered examples.

Same-author Gap course:

`/mnt/data/gap پورصمدی دوره جامع.mp4`

The Gap-course section around approximately 16:50–19:20 was also reviewed for the author's explicit candle-endpoint terminology.

Official creator page cross-check:

`https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/`

## 1. Bearish mirror — direct SP2L evidence

The reviewed SP2L P-Gap teaching panel is dominated by bullish schematic/examples. It establishes that a valid sharp directional move is associated with a visibly separated P-Gap region and that directional movement without the required gap is rejected. However, the reviewed panel does **not** provide an independently measurable bearish P-Gap example whose two endpoint wick extrema can be read with the same confidence as the bullish examples audited in G242.

The official creator description confirms that SP2L operates in both directions: a buy follows an upward spike and a sell follows a downward spike. It also explicitly describes the bearish correction counterpart as the corrective candle reaching the high of the previous candle. This confirms directional symmetry of the broader SP2L setup, but it does not publish the exact OHLC formula for the bearish P-Gap itself.

Therefore the mathematically obvious mirror candidate

`Low[t-2] > High[t]`

must remain a **candidate only**. It is not promoted to canonical P-Gap geometry from symmetry alone.

## 2. Same-author Gap-course cross-check

The reviewed Gap-course material explicitly teaches the bullish endpoint relation using the distance between the high of the candle two bars earlier and the low of the current candle. The visible chart annotations are consistent with the same full-extrema interpretation established in G242.

This source is useful evidence for the bullish construction, but the reviewed section does not provide a direct textual bearish P-Gap formula that can be safely imported into Strategy A.

Consequently, the Gap-course material strengthens the bullish source correlation but does not independently freeze the bearish mirror.

## 3. Equality and boundary handling

No reviewed source frame establishes whether exact endpoint contact counts as a P-Gap.

Therefore both of the following remain unresolved:

- bullish: `High[t-2] < Low[t]` versus `High[t-2] <= Low[t]`;
- bearish: `Low[t-2] > High[t]` versus `Low[t-2] >= High[t]`.

No numeric minimum gap distance is source-confirmed.

## 4. Event timing audit

The source demonstrates the P-Gap visually as part of the spike construction and later labels accepted breakout examples as `Valid BO = P-Gap`. It does not specify a deterministic timestamp rule such as:

- intrabar recognition;
- confirmation only at the close of the later endpoint candle;
- confirmation only after the spike candle closes;
- confirmation at the first tick where endpoint separation becomes true.

Because the production engine must be reproducible, this timing field remains `UNKNOWN` rather than being inferred from chart appearance.

No implementation may silently convert the source visual event into a close-of-candle rule merely for coding convenience.

## 5. What the source does support

The combined evidence supports these research-level conclusions:

1. P-Gap is a first-class validity condition associated with the SP2L spike/breakout concept.
2. The bullish endpoint geometry is strongly supported as wick/full-extrema based.
3. The bullish leading executable candidate is `High[t-2] < Low[t]`.
4. A sharp directional move without the corresponding gap is not sufficient.
5. SP2L itself has both bullish and bearish trade directions.
6. The bearish P-Gap formula is still not independently source-frozen.
7. The event timestamp/confirmation moment is still not source-frozen.

## 6. Explicit non-conclusions

This audit does **not** establish:

- `Low[t-2] > High[t]` as a canonical production rule;
- equality-inclusive P-Gap semantics;
- a minimum gap-size threshold;
- a deterministic spike-size/shape threshold;
- a specific intrabar or candle-close confirmation rule;
- P-Gap = FVG / generic three-candle imbalance;
- P-Gap = Pressure Gap;
- any market-entry substitute for the source pending-limit mechanism.

## Gate decision

- **Source Resolution:** `PASS_PARTIAL`.
- **Bullish endpoint geometry:** `STRONGLY_SUPPORTED = WICK_EXTREMA` from G242.
- **Bullish endpoint relation:** `LEADING = High[t-2] < Low[t]`.
- **Bearish mirror:** `UNKNOWN / CANDIDATE = Low[t-2] > High[t]`; not canonical.
- **Equality handling:** `UNKNOWN`.
- **Minimum gap:** `UNKNOWN`.
- **Spike predicate:** `UNKNOWN` as a deterministic formula.
- **Event timing:** `UNKNOWN`.
- **Historical DEV selection:** `BLOCKED` for the unresolved fields.
- **Untouched Validation:** protected.
- **Fresh Holdout:** protected.
- **Production BUY/SELL:** `BLOCKED`.

## Next action

Proceed to the formal **B1 P-Gap source-resolution decision**. Freeze only the evidence-supported bullish endpoint semantics and keep the bearish mirror, equality handling, spike predicate, timing, and horizontal extent explicitly unresolved unless a stronger raw source frame resolves them. The B1 record must not manufacture a bearish formula from mathematical symmetry alone.
