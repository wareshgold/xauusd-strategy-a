# SP2L Batch 33 — Worked-Trade Entry Geometry Forensic — 2026-09-16

## Purpose

Test whether the observed worked-trade entry prices can be reconstructed from the visible chart geometry independently of the account/history timestamps, without importing an execution rule or selecting a canonical geometric interpretation.

This is a research-only forensic artifact. It does not define canonical entry, trigger, SL, 2X, AB=CD, or fill semantics.

## Material inspected

The primary training video worked-trade segment was inspected at finer temporal resolution across approximately **58:00–67:10**, with additional 5-second sampling around the later worked-trade/chart-history views.

The inspection focused on:

- chart time-axis labels;
- visible horizontal/diagonal reference levels;
- visible price scale;
- the account-position table;
- the later account/history table;
- repeated entry/SL/TP values.

## Direct observations

### 1. Chart chronology remains earlier than the history cluster

The finer frames confirm that the visible chart in the later worked-trade material progresses through the May 12 intraday sequence but, in the inspected views, its rightmost clearly readable time-axis region remains before the history events at `12:56:02`–`12:57:06`.

A representative later chart frame shows the chart continuing through approximately the **12:4x–12:5x** region while the history table simultaneously displays records at `12:56:02`, `12:56:24`, `12:56:58`, and `12:57:06`.

The exact rightmost chart tick is not sufficiently stable/readable in every frame to assert a single precise terminal timestamp, but the inspected chart views do not expose the 12:56–12:57 candles needed for an event-level reconstruction.

### 2. Entry prices are visible in account/history, not as a source-complete chart formula

The worked account/history material repeatedly exposes entry values including:

- `3229.08`
- `3223.84`
- `3228.88`
- `3232.41`

and associated SL/TP values including:

- `3237.73`
- `3235.50`
- `3237.80`
- `3213.37`

These repeated values establish cross-view consistency of the displayed trade records.

However, the chart views inspected in the same segment do not provide a source-complete mapping saying that any one of these entry prices is mechanically equal to a specific visible wick, body boundary, horizontal level, P-Gap boundary, AB=CD point, or other named construction.

### 3. Visible horizontal levels do not uniquely reconstruct the entry set

The worked chart contains multiple horizontal references around the trade region, including lower target/price-region references and upper risk-region references. The visible lines are consistent with the account values being in the same general price neighborhood, but the screenshots do not expose a deterministic rule assigning each entry price to one specific line or geometric anchor.

In particular, the presence of several distinct executed entries does not establish whether they represent:

- repeated executions of one canonical level;
- different candidate levels;
- sequential entries during a structure;
- manual scaling;
- separate demonstrations; or
- another platform/account representation.

No sizing or order-precedence information in the chart is sufficient to distinguish these alternatives.

### 4. The chart can identify context, but not the event-level bridge

The worked chart is explicitly marked with `SP2L`, `EMA60`, and `M1`. This confirms the intended worked-example context.

The account table and chart share the same XAUUSD price neighborhood, but the temporal/display mismatch means the chart cannot be used to identify the exact candle that generated each later history timestamp.

Therefore the following mapping remains unproven:

`visible geometry → exact entry price → activation event → history record`

## Source-resolution impact

### F8 — first important swing / selection

The finer chart inspection confirms that multiple structural/local reference points exist in the worked example. It does not establish which point is the canonical first-important swing.

**Status: selection algorithm unresolved.**

### F9 — entry vs Leg-2 start

Entry values are directly observed in executed positions, but the chart does not expose a deterministic construction connecting each entry to a specific geometric point or activation event.

**Status: executed entry state confirmed / exact entry construction and activation semantics unresolved.**

### F10 — invalidation / SL

SL values are repeatedly paired with entries in the worked account. The visible chart shows risk-region references, but the source does not establish the exact structural boundary or formula that produces each displayed SL.

**Status: explicit SL state confirmed / canonical SL construction and invalidation semantics unresolved.**

### F14 — AB=CD

The worked material explicitly teaches AB=CD, but this forensic pass does not establish which visible chart points are A/B/C/D for the executed entries or what tolerance/rounding is applied.

**Status: concept confirmed / anchors and tolerance unresolved.**

## Non-inferences deliberately rejected

This pass does **not** infer any of the following:

- Entry = a particular wick/body/open/close field;
- Entry = P-Gap boundary;
- Entry = AB=CD point;
- Entry = HL/LH by a specific algorithm;
- touch = fill;
- wick penetration = fill;
- bar close = fill;
- next-bar confirmation = fill;
- account `Time` = execution time;
- displayed line = automated order level;
- multiple entries = canonical scaling rule;
- 2X = 50% of Entry→SL;
- any specific SL formula;
- any specific AB=CD tolerance.

## Conclusion

The finer geometry pass reaches the same source-resolution boundary from a different direction:

**The worked example is sufficient to confirm observed account states and chart context, but not sufficient to reconstruct a deterministic entry formula from chart geometry alone.**

This is an important negative result because it prevents the account table from being reverse-engineered into canonical geometry merely because the displayed numbers are visually near chart levels.

## Gate impact

**Source Resolution: PARTIAL PASS — worked entry/SL states and chart context confirmed; deterministic entry-to-geometry mapping remains unresolved.**

**Frozen Geometry: BLOCKED.**

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

No backtest variant, canonical geometry, execution rule, or production behavior was changed.
