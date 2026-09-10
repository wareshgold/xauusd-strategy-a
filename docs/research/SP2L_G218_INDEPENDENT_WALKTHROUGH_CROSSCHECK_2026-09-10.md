# SP2L G218 — Independent Walkthrough Cross-Check

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## 1. Objective

G217 established a strong visual mapping in the first order state: `E` aligns with the terminal Entry price, `0.0` aligns with the terminal SL, and `2x` is consistent with the midpoint between them.

This pass tests whether that structure is merely an artifact of one terminal state or whether the source repeats the same measurement construction across additional setups/trade examples.

## 2. Additional source region inspected

Two independent regions were inspected:

1. The continuation of the initial May-12 order walkthrough around 24:20–24:40, where multiple order rows and multiple measurement objects coexist.
2. The later May-13 walkthrough around 49:30–54:30, where several separate bullish SP2L examples are shown with repeated green entry/target annotations and repeated measurement/level marks.

The May-13 section is explicitly identified by the source walkthrough as XAUUSD M1 / 13 May 2025.

## 3. May-12 multi-row state

At approximately 24:20–24:40 the terminal still contains multiple order rows while the chart shows more than one measurement object. A representative frame at `t=1460s` (24:20) shows:

- terminal row A: Entry/Price `3229.08`, SL `3237.12`, TP `0.00` in that instantaneous state;
- terminal row B: Entry/Price `3223.84`, SL `3235.50`, TP `3213.33`;
- terminal row C: Entry/Price `3228.88`, SL `3235.50`, TP `3213.45`;
- multiple chart measurement objects with repeated `0.0`, `2x`, `E`, `1`, and `2` labels.

The first row's displayed TP differs from the later `3213.44` state because the order lifecycle changes over time. This is another reason not to infer a universal TP formula from one terminal snapshot.

## 4. What can be independently cross-checked

The repeated chart construction is not limited to the single 21:40 screenshot. At 24:20 the chart contains multiple measurement objects simultaneously, and the labels recur in the same semantic order: `0.0`, `2x`, `E`, followed by target-side levels `1` and `2` where the full object is visible.

This strengthens the interpretation that these labels are part of a reusable source measurement convention rather than arbitrary one-off annotations.

However, the May-12 frame does **not** provide a clean one-to-one numeric mapping for every measurement object to every terminal row. Therefore this pass does not claim that rows B/C are individually proven to map to particular `E` lines solely from that screenshot.

## 5. May-13 independent examples

The later May-13 walkthrough shows several distinct bullish SP2L examples rather than one continuous order state. Representative frames include:

- `49:30` / frame `89,100` — multiple bullish continuation examples with green setup/target boxes;
- `50:30` / frame `90,900` — repeated green entry/target regions and source annotations;
- `51:30` / frame `92,700` — additional independent example sequence;
- `52:30` / frame `94,500` — repeated setup geometry;
- `53:30` / frame `96,300` — chart explicitly shows `0.0`, `2x`, `E` and target-side levels together with a green target region.

These examples are useful because the same visual vocabulary is reused across separate market structures. They do not, by themselves, expose enough numeric price data to calculate exact Entry/SL/2x values, so they are corroborative rather than executable geometry evidence.

## 6. Important negative finding

The independent May-13 walkthrough does **not** justify promoting the following to canonical rules:

- `1 = 1R`;
- `2 = 2R`;
- `2 = TP`;
- TP always equals 1R;
- any particular relation between green target-box size and the chart level labels.

In fact, the May-12 terminal states contain different TP distances for different rows, so the source clearly contains more than one practical order/target state. The official creator page separately describes a default 1:1 TP, but that does not override the raw terminal evidence or prove that every displayed order row is a default single-entry example. citeturn0search0

## 7. Evidence update

### B2 — Entry

`E ↔ terminal Entry` remains a **STRONG SOURCE-CORRELATED CANDIDATE**, because the first order state provides direct numeric alignment and later frames repeat the same label construction.

### B3 — Structural SL

`0.0 ↔ terminal SL` remains a **STRONG SOURCE-CORRELATED CANDIDATE**, with the first order state providing direct numeric alignment.

The exact candle/wick/body construction of the SL remains unresolved.

### 2x

The midpoint interpretation remains the strongest current candidate:

`2x = midpoint(Entry, SL)`

It is corroborated by multiple order states and by the official creator-page description of a secondary entry at 50% of the Entry→SL distance. citeturn0search0

It remains **NOT FROZEN** because the source video transcript has not been recovered and the raw video does not yet contain a uniquely readable verbal definition tying the label to the arithmetic.

### B6 — Leg 2 / targets

Still unresolved. The repeated `1` and `2` labels prove a reusable target/projection vocabulary, but not the exact formula or anchor relationship.

## 8. Gate decision

**SOURCE RESOLUTION remains BLOCKED at executable geometry.**

The independent walkthrough cross-check increases confidence that the `0.0 / 2x / E / 1 / 2` stack is a reusable source convention and not a one-off annotation. It does not yet uniquely resolve the underlying candle anchors or the target formula.

The next highest-value investigation is therefore to locate a later example where the source simultaneously exposes a clean measurement stack and an explicit numeric order/price panel, or to recover authoritative source text explaining the labels. If neither is available, the geometry must remain candidate-level rather than being frozen from visual repetition alone.
