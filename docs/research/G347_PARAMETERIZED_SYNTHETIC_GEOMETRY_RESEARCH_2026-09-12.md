# G347 — Parameterized Synthetic Geometry Research

Date: 2026-09-12  
Strategy: SP2L / Strategy A  
Gate: **G347 = PASS — PARAMETERIZED SYNTHETIC GEOMETRY COVERAGE, SOURCE MEANING STILL UNRESOLVED**

## Purpose

G346 established the source-resolution boundary: the preserved authoritative lesson did not provide enough explicit evidence to freeze executable A/B/C/D, wick/body selection, AB=CD tolerance, TP1/TP2 mapping, or P-Gap geometry.

G347 therefore converts those unresolved dimensions into an explicit, parameterized **synthetic research space**. The purpose is discrimination and auditability only. It is not historical optimization and it does not decide which interpretation is canonical.

## Parameterized dimensions

- A selector: `SOURCE_DEEP_ORIGIN`, `FIRST_BREAKOUT_CANDLE`, `NEAREST_SWING`
- B selector: `PARENT_B`, `NESTED_B`
- C selector: `SOURCE_CORRECTION_REFERENCE`, `FILL_AS_C`
- price field: `HIGH`, `LOW`, `OPEN`, `CLOSE`, `BODY_HIGH`, `BODY_LOW`
- structural scale: `PARENT`, `NESTED`
- projection: `AB_EQ_CD_TRANSLATION` as the source-aligned research representation of the already confirmed AB=CD relationship
- tolerance: `null`, `0`, `0.5`, `1` — represented only as unresolved research parameters; no fitted tolerance
- TP mapping: `D`, `D_PLUS_1R`, `D_PLUS_2R`, `UNRESOLVED` — competing hypotheses only; no source mapping asserted
- P-Gap hypothesis: `UNRESOLVED`, `THREE_CANDLE_RANGE_GAP`, `BODY_BOUNDARY_GAP` — explicit hypothesis labels only; these are **not** promoted to the Strategy A definition

## Synthetic design

The fixture contains the previously established semantic sequence and additional candles that permit controlled geometric discrimination. The evaluator reports anchor IDs, selected prices, projected D, and the chosen research parameters.

The synthetic evaluator deliberately uses the same research-only signed translation already used in G341:

`D = C + (B - A)`

This is a representation for comparing candidate interpretations, **not a frozen executable Strategy A formula**. No tolerance is applied to accept/reject a setup, and no target is inferred from the TP labels.

## Required negative controls

- `FILL_AS_C` remains non-canonical and is tested as a negative control.
- Wick/body selection remains unresolved.
- Parent/nested scale remains unresolved even when the semantic distinction is source-supported.
- P-Gap hypotheses remain non-canonical and do not become a generic imbalance rule.
- TP mappings remain hypotheses and are not selected by performance.

## Findings

The parameterized space makes the unresolved geometry explicit and mechanically testable. Anchor selection and price-field changes can materially change projected D on the synthetic fixture. C-versus-fill also produces a distinct projection, reinforcing the existing source-first rejection of treating execution fill as geometric C.

Tolerance, TP mapping, and P-Gap are represented without any historical fitting or canonical assignment. The framework intentionally reports alternatives rather than ranking them.

## Source boundary

Nothing in this synthetic exercise is evidence about what the original lesson meant. Synthetic divergence demonstrates only that the competing interpretations are meaningfully different and therefore must not be silently collapsed into one implementation.

No historical data was used. No optimization was performed. No production signal logic was changed. No frozen geometry was declared.

## Gate decision

**PASS — PARAMETERIZED SYNTHETIC GEOMETRY COVERAGE, SOURCE MEANING STILL UNRESOLVED**

### Still blocked

- FROZEN_GEOMETRY
- DEV
- historical optimization
- VAL execution
- Fresh Holdout
- Production

### Next authorized step

Either obtain genuinely new authoritative source evidence capable of resolving the remaining dimensions, or continue source-constrained synthetic discrimination. Do not promote any candidate to canonical Strategy A geometry merely because it behaves better on synthetic or historical data.
