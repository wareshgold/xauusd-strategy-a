# G342 — AB=CD adversarial geometry discrimination

Date: 2026-09-12
Branch: `research/sp2l-g342-abcd-adversarial-discrimination-2026-09-12`

## Objective

Stress-test the unresolved G341 geometry hypotheses with adversarial synthetic fixtures. The purpose is to expose hidden dependence on anchor selection, price field, and structural scale without ranking or promoting any hypothesis.

## Discrimination dimensions

- Local swing candidate versus source-described deep origin.
- Wick/body/close price-field divergence.
- Parent versus nested structural scale.
- Correction reference versus fill-as-C separation.
- AB=CD projection remains a research representation only; no tolerance is introduced.

## Adversarial fixtures

### BASELINE
The G341 source-semantic sequence.

### NEAREST_SWING_DISTRACTOR
The local swing candidate is deliberately altered while source-semantic deep-origin, parent-B, correction, pending, and fill events remain unchanged. A nearest-swing implementation therefore changes its projected D while a source-anchor interpretation need not.

### PRICE_FIELD_DISCRIMINATOR
The OHLC values at source-semantic anchors are widened so wick/body/close hypotheses cannot accidentally converge.

### NESTED_PARENT_DISCRIMINATOR
Parent-B and nested-B ranges are deliberately separated to make scale selection materially affect projection.

## Guardrails

- No candidate is canonical.
- No historical data.
- No optimization or performance ranking.
- No production code.
- No AB=CD tolerance.
- No TP1/TP2 mapping.
- No claim that a synthetic result resolves source meaning.

## Gate result

**G342 = PASS — ADVERSARIAL DISCRIMINATION COVERAGE, GEOMETRY STILL UNRESOLVED**

The fixtures demonstrate that unresolved implementation choices can materially change executable geometry. This strengthens the requirement that the eventual frozen specification must obtain source evidence for the disputed dimensions rather than select a model because it is convenient or profitable.

FROZEN_GEOMETRY remains BLOCKED. DEV remains BLOCKED. VAL remains protected and Fresh Holdout remains locked.
