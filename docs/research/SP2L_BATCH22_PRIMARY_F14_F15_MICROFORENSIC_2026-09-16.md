# SP2L Batch 22 — Primary F14/F15 Micro-Forensic Pass — 2026-09-16

## Scope

This batch narrows the forensic review to the primary training artifact around the AB=CD teaching sequence and the later bullish/bearish worked material. The goal is to determine whether the primary artifact uniquely defines AB=CD anchors or the executable bearish mirror. It does not promote geometry from visual similarity or account outcomes.

## Evidence handling

- Primary artifact: user-supplied SP2L training video, approximately 69:15.72.
- Frame timestamps below refer to the extracted video timeline and are approximate to the sampled frame.
- Handwritten annotations are treated as instructional visual evidence, not as machine-readable formulas unless their meaning is explicit.
- No pixel measurement is converted into a canonical price formula.
- No account-table outcome is used to choose among geometric interpretations.

## F14 — AB=CD

### Direct primary evidence

At approximately 36:30–37:00 (frames around 2190–2220), the teaching slide explicitly shows a handwritten `AB=CD` annotation above a bullish candle example. The same sequence includes `Valid BO = P-Gap` on the slide. At frame 2220, additional handwritten marks include `1m` and `5m`; these are preserved as visible annotations and are not interpreted as a geometry formula.

The later worked diagram sequence (approximately 45:30–47:00; frames around 2730–2820) visually distinguishes a first-leg/second-leg structure and separately labels `Entry`, `TP1`, `TP2`, and `SL`. This strengthens the evidence that the two-leg construction is used as a teaching/risk framework.

### What this closes

The primary artifact directly supports these source-level concepts:

1. SP2L is taught as a Spike / 2-Leg structure.
2. `AB=CD` is explicitly written in the teaching material.
3. A breakout validation concept is shown in the same teaching sequence (`Valid BO = P-Gap`).
4. Entry, TP1, TP2, and SL are represented as distinct levels in the worked diagram.

### What remains unresolved

The artifact still does not uniquely identify:

- A anchor candle/index;
- B anchor candle/index;
- C anchor candle/index;
- D as projected versus observed point;
- wick versus body versus open/close selection;
- whether equality is exact price-distance equality or another ratio/normalization;
- numeric tolerance, rounding, or minimum/maximum deviation;
- whether the same anchor algorithm applies across all examples.

The visual sequence therefore **does not justify freezing an executable AB=CD formula**.

## F15 — bearish mirror

### Direct primary evidence

The worked section around 12 May 2025 contains an explicit bearish execution episode. Frame 3510 shows a bearish-side structure on the chart with multiple horizontal levels and handwritten markings. Frame 3630 shows the subsequent account table with four XAUUSD sell positions, including visible entries near `3229.08`, `3223.84`, `3228.88`, and `3232.41`, with corresponding SL values and TP values in the visible table.

The worked material therefore directly demonstrates that the SP2L teaching includes bearish/sell-side execution examples, not only bullish diagrams.

### What this closes

- Bearish/sell-side SP2L execution is directly demonstrated in the primary artifact.
- The bearish example uses explicit entry and SL fields in the account display.
- Multiple sell positions can coexist in the demonstrated worked example.

### What remains unresolved

The primary artifact does not uniquely establish a mathematical bearish mirror for every bullish executable rule. In particular it does not uniquely determine:

- the bearish swing-selection algorithm;
- exact LH/high selection;
- bearish Entry activation semantics;
- bearish SL boundary convention;
- bearish trigger taxonomy;
- whether AB=CD anchors are transformed by a strict sign/mirror operation or reconstructed independently;
- bearish 2X activation/order/fill semantics.

Therefore F15 remains **directionally source-confirmed but executable geometry unresolved**.

## Cross-check: F14 ↔ F15

The combined evidence supports a stronger conceptual chain:

`Spike → 2 Leg → AB=CD concept → Entry/SL/targets → bullish and bearish worked examples`

But it does not establish a deterministic mapping from that conceptual chain to candle indices and OHLC values. In particular, the existence of both directions does not by itself prove mathematical symmetry at the executable-rule level.

## Non-identifiability decision

This micro-forensic pass did **not** close F14 or F15 for Frozen Geometry.

The correct research state is:

- **F14:** SOURCE-CONFIRMED CONCEPT / PRIMARY ARTIFACT EXPLICIT `AB=CD` / ANCHORS + TOLERANCE UNRESOLVED.
- **F15:** SOURCE-CONFIRMED BEARISH EXECUTION / EXACT MIRROR GEOMETRY UNRESOLVED.

This is an evidence boundary, not a negative statement about how the strategy may work in practice.

## Implementation impact

- No Strategy A geometry changed.
- No backtest variant was selected.
- No fill semantics were invented.
- No R semantics were changed.
- No production BUY/SELL logic was introduced.
- 125R observation remains untouched.

## Next evidence target

The remaining high-value source-resolution targets are now F8/F12 and the executable parts of F11/F13. For F14, further progress requires an authoritative artifact that explicitly maps A/B/C/D to observable candle/swing prices and states the equality/tolerance condition. For F15, closure requires explicit bearish construction semantics rather than visual symmetry alone.

## Gate

**Source Resolution: PARTIAL PASS — strengthened.**

**Frozen Geometry: BLOCKED.**

**Untouched Validation: LOCKED.**

**Robustness/Stability: LOCKED.**

**Fresh Holdout: LOCKED.**

**Production: OFF.**

**125R: UNTOUCHED.**
