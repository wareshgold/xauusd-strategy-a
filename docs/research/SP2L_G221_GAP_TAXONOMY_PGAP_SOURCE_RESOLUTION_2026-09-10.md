# SP2L G221 — Gap Taxonomy / P-Gap Source Resolution

Date: 2026-09-10  
Stage: SOURCE RESOLUTION  
Status: RESEARCH-ONLY / NO GEOMETRY FREEZE

## 1. Source asset

User-supplied source video:
`gap پورصمدی دوره جامع.mp4`

Observed media properties:
- duration: ~1955.79 s (~32:35.8)
- video: H.264, 854x480, 30 fps
- audio: AAC
- SHA-256: `3345965612b52ebbefffe724f7bd16cc1085bafa29dc612f29a4d725e017c0a6`

Frame convention for this pass: nominal frame = round(t * 30), with timestamp recorded alongside frame references where needed.

## 2. High-value direct source evidence

### 2.1 Gap definition

Around 19:00–19:20 (frames approximately 34,200–34,600), the course explains a three-candle-style gap observation in Persian. The displayed text states, in substance, to pay attention to the distance between the high of the candle two candles before and the low of the current candle; if there is a distance, a gap has formed.

This is direct source evidence that the course uses a candle-indexed price separation concept for identifying a gap. The exact bullish/bearish mirror and whether this definition is intended universally or only for the illustrated direction must still be captured from the complete sequence before implementation.

Important: this does NOT establish that SP2L P-Gap is a generic three-candle FVG. It is only the course's general Gap teaching at this point.

### 2.2 Gap taxonomy

At approximately 19:40 (frame ~35,400), a slide titled `انواع گپ` (Types of Gaps) lists four categories:

1. `بریک اوت` — Breakout
2. `فشار` — Pressure
3. `خستگی` — Exhaustion
4. `معمولی` — Ordinary

The slide is direct visual source evidence from the supplied course.

### 2.3 Breakout Gap

Immediately after the taxonomy slide, around 20:00 (frame ~36,000), a definition slide states in substance:

`زمانیکه یک گپ در ابتدای یک حرکت ایجاد می شود، آن یک بریک اوت گپ است`

Meaning: when a gap is created at the beginning of a move, it is a Breakout Gap.

This is a direct source definition and is materially relevant to SP2L because the SP2L source independently marks `P-GAP` as associated with a valid breakout (`Valid BO = P-Gap`).

However, this pass does NOT yet establish that the course's `Breakout Gap` is formally identical to the SP2L source's `P-Gap`. The terminology is related and strongly suggestive, but the equivalence must be explicitly corroborated rather than inferred.

### 2.4 Pressure Gap

Around 22:30–23:00 (approximately frame 40,500–41,400), a definition slide titled `گپ فشار` describes a pressure-gap condition in which, after roughly 1–3 candles, pressure stops for a period and this is associated with the probability of the trend starting/continuing again increasing. Exact semantic boundaries should be taken from the full narrated sequence if needed.

This demonstrates that the creator distinguishes Gap types by their location/function in a price movement, not merely by a generic geometric three-candle pattern.

### 2.5 Exhaustion Gap

Around 25:00 (approximately frame 45,000), a slide titled `گپ خستگی` describes an exhaustion gap. The text states in substance that if buying pressure continues for more than about 10 candles, near resistance a good candlestick/turning condition can form and price may reverse from the gap.

The exact numeric/structural language should not be promoted into Strategy A because it belongs to the general Gap course, not yet to the SP2L rule specification.

### 2.6 Ordinary Gap

Around 28:40–29:30 (approximately frames 51,600–53,100), the course presents `گپ عادی` (Ordinary Gap). A definition slide states in substance that an ordinary gap is any gap whose value is usually followed/covered by price and that it is commonly observed in trading ranges.

Again, this is general Gap taxonomy, not a frozen SP2L rule.

## 3. Critical SP2L interpretation

The new evidence materially changes the research map for B1.

Previously:
- SP2L source: `P-GAP` is explicitly associated with a valid breakout.
- Exact P-Gap geometry: unresolved.

Now:
- The creator's broader Gap course explicitly distinguishes a `Breakout Gap` from Pressure, Exhaustion, and Ordinary gaps.
- The Breakout Gap is defined by occurring at the beginning of a move.
- This is semantically consistent with the SP2L use of P-Gap as a valid-breakout-associated condition.

Therefore the current evidence status should be upgraded from merely `P-Gap = first-class source term` to:

**P-Gap is strongly correlated with the creator's Breakout Gap concept, but equivalence is NOT frozen.**

## 4. What this does NOT prove

This pass deliberately does not infer:

- P-Gap = generic FVG
- P-Gap = any three-candle imbalance
- P-Gap = the exact high/low separation in every market condition
- exact participating candle indexes for SP2L
- wick-vs-body rule for SP2L P-Gap
- overlap/non-overlap tolerance
- minimum gap size
- fill/mitigation rule
- bullish/bearish executable formula

The general course's gap definition is evidence about the creator's terminology and conceptual taxonomy, not by itself a frozen Strategy A geometry.

## 5. Highest-value next source pass

The next pass should return to the original SP2L video and locate the earliest/clearest P-Gap examples where the same candle-indexed geometry can be compared against the Gap-course definition.

Required comparison:

`General Gap course -> Breakout Gap -> SP2L P-Gap -> Valid BO`

The goal is to determine whether the SP2L P-Gap is simply the creator's Breakout Gap applied to the SP2L breakout structure, or whether SP2L imposes an additional geometric restriction.

If an SP2L frame uniquely shows the participating candles and boundaries, only then can B1 move toward frozen executable geometry.

## 6. Gate result

SOURCE RESOLUTION: **PROGRESS — B1 semantic evidence strengthened**

FROZEN GEOMETRY: **BLOCKED**

No production code changed.
No backtest/optimization evidence was used to interpret the source.
