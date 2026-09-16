# SP2L Batch 19 — Worked-Trade Reconstruction / Non-Identifiability — 2026-09-16

## Purpose

This batch performs a forensic reconstruction of the clearest worked-trade material visible in the user-supplied primary SP2L training video. The objective is **not** to infer or promote canonical rules. Only directly observable chart/table facts and arithmetic relationships are recorded. Where the artifact does not uniquely determine a rule, the field is explicitly marked unresolved.

## Evidence handling rules

- Primary artifact: user-supplied SP2L training video, approximately 69:15.72.
- Worked-example section is shown at accelerated playback; visible overlay states 25x speed and 1-minute candles.
- Chart annotations are treated as visual evidence only; account-table numeric fields are preferred for arithmetic because they are directly readable.
- No pixel-distance measurement is promoted to a formula when visible account numbers do not uniquely establish the meaning of the annotation.
- Account screenshots may contain manual/multiple positions and therefore do not by themselves prove the canonical order state machine.
- No backtest result is used to choose among interpretations.

## Reconstruction A — 12 May 2025 bearish execution cluster

### Observable timeline

| Video frame | Approx. chart window visible | Directly observable evidence |
|---|---|---|
| 3540 | 12 May, roughly 10:25–11:45 | Bearish-side chart with several horizontal levels/annotations; account table shows four XAUUSD sell positions. |
| 3570 | 12 May, roughly 10:29–12:20 | Chart shows labels including `2x`, `E`, `1`, `2`, `3`; account table shows four sell positions with readable prices/SL/TP. |
| 3900 | 12 May, roughly 12:40–14:20 | Later chart view of a bearish structure followed by a strong rebound; account table shows a pending `sell limit` plus executed sells. |
| 3930 | 12 May, roughly 13:15–14:20 | Same trade episode; red highlighted chart region and account table with pending/filled sell orders. |
| 3960 | 12 May, later | Chart plus account-history view; order-history dialog is visible. |
| 3990 | 12 May, roughly 12:54–15:30 | Account-history table shows one pending-order row and several completed sell rows; three rows share TP 3213.37. |
| 4020 | 12 May, later | Chart shows the same marked region and subsequent recovery; account table remains visible. |

### Directly readable position records

From the clearest account-table frame (3570 / corroborated by 3990):

| Side | Entry/Price | SL | TP | Direct arithmetic | Status from screenshot |
|---|---:|---:|---:|---|---|
| Sell | 3229.08 | 3237.73 | 3213.30/3213.37 depending frame | risk = 8.65; reward to 3213.37 = 15.71; ratio ≈ 1.8168 | Executed sell |
| Sell | 3223.84 | 3235.50 | 3213.37 | risk = 11.66; reward = 10.47; ratio ≈ 0.8979 | Executed sell |
| Sell | 3228.88 | 3235.50 | 3213.37 | risk = 6.62; reward = 15.51; ratio ≈ 2.3430 | Executed sell |
| Sell | 3232.41 | 3237.80 | 0.00 | risk = 5.39; TP not set in the visible row | Executed sell |

The small TP discrepancy for the first row (`3213.30` in one view versus `3213.37` in later history) is preserved as observed rather than normalized.

### Pending-order evidence

Frame 3900/3930/3990 shows a `sell limit` row with price around `3269.88` and no SL/TP in the pending row. The same history also contains executed sells at approximately `3229.08`, `3223.84`, `3228.88`, and `3232.41`.

This establishes that the worked example visibly contains a pending sell-limit order and subsequently executed sell positions. It does **not** establish whether the pending order was filled, deleted, replaced, manually managed, or unrelated to the later executed positions. The artifact therefore does not uniquely identify the pending-order state transition.

### 2X evidence

Frame 3570 visibly labels `2x` on a horizontal level in the chart annotation. The same frame contains multiple sell entries and separate SL values. The visual location of `2x` is not sufficient to derive a unique numeric formula from the account records: the visible positions have different entries and stop distances, while the annotation is a chart-level teaching mark rather than an explicit formula/value field.

Therefore:

- `2X` is **directly confirmed as a taught concept**.
- A precise `2X = ...` price formula is **not established by this worked example**.
- The secondary 50%-distance hypothesis remains non-canonical.

### AB=CD / leg reconstruction

The chart contains a highlighted bearish region and multiple horizontal reference levels, but the screenshots do not expose an unambiguous A/B/C/D label set tied to exact candle indices and OHLC values. The account table provides execution prices and risk levels, not the required structural anchors.

