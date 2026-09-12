# G344 — Minimal-Pair Synthetic Discrimination

Date: 2026-09-12

## Gate

**G344 = PASS — MINIMAL-PAIR COVERAGE, SOURCE GEOMETRY STILL UNRESOLVED**

This gate isolates one currently unresolved model dimension at a time. It is a synthetic research gate only and does not freeze executable AB=CD geometry.

## Purpose

G343 enumerated the known model space. G344 converts that inventory into minimal pairs: two otherwise identical research models differing in exactly one model dimension.

The purpose is diagnostic, not classificatory. A numerical difference between two candidates does not establish which candidate matches the source.

## Minimal-pair dimensions

The suite isolates:

1. A selector: `SOURCE_DEEP_ORIGIN` vs `FIRST_BREAKOUT_CANDLE`
2. B selector: `PARENT_B` vs `NESTED_B`
3. C selector: `SOURCE_CORRECTION_REFERENCE` vs `FILL_AS_C`
4. Price field: `LOW` vs `CLOSE`
5. Scale: `PARENT` vs `NESTED`

The projection remains the single source-confirmed research representation `AB_EQ_CD_TRANSLATION`; no alternative projection formula is invented.

## Results / interpretation

Under the existing G341 research evaluator, A, B, C and price-field changes produce different projected D values on the fixed synthetic fixture. This confirms that those dimensions are materially capable of changing the computed research outcome.

The scale-only pair does **not** numerically discriminate because the current evaluator already expresses structural scale through the B selector and does not independently alter the projection calculation for the `scale` field. This is recorded as an implementation limitation, not repaired by inventing scale mathematics.

Therefore G344 does not select a canonical scale rule. The source-supported distinction between parent and nested structures remains intact, while executable scale selection remains unresolved.

## Negative control

`FILL_AS_C` is retained only as an explicit negative control. Its numerical discrimination is useful for demonstrating that replacing the correction reference with the later fill changes the research result, but this does not make fill the source-defined C anchor.

## Guardrails

- All models remain `canonical: false`.
- No historical data is used.
- No optimization or parameter search is used.
- No AB=CD tolerance is introduced.
- No TP1/TP2 mapping is introduced.
- No wick/body rule is selected.
- No result is ranked as the source interpretation.
- The scale limitation is explicitly documented instead of being patched with an invented rule.

## Gate impact

- SOURCE RESOLUTION: **boundary remains established**
- SYNTHETIC FIXTURES: **PASS / minimal-pair discrimination added**
- FROZEN_GEOMETRY: **BLOCKED**
- DEV: **BLOCKED**
- VAL: **PROTECTED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **BLOCKED**

## Authorized next step

If no new authoritative source material is available, the next useful research step is to improve the synthetic discriminator itself without assigning canonical meaning: independently model structural scale as a research dimension only if that behavior can be specified without borrowing an unsupported trading convention. Otherwise retain the current limitation and continue source acquisition.
