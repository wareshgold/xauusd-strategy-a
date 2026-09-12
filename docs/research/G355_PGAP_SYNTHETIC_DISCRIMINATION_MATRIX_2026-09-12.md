# G355 — P-Gap Synthetic Discrimination Matrix

Date: 2026-09-12  
Gate: SOURCE RESOLUTION → SYNTHETIC FIXTURES  
Status: **RESEARCH ONLY — no canonical geometry freeze**

## Purpose

Translate the current source-resolution boundary into deterministic synthetic fixtures that can distinguish competing interpretations of P-GAP / Pressure Gap without allowing fixture outcomes to define source meaning.

## Source-confirmed constraints carried into fixtures

- `P-GAP ↔ Pressure Gap` is source-confirmed.
- Breakout Gap, Pressure Gap, Exhaustion Gap, and Common Gap are distinct source categories.
- Generic bullish gap geometry is explicitly demonstrated as a distance between the high of the candle two bars before and the low of the current candle.
- SP2L permits at least two P-GAP timing variants: breakout → follow-through → P-GAP, and higher-lows → P-GAP.
- No source-confirmed minimum gap size, tolerance, overlap rule, wick/body convention, or executable A/B/C/D mapping exists yet.

## Fixture matrix

| ID | Synthetic condition | Competing question | Expected research classification |
|---|---|---|---|
| PG-01 | Bullish `High[i-2] < Low[i]` with clear separation | Does generic-gap geometry detect the displayed relation? | Generic-gap-positive; not automatically P-GAP |
| PG-02 | Bearish mirrored separation | Is bearish symmetry explicitly supported? | Candidate only; source confirmation still needed |
| PG-03 | Gap at movement origin, no sustained pressure context | Breakout Gap vs Pressure Gap | Breakout-gap candidate; do not relabel P-GAP |
| PG-04 | Sustained directional pressure → pause → trend bar + gap | Pressure Gap contextual identity | Pressure-gap candidate |
| PG-05 | Breakout → FT → P-GAP | Timing variant A | Source-supported SP2L variant |
| PG-06 | Higher-lows → P-GAP | Timing variant B | Source-supported SP2L variant |
| PG-07 | Wick overlap, body separation | Wick vs body endpoint convention | Discriminator; unresolved |
| PG-08 | Body overlap, wick separation | Wick vs body endpoint convention | Discriminator; unresolved |
| PG-09 | Very small positive separation | Minimum gap threshold | Threshold candidate only; unresolved |
| PG-10 | Same geometry with varying overlap | Tolerance / overlap policy | Parameter candidate only; unresolved |
| PG-11 | Pressure-like sequence near resistance + reversal | Pressure vs Exhaustion context | Context discriminator |
| PG-12 | Common-range gap with weak follow-through | Common Gap vs predictive P-GAP | Common-gap candidate; no automatic P-GAP |
| PG-13 | P-GAP visually adjacent to E-GAP | Classification boundary | Context discriminator |
| PG-14 | Same candles with alternate anchor labels | A/B/C/D dependence | Anchor hypotheses only |

## Adversarial minimal pairs

### Pair A — generic gap vs Pressure Gap

Hold candle geometry constant while changing only the surrounding pressure/context sequence. If classification changes, that demonstrates why existence of a geometric gap alone cannot define P-GAP.

### Pair B — Breakout Gap vs Pressure Gap

Hold a gap near the movement origin constant while changing sustained-pressure context. The test prevents the implementation from collapsing `Breakout Gap == P-GAP`.

### Pair C — wick/body ambiguity

Hold the visible gap constant while making wick extremes overlap but bodies separate, then reverse the condition. Any rule choosing wick/body must remain a hypothesis until source evidence labels it.

### Pair D — threshold ambiguity

Use identical structure with gap distances ε, small, medium, and large. No threshold may be selected from fixture pass/fail preference.

### Pair E — timing ambiguity

Construct both source-described SP2L timing variants and ensure an implementation does not require P-GAP to precede breakout/FT in every case.

## Assertions permitted now

1. A generic-gap detector may be tested against the explicitly taught generic relation.
2. A semantic P-GAP label may be represented as Pressure Gap.
3. Event-order fixtures may represent both source-described SP2L timing variants.
4. Candidate classifiers may be compared without promotion.

## Assertions forbidden now

- `P-GAP = generic gap formula` as canonical rule.
- Any minimum gap size.
- Any overlap/tolerance percentage.
- Wick-only or body-only endpoint semantics.
- A/B/C/D anchors.
- Fill price = C.
- Fixed TP1/TP2 numeric mapping.

## Gate decision

**Synthetic fixture design: READY.**  
**Geometry freeze: BLOCKED.**

The matrix is deliberately constructed to expose unresolved dimensions rather than choose among them using performance.