Therefore the following remain unresolved for this example:

- exact A anchor;
- exact B anchor;
- exact C anchor;
- whether D is projected or observed;
- wick/body/OHLC selection;
- equality versus ratio/tolerance test;
- exact candle-selection algorithm.

## Reconstruction B — bullish SP2L teaching example around 3480s

Frame 3480 shows a bullish chart with handwritten `SP2L`, `EMA 60`, and `M1` annotations. Multiple local lower points are circled/marked and horizontal levels are drawn. The chart visually demonstrates that local lows/levels participate in the bullish structure.

What can be reconstructed directly:

- Direction: bullish teaching example.
- Timeframe: M1 is explicitly written.
- EMA context: `EMA 60` is explicitly written.
- Multiple local lows/levels are visually marked.
- A bullish SP2L concept is explicitly being illustrated.

What cannot be uniquely reconstructed:

- which marked low is the canonical first important swing when several candidates exist;
- exact Entry price activation semantics;
- exact Leg-2 start price;
- exact SL price formula/boundary;
- exact trigger candle count or touch/break/close semantics;
- exact AB=CD A/B/C/D mapping.

This example therefore strengthens the evidence for structural level marking but is **not sufficient to freeze executable geometry**.

## Reconstruction C — same bearish episode, order-history / outcome view

Frames 3990–4050 show the marked bearish region and account history after the execution sequence. Three completed sell rows show the same TP `3213.37`; several other sell rows around `3232.41` show no TP and different current prices at the snapshot time.

This provides a useful cross-check:

1. Multiple entries can coexist in the visible worked example.
2. Multiple positions can share a TP while having different entry and SL values.
3. Some positions visibly have no TP at the snapshot.
4. A pending order can appear alongside executed positions.
5. The screenshots therefore do not support a unique single-order, single-entry execution model.

This is evidence about the **worked example as presented**, not a canonical strategy rule.

## Direct arithmetic sanity checks

For the three completed sells with TP `3213.37`:

- `3229.08 → 3237.73` risk = `8.65`; `3229.08 → 3213.37` reward = `15.71`; reward/risk ≈ `1.8168`.
- `3223.84 → 3235.50` risk = `11.66`; reward = `10.47`; reward/risk ≈ `0.8979`.
- `3228.88 → 3235.50` risk = `6.62`; reward = `15.51`; reward/risk ≈ `2.3430`.

These are arithmetic relationships between visible account fields only. They are **not** evidence that the strategy's canonical TP, R-multiple, or execution rules use these ratios.

## Non-identifiability result

The worked examples materially strengthen several source concepts but do not uniquely determine the executable geometry required for a frozen strategy specification.

### Strengthened by the worked examples

- bearish and bullish SP2L examples are explicitly demonstrated;
- local structural levels/lows are visibly marked;
- pending order placement exists in the worked material;
- order deletion is visible in the broader order-placement section;
- `2X` is explicitly marked;
- multiple target/risk/entry concepts coexist in the teaching material;
- account history demonstrates multiple positions and shared TP levels;
- M1 / EMA60 context is explicitly visible in the worked section.

### Still non-identifiable from the reviewed frames

- exact first-important-swing selection;
- exact Entry activation semantics;
- exact Leg-2 start semantics;
- exact SL boundary and price convention;
- pending-order replacement/supersede/expiry/invalidation state machine;
- exact 1/2/3-candle trigger taxonomy;
- exact 2X formula, trigger, order type, fill and sizing semantics;
- exact AB=CD A/B/C/D anchors;
- AB=CD equality/ratio and numeric tolerance;
- exact bearish mathematical mirror at executable-rule level.

## Gate consequence

**Source Resolution: PARTIAL PASS — further strengthened by primary worked-example evidence.**

**Frozen Geometry: BLOCKED.** The worked examples do not uniquely identify all executable semantics, so no competing interpretation is promoted to canonical.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**

## Implementation impact

No strategy geometry, backtest logic, R semantics, fill semantics, or production BUY/SELL logic was changed as a result of this batch.

No performance-based interpretation was selected.

The next evidence target is narrower: timestamped inspection of the exact frames surrounding the first order placement, the visible `delete` action, and the 2X/risk diagram to determine whether the primary artifact contains explicit spoken or graphical semantics that can close one of the remaining blockers without inference.
