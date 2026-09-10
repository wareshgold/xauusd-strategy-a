# SP2L G213 — First-Four-Trades Order-Panel Evidence Pass

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## 1. Purpose

This pass moves from the May-13 walkthrough to the **first live-trading/order-panel sequence** near 21:20–24:00 of the supplied source video. The objective is not to reverse-engineer a rule from chart appearance, but to record what the source actually displays when an order is active and when the teacher annotates the setup.

The source video's registered frame convention is `round(t × 30)` at 30 fps. All frame references below use that convention.

## 2. External source-index corroboration

The public source description lists, in order, `نحوه اوردگذاری با این استراتژی SP2L` (how to place orders with SP2L), `نحوه و دلیل ورود در 2x` (how/why to enter at 2x), and later `آموزش دقیق ۴ معامله ی ابتدای ویدیو` (detailed teaching of the four initial trades). This is useful provenance for treating the early order-panel sequence as a deliberate source teaching section, but it does not itself define the numerical geometry.

## 3. Trade sequence observations

### 21:20–21:35 — channel / breakout lead-in

The chart shows a manually drawn converging/downward channel around the preceding price action. Around 21:30–21:35 the teacher marks the upper/lower channel boundaries and highlights the downward break area with blue arrows/marks.

Reference frames:

- 21:20 → frame 38,400
- 21:25 → frame 38,550
- 21:30 → frame 38,700
- 21:35 → frame 38,850

Interpretation: this is source evidence for context/range → breakout/follow-through discussion. It is not sufficient to define a canonical channel formula or a numeric trigger.

### 21:40 — first clearly visible order-panel state

The chart now displays a measured structure with horizontal labels including `0.0`, `2x`, `E`, `1`, and `2`. The order panel below shows an active price/SL/TP state. The visible row includes approximately:

- Price: `3229.08`
- S/L: `3237.12`
- T/P: `3213.44`
- current/market Price column: approximately `3224.67`

The screenshot therefore establishes that the source uses an explicit entry-related level (`E`), a `2x` level, and separate SL/TP order fields in the trading terminal.

Reference frame:

- 21:40 → frame 39,600

Important boundary: the screenshot alone does **not** uniquely prove which of `E` or `2x` is the source's canonical pending-limit anchor, nor does it identify the A/B/C/D construction behind the measured levels. It also does not prove that the visible `2x` label is mathematically identical to a particular multiple of risk.

### 22:00–22:30 — same position evolves

At 22:00 the same order-panel family remains visible with the first row showing approximately `Price 3229.08`, `S/L 3237.12`, `T/P 3213.44`, while the profit value changes as price evolves. At 22:30 the same order remains visible and the profit has changed again.

Reference frames:

- 22:00 → frame 39,600
- 22:30 → frame 40,500

The order-panel evidence is important because it demonstrates a real pending/active trade lifecycle with independently specified SL and TP prices. It does not by itself resolve the source geometry that generated those values.

### 23:00 — multiple order rows and repeated 0.0 / 2x / E / 1 / 2 labels

The chart again shows measured horizontal levels. The labels `0.0`, `2x`, `E`, `1`, and `2` are visible at different price levels. The order panel now contains multiple rows, including the previously observed price/SL family and additional rows.

Reference frame:

- 23:00 → frame 41,400

The presence of multiple rows demonstrates that the source is capable of holding multiple order/position states in the walkthrough. It still does not establish a deterministic rule for when an additional order is allowed or whether the rows represent separate attempts, scaling, or another terminal state.

### 24:00 — three visible order rows

At 24:00 the terminal shows three visible order rows with distinct prices/SL/TP states and negative current profit values. The chart still displays `0.0`, `2x`, `E`, `1`, and `2` reference labels.

Reference frame:

- 24:00 → frame 43,200

This is strong source evidence that order placement, SL, TP, and measured target/reference levels are all part of the practical SP2L execution walkthrough.

## 4. What this pass strengthens

### Entry / B2

Strengthened:

1. The source uses an explicit entry-related label `E`.
2. The source simultaneously displays a `2x` reference level.
3. The source uses real terminal order fields with explicit numeric prices.
4. The public source index explicitly calls out both order placement and the reason for entering at `2x`.

Still unresolved:

- whether canonical Entry is exactly the level labelled `E`, exactly `2x`, or a relationship between them;
- how the displayed levels are calculated from the preceding spike/leg;
- whether the source's `2x` notation is a geometric projection, a retracement level, or another source-specific measurement;
- exact candle anchors;
- whether fill price equals C.

Therefore **B2 remains SOURCE-UNRESOLVED at executable geometry**.

### Structural SL / B3

Strengthened:

- the terminal explicitly carries an SL price independently from Entry and TP;
- the chart's measured structure also shows a stop-side reference (`0.0` in the displayed measurement) above/beyond the short setup.

Still unresolved:

- exact source definition of the structural invalidation boundary;
- wick versus body treatment;
- whether a buffer is used;
- how the numeric SL in the terminal is derived from the source drawing.

Therefore **B3 remains SOURCE-UNRESOLVED at executable geometry**.

### Leg 2 / TP / B6

Strengthened:

- the source explicitly displays TP in the terminal;
- the chart displays `1` and `2` levels below the short setup, consistent with a staged target/projection illustration;
- the source index independently identifies the `2x` entry discussion and later TP/target discussion.

Still unresolved:

- exact TP formula;
- exact relationship of levels `1` and `2` to Leg 1 / Leg 2;
- whether the terminal TP corresponds to `2`, `2x`, AB=CD, a round level, or another source-defined target;
- TP1/TP2 precedence and execution semantics.

Therefore **B6 remains SOURCE-UNRESOLVED at executable geometry**.

## 5. Important correction: frame bookkeeping

Earlier G211 contained incorrect frame numbers for the 49:00+ May-13 walkthrough because minute/second values were accidentally multiplied as if the minute component were already seconds. The correct convention is `round(total_seconds × 30)`.

Examples:

- 49:00 = frame `88,200`
- 49:10 = frame `88,500`
- 49:20 = frame `88,800`
- 49:30 = frame `89,100`
- 50:00 = frame `90,000`
- 54:00 = frame `97,200`

This G213 record uses the corrected convention and should be treated as the authoritative frame-index convention for subsequent work.

## 6. Non-inference boundary

This pass does **not** promote any of the following to canonical rules:

- Entry = E by label alone;
- Entry = 2x by label alone;
- Entry = C;
- SL = a particular wick/body level;
- TP = 2R;
- TP = level `2` by label alone;
- 2x = generic Fibonacci/extension formula;
- a specific channel formula;
- scaling/multiple-entry logic;
- any MA filter visible on the chart.

The numeric order-panel values are evidence of source execution, not sufficient by themselves to define the generating geometry.

## 7. Gate decision

**SOURCE RESOLUTION remains BLOCKED at executable geometry.**

This pass materially strengthens the evidence for real pending/active order mechanics and for the importance of the source's `2x` concept. It does not yet uniquely resolve the formula/anchor behind `E`, `2x`, SL, or TP.

The next source-resolution step should therefore focus on the **audio/text explanation immediately surrounding the 21:40–24:00 order sequence**, and then cross-reference those statements with the later section explicitly titled around `2x` entry and the detailed four-trade explanation. If source text uniquely maps the labels to price anchors, that mapping can then be promoted to the evidence ledger; otherwise the geometry stays `UNRESOLVED`.
