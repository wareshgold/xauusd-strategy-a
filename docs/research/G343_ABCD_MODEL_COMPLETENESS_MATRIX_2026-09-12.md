# G343 — AB=CD Model Completeness Matrix

Date: 2026-09-12

## Gate

**G343 = PASS — KNOWN MODEL SPACE EXHAUSTIVELY REPRESENTED, GEOMETRY STILL UNRESOLVED**

This gate is a research-coverage gate only. It does not freeze any executable A/B/C/D geometry and does not authorize historical optimization, validation, or production promotion.

## Purpose

G340 established the source-resolution boundary: repeated inspection of the existing authoritative material cannot manufacture an executable A/B/C/D rule where the source does not explicitly provide one. G341 represented concrete competing AB=CD interpretations, and G342 added adversarial fixtures to ensure the important dimensions actually discriminate between those interpretations.

G343 makes the known model space explicit as a finite Cartesian product so that a later research result cannot accidentally omit an already-identified interpretation dimension.

## Enumerated dimensions

The matrix spans:

- **A selector (3):** `SOURCE_DEEP_ORIGIN`, `FIRST_BREAKOUT_CANDLE`, `NEAREST_SWING`
- **B selector (2):** `PARENT_B`, `NESTED_B`
- **C selector (2):** `SOURCE_CORRECTION_REFERENCE`, `FILL_AS_C`
- **Price field (6):** `HIGH`, `LOW`, `OPEN`, `CLOSE`, `BODY_HIGH`, `BODY_LOW`
- **Scale (2):** `PARENT`, `NESTED`
- **Projection (1):** `AB_EQ_CD_TRANSLATION`

Therefore the explicit matrix contains:

`3 × 2 × 2 × 6 × 2 × 1 = 144` research rows.

## Source status map

| Dimension | Status |
|---|---|
| Deep-leg origin | Source-supported semantically; executable candle/price field unresolved |
| First breakout candle as A | Unresolved executable candidate |
| Nearest swing as A | Unresolved executable candidate; not canonical |
| Parent vs nested B | Source-confirmed as distinct structural scales; exact executable selector unresolved |
| Correction reference as C | Source-supported semantically; exact executable anchor unresolved |
| Fill as C | Explicitly rejected as canonical by the accumulated source/visual audit; retained only as a negative-control hypothesis |
| OHLC/body price field | Unresolved |
| Parent vs nested scale selection | Unresolved as an executable selection rule |
| AB=CD relationship | Source-confirmed semantically |
| Executable D calculation | Unresolved because A/B/C fields and tolerance are unresolved |
| AB=CD tolerance | Unresolved |
| TP1/TP2 relationship to D | Unresolved |

## Completeness invariant

The matrix generator must cover every value in each known dimension and every combination across those dimensions. The test suite therefore checks:

1. exactly 144 unique rows are generated;
2. every known A/B/C selector is represented;
3. every known price field is represented;
4. both structural scales are represented;
5. the source-confirmed projection representation is represented;
6. every row remains `canonical: false`;
7. unresolved dimensions remain explicitly unresolved;
8. `FILL_AS_C` remains visible as a negative control and is never promoted;
9. no tolerance or optimization dimension is silently introduced.

## Important boundary

This matrix is **not** a model-selection mechanism. No row is ranked, scored, optimized, or promoted based on historical performance.

The `AB_EQ_CD_TRANSLATION` projection is only a research representation of the source-confirmed equal-leg relationship. It must not be interpreted as the final executable D formula, because the source has not resolved the exact A/B/C price anchors or AB=CD tolerance.

Likewise, the presence of `HIGH`, `LOW`, `OPEN`, `CLOSE`, `BODY_HIGH`, and `BODY_LOW` enumerations does not claim that the source uses any one of them. They are competing research dimensions.

## Gate impact

- SOURCE RESOLUTION: **boundary established**
- SYNTHETIC FIXTURES: **PASS / expanded coverage**
- FROZEN_GEOMETRY: **BLOCKED**
- DEV: **BLOCKED**
- VAL: **PROTECTED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **BLOCKED**

## Next authorized research

Only source-aligned or synthetic discrimination work is authorized from this gate. A suitable next step is to use the complete matrix to construct minimal pair fixtures that isolate one dimension at a time, without ranking the models or using historical profitability to infer source meaning.
