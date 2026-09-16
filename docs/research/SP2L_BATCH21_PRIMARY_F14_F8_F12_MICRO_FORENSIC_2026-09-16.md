# SP2L Batch 21 — Primary F14/F8/F12 Micro-Forensic Pass — 2026-09-16

## Scope

This batch inspects the dense primary-artifact sequence around the SP2L teaching diagrams at approximately 36:00–44:00. The goal is to extract only source-visible semantics and to test whether F14 (AB=CD), F8 (swing selection), or F12 (breakout/trigger) can be uniquely closed.

No formula is promoted from visual convenience. No backtest result is used to select an interpretation.

## F14 — AB=CD: what the primary artifact actually shows

### Direct observations

- Around frame 2190, the teaching slide visibly writes **`AB=CD`** above a bullish candle sequence.
- Around frame 2220, the same `AB=CD` annotation remains visible. Additional handwritten notes include `1M` and `5M`; these are recorded as visible annotations only and are not interpreted as a canonical timeframe rule.
- Around frame 2250, the artifact shows a hand-drawn two-leg price path with two visually similar impulse segments separated by a correction.
- Around frames 2280–2310, the artifact returns to a bullish candle sequence and marks lower structural points/levels while the text **`Valid BO = P-Gap`** remains visible.

### What this closes

The primary artifact now directly supports the following source-level statements:

1. **AB=CD is explicitly taught as part of SP2L.**
2. The teaching diagram visually represents a two-leg structure in which the two impulse segments are intended to correspond.
3. The artifact therefore provides stronger primary evidence for a **two-leg symmetry/equality concept** than the earlier indexed secondary material alone.

### What remains unresolved

The artifact does **not** provide enough explicit labeling to uniquely identify:

- A as a specific candle price/point;
- B as a specific candle price/point;
- C as a specific candle price/point;
- D as a projected or observed point;
- whether each anchor uses wick extreme, candle body, open, close, or a structural swing;
- whether `AB=CD` means exact price-distance equality, equality within a tolerance, a ratio, or another source-defined comparison;
- the numeric tolerance or rounding convention;
- the exact candle-index selection procedure when multiple candidate pivots exist.

The hand-drawn path in frame 2250 is conceptual geometry; it does not contain numeric price coordinates from which a deterministic OHLC formula can be recovered.

### F14 determination

**SOURCE-CONFIRMED CONCEPT / PRIMARY ARTIFACT STRENGTHENED / A-B-C-D ANCHORS UNRESOLVED / EQUALITY-TOLERANCE UNRESOLVED.**

No canonical AB=CD formula is frozen.

## F8 — swing/level selection

### Direct observations

- Around frame 2310, several lower points under successive bullish candles are explicitly marked with turquoise dots/short marks.
- Around frame 2340, the same bullish structure contains multiple horizontal reference levels, a visible `BO` annotation, and a handwritten `Buy Limit` note.
- Around frame 2490, a horizontal level is explicitly labeled `Buy`, with a separate lower horizontal mark labeled `SL`.

### Determination

These frames strengthen that local structural lows/levels are actively used in the teaching diagram and that the selected entry/risk levels are distinct visual objects.

However, when multiple local lows are visible, the artifact still does not uniquely state an algorithm such as first qualifying low, latest qualifying low, highest/lowest swing under a specific condition, or another deterministic selection rule.

**F8 remains unresolved at executable selection level.**

## F12 — breakout / trigger evidence

### Direct observations

- Around frame 2190–2280, the slide explicitly states **`Valid BO = P-Gap`**.
- Around frame 2340, a `BO` annotation is placed over the bullish sequence and a `Buy Limit` note is visible beside the structure.
- Around frame 2370, the horizontal level is explicitly labeled **`Buy Limit`**.
- Around frame 2400, the same horizontal level is shown as an order line extending across the chart.
- Around frame 2460, the teaching sequence again shows the marked level and annotations associated with order management.
- Around frame 2490, the level is labeled `Buy` while the lower risk line is labeled `SL`.

### What this strengthens

The primary artifact supports a chain containing:

**breakout validation concept → structural level → pending Buy Limit order → separate SL level**.

It also directly supports the previously observed existence of a P-Gap/valid-breakout concept.

### What remains unresolved

The artifact still does not uniquely specify:

- whether `BO` requires an intrabar breach or candle close;
- exact P-Gap numeric definition;
- whether one, two, or three candles constitute the trigger/confirmation family;
- whether the order is placed before or after a particular confirmation event in every case;
- touch versus break versus close semantics for level activation;
- exact retest/fill semantics;
- whether the displayed `Buy Limit` is the canonical entry level or an illustrative order-placement example.

**F12 remains SOURCE-CONFIRMED CONCEPT / EXACT EXECUTABLE TAXONOMY UNRESOLVED.**

## Cross-fixture result

The same short primary sequence now gives a coherent source-visible teaching chain:

1. `AB=CD` is explicitly written.
2. A bullish two-leg/correction structure is drawn.
3. Several local lows/levels are marked.
4. `Valid BO = P-Gap` is explicitly written.
5. A `Buy Limit` order level is shown.
6. Later frames distinguish `Buy` and `SL` levels.

This is materially stronger source evidence than isolated secondary descriptions. It still does not uniquely determine the low-level geometry needed for a frozen deterministic implementation.

## Non-canonical items preserved

- No A/B/C/D anchor formula.
- No AB=CD tolerance.
- No wick/body/OHLC anchor convention.
- No P-Gap numeric formula.
- No trigger-candle taxonomy.
- No touch/break/close execution rule.
- No fill semantics.
- No swing-selection algorithm.
- No performance-based interpretation.
- No production BUY/SELL logic.
- 125R remains untouched.

## Gate consequence

**Source Resolution: PARTIAL PASS — materially strengthened by direct primary visual evidence.**

**Frozen Geometry: BLOCKED.** F14 is conceptually confirmed but its deterministic anchors/tolerance remain unresolved; F8 and F12 likewise remain unresolved at executable-rule level.

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**
