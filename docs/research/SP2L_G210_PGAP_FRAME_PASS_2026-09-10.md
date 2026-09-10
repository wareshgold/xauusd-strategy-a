# SP2L G210 — P-Gap Fine-Grained Frame Pass

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## Source asset inspected

The registered source video was inspected directly at 30.000 fps using the persisted source identity `SP2L_FULL_2026-09-08`.

The source registry defines the nominal frame convention as `round(t × 30)` and requires timestamp + frame to be recorded together.

## Fine-grained observations

### 30:00–31:30 — spike/P-Gap construction lead-in

The source progressively annotates a bullish candle sequence with arrows and circles. Around 31:00–31:30, a small candle below a large bullish candle and a subsequent candle are explicitly highlighted. The visual sequence is useful evidence that the teacher is distinguishing particular candle relationships, but the frame alone does not uniquely label each candle as a formal OHLC participant of P-Gap.

Observed reference frames:

- 30:00 → frame 54,000: annotated bullish candle sequence; multiple arrows/marks.
- 30:30 → frame 54,900: additional candle annotations.
- 31:00 → frame 55,800: upper/lower candles circled/pointed to in the illustrated sequence.
- 31:20 → frame 56,400: close view of the highlighted candle relationship.
- 31:30 → frame 56,700: same relationship remains visible.

Interpretation: strong evidence for source-specific candle/spike grammar; **not sufficient to freeze a numeric P-Gap formula**.

### 31:48–32:18 — explicit P-GAP annotation

The teacher writes `P-GAP` above the illustrated examples and subsequently adds a continuation-style annotation. The source therefore directly establishes the term P-GAP in this candle-construction discussion.

Observed reference frames:

- 31:48 → frame 56,940: P-GAP annotation begins.
- 31:54 → frame 57,420: P-GAP text/arrow visible.
- 32:00 → frame 57,600: P-GAP prominently annotated.
- 32:06 → frame 57,780: P-GAP circled.
- 32:12 → frame 57,960: P-GAP plus continuation annotation visible.
- 32:18 → frame 58,140: final annotated state before the next construction.

Interpretation: **direct source evidence that P-GAP is a named source concept associated with the illustrated candle construction**. The visible annotations still do not uniquely specify participating candle indices and exact OHLC boundary equations.

### 35:45–36:05 — pre-existing shaded P-Gap examples

Before the later numbered annotations are added, the slide already contains several shaded rectangular regions behind bullish candle constructions, while a separate construction is marked with a red X. The later `Valid BO = P-Gap` text is therefore attached to a visual distinction between accepted and rejected constructions.

Reference frames:

- 35:45 → frame 64,050: multiple bullish constructions; shaded regions visible; rejected example marked red X.
- 35:50 → frame 64,200: same structure, shaded regions persist.
- 35:55 → frame 64,350: shaded regions persist.
- 36:00 → frame 64,800: `Valid BO = P-Gap` visible.
- 36:05 → frame 64,950: numbered-example annotation begins.

Interpretation: **direct/strong evidence that the shaded region is the visual representation used for P-Gap in this teaching example and that P-Gap is tied to breakout validity**. Exact mathematical boundaries remain unresolved.

### 36:07–36:16 — three numbered examples

The teacher explicitly numbers three illustrated constructions `1`, `2`, and `3` and circles them. P-Gap shading is visibly associated with the examples, while the red-X construction remains separate.

Reference frames:

- 36:07 → frame 64,?00 (nominal `round(2167 × 30)` = 65,010): numbered examples begin.
- 36:10 → frame 65,100: three examples clearly numbered/circled.
- 36:12 → frame 65,160: three examples clearly visible; P-Gap shaded regions visible.
- 36:14 → frame 65,220: same.
- 36:16 → frame 65,280: same before transition.

Interpretation: direct evidence that the source treats multiple visual constructions as examples in its P-Gap/breakout explanation. This does **not** by itself prove that all three share one uniquely recoverable OHLC formula.

## Important correction to prior frame bookkeeping

For exact deterministic work, timestamps must be converted using the registered convention `round(t × 30)`. The nominal frame for 36:07 is therefore 65,010; the registry's previously listed 36:10/65,100 and 36:00/64,800 remain consistent.

## B1 decision after this pass

**B1 remains SOURCE-UNRESOLVED.**

What is now stronger:

1. P-GAP is explicitly named in the 31:48–32:18 construction discussion.
2. The later slide explicitly states `Valid BO = P-Gap`.
3. Shaded regions are used as the visual P-Gap representation in accepted examples.
4. A red-X example is visually contrasted with the accepted constructions.
5. The source presents multiple P-Gap constructions rather than a single accidental chart shape.

What is still missing for a canonical executable rule:

- uniquely identified participating candle indices;
- exact OHLC/range boundaries of the shaded region;
- whether the boundary uses wick, body, high/low, open/close, or another source-defined level;
- explicit overlap/non-overlap condition;
- exact breakout/follow-through timing relative to the P-Gap;
- deterministic invalidation/expiry semantics.

## Non-inference boundary

This pass does **not** establish that P-Gap equals:

- a generic three-candle imbalance;
- FVG;
- any particular wick-to-wick or body-to-body formula;
- a fixed percentage/point threshold;
- a backtest-selected candle pattern.

The correct gate action is continued source inspection, not geometry freezing.

## Next source pass

Proceed to the 36:20–37:10 sequence and then 38:30–40:10, with special attention to whether the teacher's hand-drawn arrows/levels explicitly connect P-Gap to A/B/C, the pending-limit entry, and SL. If no unique mapping appears, retain B1/B2/B3 as unresolved.
